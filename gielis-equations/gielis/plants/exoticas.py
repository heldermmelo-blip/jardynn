"""Plantas e árvores ornamentais exóticas (Lote 1 da pesquisa em
`ynn-generator/PESQUISA_PLANTAS.md`): baobá, samambaia arbórea, cica,
nepentes, vitória-régia e flor-cadáver.

Cada espécie é uma função `gerar_x(rng, altura=None)` que devolve
`(partes, segmentos)`, a convenção das demais espécies de `gielis.plants`:
`partes` é a lista de `(vértices, faces)` — ou `(vértices, faces, cor)` quando a
planta tem cor de vértice (nepentes, vitória-régia e flor-cadáver, que levam
cores próprias como as flores) — e `segmentos` o esqueleto (dicts `start`, `end`,
`r0`, `r1`, `depth`). `altura` (em metros) é a altura-alvo das espécies
arbóreas (baobá, samambaia arbórea, cica) e vale para o **tronco** (o baobá ainda
ganha galhos acima dele); sem ela, cada exemplar sorteia a sua, de muda a
veterana; nas outras espécies é ignorada.

Coordenadas de construção: Z pra cima, base da planta na origem.
"""

import math

import numpy as np

from . import foliage
from .flowers import (
    VERDE_FOLHA,
    VERDE_HASTE,
    _esfera,
    _folha,
    _haste,
    anel_de_petalas,
    corola,
    mais_claro,
    mais_escuro,
    sortear_cor,
    _orientar,
)
from .mesh_utils import tube_mesh

CASCA_BAOBA = (0.5, 0.42, 0.34)
FIBRA_SAMAMBAIA = (0.28, 0.2, 0.13)
VERDE_CICA = (0.12, 0.34, 0.14)
TRONCO_CICA = (0.22, 0.18, 0.12)
JARRO_CORES = [(0.6, 0.15, 0.2), (0.55, 0.75, 0.3), (0.85, 0.5, 0.2), (0.45, 0.2, 0.45)]
ESPATA_FORA = (0.55, 0.45, 0.4)
ESPATA_DENTRO = (0.42, 0.04, 0.1)
ESPADICE = (0.6, 0.4, 0.22)


def _tubo(a, b, r0, r1=None, lados=6, cor=None):
    """Tubo de `a` a `b`; com `cor`, a parte sai colorida (v, f, cor)."""
    seg = dict(start=np.asarray(a, float), end=np.asarray(b, float), r0=r0, r1=r0 if r1 is None else r1, depth=0)
    v, f = tube_mesh(seg, n_sides=lados, cross_section_n=2.0)
    return (v, f) if cor is None else (v, f, cor)


def _segmento(a, b, r0, r1):
    """Segmento do esqueleto (o que `generate_plant` devolve junto da malha)."""
    return dict(start=np.asarray(a, float), end=np.asarray(b, float), r0=r0, r1=r1, depth=0)


def _folhas_do_cacho(rng, base, n, comprimento, largura, cor, elevacao=(30, 70), forca=1.2):
    """Roseta de `n` folhas saindo de `base` em leque pra cima (a tangente pra baixo
    faz o "droop" virar elevação, como no agave). Devolve partes coloridas."""
    partes = []
    for k in range(n):
        lv, lf = foliage.leaf_mesh(shape_power=forca, length=comprimento * rng.uniform(0.8, 1.15), width_ratio=largura)
        mundo = foliage.place_leaf(
            lv, np.asarray(base, float), np.array([0.0, 0.0, -1.0]), twist=2 * math.pi * k / n + rng.uniform(-0.2, 0.2), droop_deg=rng.uniform(*elevacao)
        )
        partes.append((mundo, lf, cor))
    return partes


# ---------------------------------------------------------------------- baobá
def gerar_baoba(rng, altura=None):
    """Baobá: tronco inchado como uma garrafa (mais largo perto da base, fino no alto),
    guardando água, e no topo poucos galhos curtos e finos que parecem raízes no ar,
    com cachos de folhas nas pontas. Altura de 4 a 8 m (ou `altura`)."""
    H = altura if altura is not None else rng.uniform(4.0, 8.0)
    R = H * rng.uniform(0.17, 0.24)

    def raio(t):
        """Raio do tronco na fração `t` (0 a 1) da altura."""
        # bojo: máximo a 28% da altura, afinando pro topo até ~40% do raio
        return R * (0.38 + 0.62 * math.exp(-(((t - 0.28) / 0.38) ** 2)))

    partes, segmentos = [], []
    n = 10
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        a, b = [0.0, 0.0, H * t0], [0.0, 0.0, H * t1]
        partes.append(_tubo(a, b, raio(t0), raio(t1), lados=12))
        segmentos.append(_segmento(a, b, raio(t0), raio(t1)))
    topo = np.array([0.0, 0.0, H])
    for _ in range(rng.randint(6, 10)):
        ang = rng.uniform(0, 2 * math.pi)
        inclina = math.radians(rng.uniform(25, 60))
        direcao = np.array([math.sin(inclina) * math.cos(ang), math.sin(inclina) * math.sin(ang), math.cos(inclina)])
        ponto, r = topo * 1.0, H * 0.035
        for passo in range(rng.randint(2, 3)):
            dobra = np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(-0.1, 0.15)])
            direcao = direcao + dobra
            direcao = direcao / np.linalg.norm(direcao)
            proximo = ponto + direcao * H * rng.uniform(0.12, 0.22)
            partes.append(_tubo(ponto, proximo, r, r * 0.7, lados=6))
            segmentos.append(_segmento(ponto, proximo, r, r * 0.7))
            ponto, r = proximo, r * 0.7
        for k in range(rng.randint(3, 5)):  # cacho digitado de folhas na ponta
            lv, lf = foliage.leaf_mesh(shape_power=1.6, length=H * rng.uniform(0.09, 0.13), width_ratio=0.26)
            partes.append((foliage.place_leaf(lv, ponto, direcao, twist=rng.uniform(0, 6.28), droop_deg=rng.uniform(10, 45)), lf))
    return partes, segmentos


# ------------------------------------------------------------ samambaia arbórea
def gerar_samambaia_arborea(rng, altura=None):
    """Samambaia arbórea: tronco fibroso e escuro, de espessura quase constante e meio
    torto, coroado por 12 a 18 frondes longas que arqueiam em volta de brotos
    enrolados (báculos) no centro. Altura de 1,6 a 4,5 m (ou `altura`)."""
    H = altura if altura is not None else rng.uniform(1.6, 4.5)
    raio = 0.08 + 0.035 * H
    desvio = np.array([rng.uniform(-0.1, 0.1) * H, rng.uniform(-0.1, 0.1) * H])
    partes, segmentos = [], []
    n = 5
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        a = [desvio[0] * t0**2, desvio[1] * t0**2, H * t0]
        b = [desvio[0] * t1**2, desvio[1] * t1**2, H * t1]
        r0, r1 = raio * rng.uniform(0.92, 1.1), raio * rng.uniform(0.92, 1.1)
        partes.append(_tubo(a, b, r0, r1, lados=9, cor=FIBRA_SAMAMBAIA))
        segmentos.append(_segmento(a, b, r0, r1))
    topo = np.array([desvio[0], desvio[1], H])
    n_frondes = rng.randint(16, 22)
    comprimento = (0.7 + 0.2 * H) * rng.uniform(1.2, 1.8)
    for k in range(n_frondes):
        verde = _mistura_verde(rng)
        lv, lf = foliage.leaf_mesh(shape_power=rng.uniform(1.0, 1.5), length=comprimento * rng.uniform(0.8, 1.15), width_ratio=0.26)
        if k % 3 == 0:  # as frondes novas ficam eretas
            mundo = foliage.place_leaf(lv, topo, np.array([0.0, 0.0, -1.0]), twist=2 * math.pi * k / n_frondes, droop_deg=rng.uniform(55, 75))
        else:
            mundo = foliage.place_leaf(lv, topo, np.array([0.0, 0.0, 1.0]), twist=2 * math.pi * k / n_frondes + rng.uniform(-0.2, 0.2), droop_deg=rng.uniform(15, 55))
        partes.append((mundo, lf, verde))
    for _ in range(rng.randint(3, 5)):  # báculos: brotos enrolados
        ang = rng.uniform(0, 2 * math.pi)
        base = topo + np.array([0.06 * math.cos(ang), 0.06 * math.sin(ang), 0.02])
        for t in np.linspace(0.0, 2.2 * math.pi, 9)[1:]:
            r_esp = 0.06 * (1.0 - t / (2.6 * math.pi))
            prox = topo + np.array([0.06 * math.cos(ang) + r_esp * math.cos(ang + t) * 0.3, 0.06 * math.sin(ang) + r_esp * math.sin(ang + t) * 0.3, 0.02 + 0.5 * t * 0.12])
            partes.append(_tubo(base, prox, 0.008, 0.006, lados=4, cor=(0.45, 0.4, 0.2)))
            base = prox
    return partes, segmentos


def _mistura_verde(rng):
    """Um verde de folha com pequena variação (nenhuma fronde sai igual à outra)."""
    return tuple(float(min(1.0, max(0.0, c + rng.uniform(-0.04, 0.04)))) for c in VERDE_FOLHA)


# ------------------------------------------------------------------------ cica
def gerar_cica(rng, altura=None):
    """Cica: tronco curto e grosso, de aspecto escamoso (anéis que alternam de espessura,
    as cicatrizes das folhas velhas), e uma coroa de 14 a 22 folhas rígidas e
    pinadas — um eixo que arqueia com pares de folíolos estreitos em V. Altura de 0,8
    a 3 m (ou `altura`)."""
    H = altura if altura is not None else rng.uniform(0.8, 3.0)
    raio = 0.12 + 0.08 * H
    partes, segmentos = [], []
    n = 9
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        a, b = [0.0, 0.0, H * t0], [0.0, 0.0, H * t1]
        r = raio * (1.12 if k % 2 == 0 else 0.92) * (1.0 - 0.15 * t0)
        partes.append(_tubo(a, b, r, r * 0.97, lados=10, cor=TRONCO_CICA))
        segmentos.append(_segmento(a, b, r, r * 0.97))
    topo = np.array([0.0, 0.0, H])
    n_folhas = rng.randint(14, 22)
    comp = (0.9 + 0.35 * H) * rng.uniform(0.9, 1.15)
    for k in range(n_folhas):
        ang = 2 * math.pi * k / n_folhas + rng.uniform(-0.15, 0.15)
        saida = np.array([math.cos(ang), math.sin(ang), 0.0])
        elev = rng.uniform(0.25, 1.0)  # as do centro são mais eretas
        pontos = [topo + np.array([0.0, 0.0, 0.0])]
        direcao = saida * math.cos(elev) + np.array([0.0, 0.0, math.sin(elev)])
        p = topo * 1.0
        for passo in range(6):
            direcao = direcao + np.array([0.0, 0.0, -0.13])  # o eixo arqueia pra baixo, de leve
            direcao = direcao / np.linalg.norm(direcao)
            p = p + direcao * comp / 6.0
            pontos.append(p.copy())
        for a, b in zip(pontos, pontos[1:]):
            partes.append(_tubo(a, b, 0.012, 0.01, lados=4, cor=VERDE_CICA))
        for j in range(2, 6):  # pares de folíolos ao longo do eixo
            for lado in (-1, 1):
                for sub in range(3):
                    pos = pontos[j - 1] + (pontos[j] - pontos[j - 1]) * (sub / 3.0)
                    tangente = pontos[j] - pontos[j - 1]
                    lv, lf = foliage.leaf_mesh(shape_power=1.1, length=comp * 0.3 * (1.0 - 0.1 * j), width_ratio=0.11, n_points=10)
                    giro = lado * math.pi / 2
                    partes.append((foliage.place_leaf(lv, pos, tangente, twist=giro, droop_deg=-25), lf, VERDE_CICA))
    return partes, segmentos


# --------------------------------------------------------------------- nepentes
def gerar_nepentes(rng, altura=None):
    """Nepentes (planta-jarro): roseta de folhas na base, um caule que arqueia e de 3 a 6
    jarros pendurados em gavinhas finas, cada um com a borda listrada e uma tampa. As
    cores (verde das folhas, o jarro de uma cor sorteada) vão como cor de vértice."""
    H = rng.uniform(0.7, 1.4)
    partes, segmentos = [], []
    partes += _folhas_do_cacho(rng, [0, 0, 0.02], rng.randint(7, 10), rng.uniform(0.3, 0.45), 0.16, VERDE_FOLHA, elevacao=(5, 40))
    rumo = rng.uniform(0, 2 * math.pi)
    lado = np.array([math.cos(rumo), math.sin(rumo), 0.0])
    pts = [np.array([0.0, 0.0, H * s]) + lado * (H * 0.3 * s**2) for s in np.linspace(0, 1, 6)]
    for a, b in zip(pts, pts[1:]):
        partes.append(_tubo(a, b, 0.012, 0.009, lados=5, cor=VERDE_HASTE))
        segmentos.append(_segmento(a, b, 0.012, 0.009))
    cor = rng.choice(JARRO_CORES)
    for k in range(rng.randint(3, 6)):
        s = 0.35 + 0.65 * k / 5.0
        base = np.array([0.0, 0.0, H * s]) + lado * (H * 0.3 * s**2)
        ang = rumo + rng.uniform(-1.2, 1.2)
        fora = np.array([math.cos(ang), math.sin(ang), 0.0])
        ponta = base + fora * rng.uniform(0.08, 0.16) + np.array([0.0, 0.0, -rng.uniform(0.12, 0.25)])
        partes.append(_tubo(base, ponta, 0.004, 0.003, lados=4, cor=VERDE_HASTE))  # a gavinha
        r = rng.uniform(0.055, 0.085)
        centro = ponta + np.array([0.0, 0.0, -r * 1.6])
        v, f = _esfera(centro, r, achatamento=1.7, n_lat=5, n_lon=9)
        partes.append((v, f, cor))  # o jarro
        boca = ponta + np.array([0.0, 0.0, -r * 0.1])
        anel = [boca + np.array([r * 0.95 * math.cos(t), r * 0.95 * math.sin(t), 0.0]) for t in np.linspace(0, 2 * math.pi, 10)]
        for a, b in zip(anel, anel[1:]):
            partes.append(_tubo(a, b, 0.007, 0.007, lados=4, cor=mais_claro(cor, 0.45)))  # a borda listrada
        lv, lf = foliage.leaf_mesh(shape_power=0.6, length=r * 1.7, width_ratio=0.5)
        tampa = foliage.place_leaf(lv, boca + fora * r * 0.6, np.array([0.0, 0.0, 1.0]), twist=ang, droop_deg=rng.uniform(55, 80))
        partes.append((tampa, lf, mais_escuro(cor, 0.25)))
    return partes, segmentos


# ------------------------------------------------------------------ vitória-régia
def almofada_vitoria(rng, centro, raio, z=0.04):
    """Folha de vitória-régia: um disco redondo com uma fenda e a borda levantada, boiando
    em `centro` (x, y) à altura `z`, de `raio` metros. Devolve partes `(vértices, faces)`
    sem cor (quem monta decide o material). Serve também aos lagos (`pitoresco`)."""
    n = 36
    fenda = rng.uniform(0, 2 * math.pi)
    angs = [fenda + 0.14 + (2 * math.pi - 0.28) * k / (n - 1) for k in range(n)]
    cx, cy = centro[0], centro[1]
    interno = raio * 0.9
    disco = [[cx, cy, z]] + [[cx + interno * math.cos(a), cy + interno * math.sin(a), z] for a in angs]
    faces = [[0, 1 + k, 2 + k] for k in range(n - 1)]
    partes = [(np.array(disco), np.array(faces, dtype=int))]
    borda = []
    for a in angs:  # a borda sobe do disco até 14 cm acima
        borda.append([cx + interno * math.cos(a), cy + interno * math.sin(a), z])
        borda.append([cx + raio * math.cos(a), cy + raio * math.sin(a), z + 0.14])
    fb = []
    for k in range(n - 1):
        a0, a1, b0, b1 = 2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 3
        fb += [[a0, a1, b1], [a0, b1, b0]]
    partes.append((np.array(borda), np.array(fb, dtype=int)))
    return partes


def gerar_vitoria_regia(rng, altura=None):
    """Vitória-régia: a folha gigante de 0,9 a 1,5 m de raio, redonda, de borda erguida,
    com as nervuras radiais avermelhadas por baixo, e (em 3 de cada 4 exemplares) uma flor
    grande de pétalas em camadas, branca ou rosada, ao lado. Tem cor de vértice."""
    raio = rng.uniform(0.9, 1.5)
    partes = [(v, f, mais_claro(VERDE_FOLHA, 0.0)) for v, f in almofada_vitoria(rng, (0.0, 0.0), raio)]
    for k in range(rng.randint(14, 22)):  # nervuras por baixo
        a = 2 * math.pi * k / 20
        partes.append(_tubo([0, 0, 0.045], [raio * 0.9 * math.cos(a), raio * 0.9 * math.sin(a), 0.055], 0.012, 0.006, lados=4, cor=(0.5, 0.12, 0.16)))
    if rng.random() < 0.75:
        cor = sortear_cor(rng, "nenufar")
        camadas = [dict(raio=0.34 * (0.78**k), petalas=14, n1=0.7, n2=2.0, n3=2.0, elevacao=0.06 + 0.05 * k, giro=k * 0.22) for k in range(3)]
        pos = [raio * 0.3, raio * 0.2, 0.06]
        partes += corola(pos, [0, 0, 1], camadas, cor, (0.95, 0.8, 0.2), 0.05)
    segmentos = [_segmento([0, 0, 0], [0, 0, 0.1], 0.02, 0.02)]
    return partes, segmentos


# ------------------------------------------------------------------- flor-cadáver
def gerar_flor_cadaver(rng, altura=None):
    """Flor-cadáver (*Amorphophallus titanum*): ou a inflorescência — um espádice alto e
    pontudo saindo de uma espata em forma de sino, de babados vinho por dentro — ou, na
    outra metade das vezes, a folha única, um guarda-chuva de folíolos sobre um caule
    malhado. Altura de 1,8 a 3,2 m (ou `altura`). Tem cor de vértice."""
    H = altura if altura is not None else rng.uniform(1.8, 3.2)
    caule_cor = (0.62, 0.66, 0.44)
    if rng.random() < 0.5:  # estágio da folha
        topo = np.array([0.0, 0.0, H * 0.7])
        partes = [_tubo([0, 0, 0], topo, 0.09 * H**0.5, 0.06 * H**0.5, lados=8, cor=caule_cor)]
        n = rng.randint(14, 18)
        for k in range(n):
            lv, lf = foliage.leaf_mesh(shape_power=0.9, length=H * rng.uniform(0.38, 0.5), width_ratio=0.24)
            mundo = foliage.place_leaf(lv, topo, np.array([0.0, 0.0, 1.0]), twist=2 * math.pi * k / n, droop_deg=rng.uniform(15, 40))
            partes.append((mundo, lf, _mistura_verde(rng)))
        return partes, [_segmento([0, 0, 0], topo, 0.09, 0.06)]
    # estágio da flor: espata em sino + espádice
    base_z = H * 0.28
    r_boca = H * rng.uniform(0.17, 0.23)
    partes = [_tubo([0, 0, 0], [0, 0, base_z], 0.1 * H**0.5, 0.07 * H**0.5, lados=8, cor=caule_cor)]
    lados = 18
    for fora, (r0, r1, cor) in enumerate(((0.0, 1.0, ESPATA_FORA), (-0.02, 0.97, ESPATA_DENTRO))):
        verts, faces = [], []
        for anel_k, (t, r) in enumerate(((0.0, 0.05 * H), (1.0, r_boca))):
            for j in range(lados):
                a = 2 * math.pi * j / lados
                rr = (r + r0 * H) * (1.0 if anel_k == 0 else r1)
                verts.append([rr * math.cos(a), rr * math.sin(a), base_z + t * H * 0.3])
        for j in range(lados):
            k = (j + 1) % lados
            faces += [[j, k, lados + k], [j, lados + k, lados + j]]
        partes.append((np.array(verts), np.array(faces, dtype=int), cor))
    babado, bf = anel_de_petalas(r_boca * 1.12, rng.choice([12, 14, 16]), 0.9, 2.4, 2.4, 0.08 * H)
    partes.append((_orientar(babado, [0, 0, base_z + H * 0.3], [0, 0, 1]), bf, ESPATA_DENTRO))
    topo = np.array([0.0, 0.0, H])
    partes.append(_tubo([0, 0, base_z], topo, 0.05 * H, 0.012 * H, lados=8, cor=ESPADICE))  # o espádice
    v, f = _esfera(topo, 0.014 * H, achatamento=1.6, n_lat=4, n_lon=6)
    partes.append((v, f, mais_escuro(ESPADICE, 0.3)))
    return partes, [_segmento([0, 0, 0], topo, 0.05 * H, 0.012 * H)]


EXOTICAS = {
    "baoba": gerar_baoba,
    "samambaia_arborea": gerar_samambaia_arborea,
    "cica": gerar_cica,
    "nepentes": gerar_nepentes,
    "vitoria_regia": gerar_vitoria_regia,
    "flor_cadaver": gerar_flor_cadaver,
}
ESPECIES_EXOTICAS = tuple(EXOTICAS)
# as que são árvores (aceitam `altura` e crescem de muda a veterana)
ARVORES_EXOTICAS = ("baoba", "samambaia_arborea", "cica")
