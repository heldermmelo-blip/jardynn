"""Árvores por L-system (sistema de Lindenmayer): uma gramática estocástica
reescreve uma cadeia de símbolos e uma "tartaruga" 3D lê a cadeia final pra
traçar o esqueleto de galhos, que vira malha com o mesmo motor das demais
espécies (`mesh_utils.tube_mesh` + `foliage.leaf_mesh`).

Símbolos da tartaruga (convenção de Prusinkiewicz & Lindenmayer, *The
Algorithmic Beauty of Plants*):
    F   anda pra frente desenhando um galho (comprimento atual)
    + - gira à esquerda/direita (em torno do eixo "pra cima" do galho)
    & ^ inclina pra baixo/pra cima (em torno do eixo "esquerda")
    u d inclina um passo fixo (25°) pra cima/pra baixo: arqueia o ramo sem depender do ângulo da árvore
    / \\ rola pra um lado/outro (em torno da direção de avanço)
    [ ] empilha/desempilha a posição e a orientação (abre/fecha um ramo)
    !   afina o raio do galho;  '  encurta o comprimento
    L   folhagem (um cacho de folhas) na ponta;  R  roseta de folhas rígidas

Letras maiúsculas como A e B são "brotos", que a gramática reescreve; no fim
os brotos que sobraram viram folhagem. O tropismo (`tropismo`) curva os
galhos em direção a um vetor (pra baixo no salgueiro, pra cima na dracena).

Coordenadas: Z pra cima, como o resto de `gielis.plants`.
"""

import math

import numpy as np

from . import foliage
from .mesh_utils import tube_mesh

ANGULO_DOURADO = 137.5  # graus: ângulo áureo entre ramos sucessivos (filotaxia)
MAX_CADEIA = 1800  # a cadeia para de crescer aqui: a árvore não vira um arquivo de megabytes
MAX_PONTAS = 240  # no máximo este tanto de cachos de folhas por árvore

# Cada gramática: axioma, regras (símbolo -> lista de (peso, cadeia)), o que
# cada broto vira no fim, e os parâmetros da tartaruga e da folhagem.
GRAMATICAS = {
    # Copa larga e arredondada: o tronco segue e solta de 2 a 3 ramos por nó,
    # cada ramo se bifurcando, cada vez menores.
    "carvalho": dict(
        altura=(7.0, 22.0),
        axioma="FA",
        regras={
            "A": [(0.5, "F'!A[&+B][&-B]/[&B]"), (0.5, "F'!A[&B]/[&B]/[&B]")],
            "B": [(0.6, "F'!LB[+B][-B]"), (0.25, "F'!LB[+B]"), (0.15, "F'!L[-B]B")],
        },
        iteracoes=(5, 6),
        fim={"A": "L", "B": "L"},
        angulo=(48.0, 60.0),
        giro=ANGULO_DOURADO,
        comprimento=0.6,
        raio=0.08,
        afina=0.86,
        encurta=0.88,
        tropismo=((0.0, 0.0, 1.0), -0.04),
        folha=dict(comprimento=(0.3, 0.45), por_cacho=(1, 2), largura=0.45, forca=1.6),
    ),
    # Ramos longos que pendem: o tropismo pra baixo vence a gravidade dos galhos.
    "salgueiro": dict(
        altura=(5.0, 14.0),
        axioma="FFFA",
        regras={
            "A": [(0.7, "F'!A[&+B][&-B]/[&B]"), (0.3, "F'!A[&B]/[&B]")],
            "B": [(0.7, "F'!LB[&B]"), (0.3, "F'!LB")],
        },
        iteracoes=(6, 7),
        fim={"A": "L", "B": "LL"},
        angulo=(48.0, 62.0),
        giro=ANGULO_DOURADO,
        comprimento=0.55,
        raio=0.07,
        afina=0.9,
        encurta=0.95,
        tropismo=((0.0, 0.0, -1.0), 0.28),
        folha=dict(comprimento=(0.35, 0.55), por_cacho=(1, 2), largura=0.1, forca=1.1),
    ),
    # Cone de verticilos: a cada nível, um anel de ramos quase horizontais,
    # cada nível menor que o de baixo.
    "pinheiro": dict(
        altura=(8.0, 28.0),
        axioma="FFFA",
        regras={
            "A": [(1.0, "F'![&B]/[&B]/[&B]/[&B]/[&B]FA")],
            "B": [(0.6, "F!FL"), (0.4, "F!F[&-F]L")],
        },
        iteracoes=(9, 11),
        fim={"A": "L"},
        angulo=(72.0, 80.0),
        giro=72.0,
        comprimento=0.35,
        raio=0.05,
        afina=0.95,
        encurta=0.92,
        tropismo=((0.0, 0.0, 1.0), -0.03),
        folha=dict(comprimento=(0.14, 0.24), por_cacho=(6, 8), largura=0.07, forca=1.0),
    ),
    # Araucária: tronco reto, sem galhos embaixo; no alto, verticilos de ramos
    # horizontais cujas pontas arqueiam pra cima, com folhas duras e densas.
    "araucaria": dict(
        altura=(8.0, 30.0),
        axioma="FFFFFA",
        regras={
            "A": [(1.0, "F'![&B]/[&B]/[&B]/[&B]/[&B]FA")],
            "B": [(1.0, "FFuFuFL")],
        },
        iteracoes=(7, 9),
        fim={"A": "L"},
        angulo=(80.0, 88.0),
        giro=72.0,
        comprimento=0.42,
        raio=0.07,
        afina=0.94,
        encurta=0.93,
        tropismo=((0.0, 0.0, 1.0), -0.02),
        folha=dict(comprimento=(0.16, 0.26), por_cacho=(6, 8), largura=0.3, forca=1.0),
    ),
    # Dracena-dragão: tronco grosso que se bifurca sempre em dois, formando
    # uma copa de guarda-chuva com rosetas de folhas rígidas nas pontas.
    "dracena_dragao": dict(
        altura=(2.5, 9.0),
        axioma="FFA",
        regras={"A": [(1.0, "F'![&+A][&-A]")]},
        iteracoes=(4, 5),
        fim={"A": "R"},
        angulo=(32.0, 40.0),
        giro=180.0,
        comprimento=0.5,
        raio=0.12,
        afina=0.8,
        encurta=0.82,
        tropismo=((0.0, 0.0, 1.0), -0.12),
        folha=dict(comprimento=(0.3, 0.45), por_cacho=(9, 12), largura=0.1, forca=1.0),
    ),
}

ESPECIES_L = tuple(GRAMATICAS)


def reescrever(rng, gramatica, iteracoes):
    """Aplica as regras estocásticas `iteracoes` vezes ao axioma e troca os
    brotos que sobraram pelo que `fim` manda. Devolve a cadeia final.

    Em cada passada todos os símbolos são reescritos ao mesmo tempo (os que
    não têm regra passam inalterados); entre as opções de uma regra, a
    escolha é sorteada com os pesos dados. Para antes de `iteracoes` se a
    cadeia já passou de `MAX_CADEIA`."""
    cadeia = gramatica["axioma"]
    regras = gramatica["regras"]
    for _ in range(iteracoes):
        if len(cadeia) > MAX_CADEIA:
            break
        saida = []
        for simbolo in cadeia:
            opcoes = regras.get(simbolo)
            if opcoes is None:
                saida.append(simbolo)
            else:
                saida.append(rng.choices([c for _, c in opcoes], weights=[p for p, _ in opcoes])[0])
        cadeia = "".join(saida)
    return "".join(gramatica["fim"].get(s, s) if s in gramatica["fim"] else s for s in cadeia)


def _rotacionar(eixo, vetor, angulo):
    """Gira `vetor` em torno de `eixo` (unitário) por `angulo` radianos
    (fórmula de Rodrigues; mesma de `mesh_utils.rotate_around_axis`, mas sem
    normalizar o eixo)."""
    c, s = math.cos(angulo), math.sin(angulo)
    return vetor * c + np.cross(eixo, vetor) * s + eixo * np.dot(eixo, vetor) * (1 - c)


def interpretar(rng, cadeia, gramatica):
    """Tartaruga 3D. Devolve `(segmentos, pontas)`: os galhos (dicts com
    `start`, `end`, `r0`, `r1`, `depth`, como o resto do esqueleto) e as pontas
    de folhagem `(posição, direção, tipo)`, com tipo "L" ou "R".

    O ângulo de ramificação é sorteado uma vez por árvore, dentro da faixa
    `angulo` da gramática. O estado da tartaruga é o trio de eixos (H, L, U)
    — avanço, esquerda e cima — mais posição, raio e comprimento atuais; os
    colchetes guardam e restauram esse estado numa pilha. Coordenadas Z-up:
    a tartaruga começa na origem apontando para +Z. As profundidades
    (`depth`) contam quantos `[` estão abertos."""
    angulo = math.radians(rng.uniform(*gramatica["angulo"]))
    giro = math.radians(gramatica["giro"])
    comprimento = gramatica["comprimento"]
    raio = gramatica["raio"]
    afina, encurta = gramatica["afina"], gramatica["encurta"]
    tropismo, forca = gramatica["tropismo"]
    tropismo = np.asarray(tropismo, float)

    pos = np.zeros(3)
    H = np.array([0.0, 0.0, 1.0])  # direção de avanço
    L = np.array([-1.0, 0.0, 0.0])  # esquerda
    U = np.cross(H, L)  # cima do galho
    pilha = []
    segmentos, pontas = [], []
    prof = 0

    for simbolo in cadeia:
        if simbolo == "F":
            fim = pos + H * comprimento
            r1 = raio * afina
            segmentos.append(dict(start=pos.copy(), end=fim.copy(), r0=raio, r1=r1, depth=prof))
            pos = fim
            raio = r1
            if forca:  # tropismo: curva H na direção de `tropismo`
                eixo = np.cross(H, tropismo)
                n = np.linalg.norm(eixo)
                if n > 1e-9:
                    # Quanto mais H é perpendicular ao vetor de tropismo, maior a
                    # curvatura (|H x T| = sen do ângulo); `forca` < 0 afasta.
                    ang = forca * n
                    H = _rotacionar(eixo / n, H, ang)
                    L = _rotacionar(eixo / n, L, ang)
                    # Reortonormaliza H, L, U para o erro numérico não se acumular.
                    H = H / np.linalg.norm(H)
                    U = np.cross(H, L)
                    L = np.cross(U, H)
        elif simbolo in "+-":
            a = angulo if simbolo == "+" else -angulo
            H, L = _rotacionar(U, H, a), _rotacionar(U, L, a)
        elif simbolo in "&^":
            a = angulo if simbolo == "&" else -angulo
            H, U = _rotacionar(L, H, a), _rotacionar(L, U, a)
        elif simbolo in "ud":
            a = math.radians(25.0) * (-1 if simbolo == "u" else 1)
            H, U = _rotacionar(L, H, a), _rotacionar(L, U, a)
        elif simbolo in "/\\":
            a = giro if simbolo == "/" else -giro
            L, U = _rotacionar(H, L, a), _rotacionar(H, U, a)
        elif simbolo == "[":
            pilha.append((pos.copy(), H.copy(), L.copy(), U.copy(), raio, comprimento))
            prof += 1
        elif simbolo == "]":
            pos, H, L, U, raio, comprimento = pilha.pop()
            prof -= 1
        elif simbolo == "!":
            raio *= afina
        elif simbolo == "'":
            comprimento *= encurta
        elif simbolo in "LR":
            pontas.append((pos.copy(), H.copy(), simbolo))
    return segmentos, pontas


def montar_malha(rng, gramatica, segmentos, pontas, escala_folha=1.0):
    """Transforma esqueleto e pontas em partes (vértices, faces). As folhas
    crescem com `escala_folha` (menos que a árvore: folha de carvalho velho
    não é do tamanho de uma porta).

    Cada segmento vira um tubo (`tube_mesh`, seção circular; 8 lados, ou 5 nos
    galhos finos). Cada ponta "R" vira uma roseta de folhas rígidas em leque;
    cada ponta "L" vira um cacho de folhas voltado para a direção do ramo.
    Se há mais pontas que `MAX_PONTAS`, sorteia-se esse tanto delas. Devolve
    uma lista de pares (vértices, faces) em coordenadas mundiais Z-up, sem
    cor."""
    if len(pontas) > MAX_PONTAS:
        pontas = rng.sample(pontas, MAX_PONTAS)
    partes = []
    for seg in segmentos:
        v, f = tube_mesh(seg, n_sides=8 if seg["r0"] > 0.02 else 5, cross_section_n=2.0)  # galho fino, menos lados
        if len(v):
            partes.append((v, f))
    cfg = gramatica["folha"]
    for pos, direcao, tipo in pontas:
        if tipo == "R":  # roseta: folhas rígidas saindo em leque pra cima
            # A tangente -Z com queda grande faz as folhas saírem inclinadas pra cima;
            # o giro divide a volta igualmente entre as `n` folhas.
            n = rng.randint(*cfg["por_cacho"])
            for k in range(n):
                lv, lf = foliage.leaf_mesh(
                    shape_power=cfg["forca"], length=rng.uniform(*cfg["comprimento"]) * escala_folha, width_ratio=cfg["largura"]
                )
                mundo = foliage.place_leaf(
                    lv, pos, np.array([0.0, 0.0, -1.0]), twist=2 * math.pi * k / n + rng.uniform(-0.2, 0.2), droop_deg=rng.uniform(30, 70)
                )
                partes.append((mundo, lf))
        else:
            for k in range(rng.randint(*cfg["por_cacho"])):
                lv, lf = foliage.leaf_mesh(
                    shape_power=rng.uniform(cfg["forca"], cfg["forca"] + 1.2),
                    length=rng.uniform(*cfg["comprimento"]) * escala_folha,
                    width_ratio=cfg["largura"],
                )
                mundo = foliage.place_leaf(lv, pos, direcao, twist=rng.uniform(0, 2 * math.pi), droop_deg=rng.uniform(10, 40))
                partes.append((mundo, lf))
    return partes


def sortear_altura(rng, nome):
    """Altura-alvo (m) de uma árvore da gramática `nome`: triangular entre o
    mínimo (muda) e o máximo (veterana) da espécie, com mais árvores adultas
    do que mudas ou veteranas."""
    lo, hi = GRAMATICAS[nome]["altura"]
    return rng.triangular(lo, hi, lo + 0.4 * (hi - lo))


def gerar_arvore_l(rng, nome, altura=None):
    """Gera uma árvore da gramática `nome` (de `GRAMATICAS`): sorteia o número
    de iterações, reescreve, interpreta e escala o esqueleto até a `altura`
    pedida (padrão: sorteada por `sortear_altura`, de muda a veterana), e monta
    a malha. Devolve `(partes, segmentos)`, a convenção das espécies de
    `gielis.plants.generator`."""
    gramatica = GRAMATICAS[nome]
    cadeia = reescrever(rng, gramatica, rng.randint(*gramatica["iteracoes"]))
    segmentos, pontas = interpretar(rng, cadeia, gramatica)
    altura = altura if altura is not None else sortear_altura(rng, nome)
    # Fator de escala único: leva o ponto mais alto do esqueleto à altura pedida.
    natural = max(max(s["end"][2], s["start"][2]) for s in segmentos)
    k = altura / max(natural, 1e-6)
    for seg in segmentos:
        for chave in ("start", "end"):
            seg[chave] = seg[chave] * k
        seg["r0"] *= k
        seg["r1"] *= k
    pontas = [(pos * k, direcao, tipo) for pos, direcao, tipo in pontas]
    return montar_malha(rng, gramatica, segmentos, pontas, escala_folha=k**0.6), segmentos
