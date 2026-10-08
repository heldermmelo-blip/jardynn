"""Flores de várias famílias, com corola em camadas e cor por flor.

A silhueta de cada anel de pétalas vem da Superfórmula de Gielis (Eq. 5.8),
via `foliage.flower_bloom_mesh`; aqui o anel ganha relevo (a borda sobe, como
numa taça), é girado e empilhado em camadas, cada vez menor e mais fechada
por dentro. Cada parte sai com uma cor (r, g, b em 0..1) — haste e folhas
verdes, corola da paleta da espécie, miolo de outro tom — gravada como cor de
vértice no .obj (`mesh_utils.write_obj`), então cada flor tem as suas.

Espécies: flor (genérica), rosa, dalia, margarida, girassol, tulipa, lavanda,
nenufar e orquidea. Convenção de construção como no resto: Z pra cima.
"""

import math

import numpy as np

from . import foliage
from .mesh_utils import orthonormal_basis, tube_mesh

PALETAS = {
    "flor": [(0.9, 0.35, 0.5), (0.95, 0.8, 0.2), (0.6, 0.4, 0.85), (0.95, 0.5, 0.2), (0.92, 0.92, 0.96), (0.4, 0.6, 0.95)],
    "rosa": [(0.8, 0.1, 0.15), (0.95, 0.55, 0.65), (0.98, 0.85, 0.35), (0.97, 0.95, 0.9), (0.14, 0.04, 0.09), (0.95, 0.5, 0.3)],
    "dalia": [(0.9, 0.4, 0.1), (0.8, 0.15, 0.5), (0.55, 0.2, 0.7), (0.95, 0.75, 0.2), (0.85, 0.15, 0.2)],
    "margarida": [(0.97, 0.97, 0.95), (0.97, 0.8, 0.85), (0.97, 0.9, 0.5)],
    "girassol": [(0.98, 0.75, 0.1), (0.95, 0.55, 0.1), (0.88, 0.32, 0.1)],
    "tulipa": [(0.85, 0.1, 0.15), (0.95, 0.85, 0.2), (0.9, 0.4, 0.6), (0.6, 0.2, 0.7), (0.97, 0.95, 0.9), (0.95, 0.5, 0.1)],
    "lavanda": [(0.55, 0.4, 0.8), (0.45, 0.35, 0.75), (0.7, 0.55, 0.85)],
    "nenufar": [(0.97, 0.85, 0.9), (0.95, 0.6, 0.75), (0.97, 0.97, 0.95)],
    "orquidea": [(0.97, 0.95, 0.97), (0.85, 0.4, 0.7), (0.6, 0.3, 0.8), (0.95, 0.85, 0.3), (0.9, 0.5, 0.55)],
}
ESPECIES_FLORES = tuple(PALETAS)

VERDE_HASTE = (0.2, 0.44, 0.17)
VERDE_FOLHA = (0.18, 0.5, 0.2)
VERDE_PRATA = (0.5, 0.62, 0.5)
MIOLO_AMARELO = (0.95, 0.78, 0.15)
MIOLO_MARROM = (0.28, 0.15, 0.06)


def sortear_cor(rng, especie):
    """Cor da corola de uma flor: um tom da paleta da espécie, com pequena
    variação (nenhuma flor sai igual à outra)."""
    base = rng.choice(PALETAS[especie])
    return tuple(float(min(1.0, max(0.0, c + rng.uniform(-0.05, 0.05)))) for c in base)


def _mistura(cor, alvo, t):
    return tuple(c + (a - c) * t for c, a in zip(cor, alvo))


def mais_claro(cor, t=0.3):
    return _mistura(cor, (1.0, 1.0, 1.0), t)


def mais_escuro(cor, t=0.3):
    return _mistura(cor, (0.0, 0.0, 0.0), t)


def _esfera(centro, raio, achatamento=1.0, n_lat=5, n_lon=10):
    verts = []
    for i in range(n_lat + 1):
        theta = math.pi * i / n_lat
        for j in range(n_lon):
            phi = 2 * math.pi * j / n_lon
            verts.append(
                centro
                + np.array(
                    [raio * math.sin(theta) * math.cos(phi), raio * math.sin(theta) * math.sin(phi), raio * achatamento * math.cos(theta)]
                )
            )
    faces = []
    for i in range(n_lat):
        for j in range(n_lon):
            a, b = i * n_lon + j, i * n_lon + (j + 1) % n_lon
            c, d = (i + 1) * n_lon + (j + 1) % n_lon, (i + 1) * n_lon + j
            faces += [[a, c, b], [a, d, c]]
    return np.array(verts), np.array(faces, dtype=int)


def _orientar(vertices, origem, direcao):
    """Leva vértices locais (com Z como "pra cima da flor") pro espaço, com
    o eixo local Z apontando pra `direcao`, a partir de `origem`."""
    direcao = np.asarray(direcao, float)
    direcao = direcao / np.linalg.norm(direcao)
    u, v = orthonormal_basis(direcao)
    return np.asarray(origem, float) + vertices[:, 0:1] * u + vertices[:, 1:2] * v + vertices[:, 2:3] * direcao


def anel_de_petalas(raio, n_petalas, n1, n2, n3, elevacao, giro=0.0, n_pontos=None):
    """Um anel de pétalas visto de cima, em coordenadas locais: o centro fica
    em z = 0 e a borda sobe até `elevacao` (taça). Devolve (vértices, faces)."""
    # flower_bloom_mesh usa m = 2 * n_petals lóbulos; aqui n_petalas é o número real de pétalas do anel
    n_pontos = n_pontos or max(72, 14 * n_petalas)  # pontos suficientes pra cada pétala ter ponta
    v, f = foliage.flower_bloom_mesh(n_petals=n_petalas / 2.0, radius=raio, n1=n1, n2=n2, n3=n3, n_points=n_pontos)
    v = v.copy()
    r = np.hypot(v[:, 0], v[:, 1])
    topo = max(float(r.max()), 1e-9)
    v[:, 0] *= raio / topo  # `raio` é o raio da ponta das pétalas, qualquer que seja a forma
    v[:, 1] *= raio / topo
    v[:, 2] = elevacao * (r / topo) ** 1.5
    c, s = math.cos(giro), math.sin(giro)
    x, y = v[:, 0].copy(), v[:, 1].copy()
    v[:, 0], v[:, 1] = x * c - y * s, x * s + y * c
    return v, f


def corola(origem, direcao, camadas, cor, miolo=None, miolo_raio=0.0):
    """Corola em camadas. `camadas` é uma lista de dicts com `raio`,
    `petalas`, `n1`, `n2`, `n3`, `elevacao` e `giro`, da de fora pra de
    dentro; cada camada mais funda fica um pouco mais clara. Devolve partes
    coloridas (vértices, faces, cor)."""
    partes = []
    for k, cam in enumerate(camadas):
        v, f = anel_de_petalas(cam["raio"], cam["petalas"], cam["n1"], cam["n2"], cam["n3"], cam["elevacao"], cam.get("giro", 0.0))
        tom = mais_claro(cor, 0.12 * k) if cam.get("claro", True) else mais_escuro(cor, 0.1 * k)
        partes.append((_orientar(v, origem, direcao), f, tom))
    if miolo is not None and miolo_raio > 0:
        ev, ef = _esfera(np.zeros(3), miolo_raio, achatamento=0.6)
        partes.append((_orientar(ev, np.asarray(origem, float) + np.asarray(direcao, float) / np.linalg.norm(direcao) * miolo_raio * 0.3, direcao), ef, miolo))
    return partes


def corola_sem_cor(origem, direcao, camadas):
    """Mesma corola, sem cores (pra quem pinta por grupo, como o lago)."""
    return [(v, f) for v, f, _ in corola(origem, direcao, camadas, (1, 1, 1))]


def _haste(a, b, r0, r1, lados=6):
    seg = dict(start=np.asarray(a, float), end=np.asarray(b, float), r0=r0, r1=r1, depth=0)
    v, f = tube_mesh(seg, n_sides=lados, cross_section_n=2.0)
    return v, f, VERDE_HASTE


def _folha(rng, base, direcao_tangente, comprimento, largura=0.35, forca=2.2, giro=None, queda=None, cor=VERDE_FOLHA):
    lv, lf = foliage.leaf_mesh(shape_power=forca, length=comprimento, width_ratio=largura)
    giro = rng.uniform(0, 2 * math.pi) if giro is None else giro
    queda = rng.uniform(15, 50) if queda is None else queda
    mundo = foliage.place_leaf(lv, np.asarray(base, float), np.asarray(direcao_tangente, float), twist=giro, droop_deg=queda)
    return mundo, lf, cor


def _camadas(n, raio, petalas, n1, n2, n3, elevacao, passo=0.76, giro_passo=None, fecha=0.0):
    """`n` camadas: cada uma com `passo` do raio da anterior, girada meia
    pétala (ou `giro_passo`) e, se `fecha`, com a borda subindo mais."""
    giro_passo = math.pi / petalas if giro_passo is None else giro_passo
    return [
        dict(
            raio=raio * passo**k,
            petalas=petalas,
            n1=n1,
            n2=n2,
            n3=n3,
            elevacao=elevacao * (1.0 + fecha * k),
            giro=k * giro_passo,
        )
        for k in range(n)
    ]


# ------------------------------------------------------------------ espécies
def gerar_flor(rng):
    """Flor genérica: 1 a 3 camadas de pétalas, miolo amarelo, duas folhas na
    haste."""
    altura = rng.uniform(0.35, 0.55)
    haste = _haste([0, 0, 0], [0, 0, altura], 0.012, 0.008)
    cor = sortear_cor(rng, "flor")
    petalas = rng.choice([5, 6, 8, 13])
    camadas = _camadas(
        rng.randint(1, 3), rng.uniform(0.08, 0.16), petalas, rng.uniform(0.35, 0.9), rng.uniform(1.2, 2.2), rng.uniform(1.2, 2.2), 0.02
    )
    partes = [haste] + corola([0, 0, altura], [0, 0, 1], camadas, cor, MIOLO_AMARELO, camadas[0]["raio"] * 0.22)
    for z in (altura * 0.25, altura * 0.5):
        partes.append(_folha(rng, [0, 0, z], [0, 0, 1], rng.uniform(0.08, 0.14), 0.3))
    return partes, [dict(start=np.zeros(3), end=np.array([0.0, 0.0, altura]), r0=0.012, r1=0.008, depth=0)]


def gerar_margarida(rng):
    """Margarida: muitas pétalas estreitas, miolo amarelo, haste fina."""
    altura = rng.uniform(0.3, 0.5)
    haste = _haste([0, 0, 0], [0, 0, altura], 0.008, 0.006)
    cor = sortear_cor(rng, "margarida")
    n = rng.choice([13, 16, 21])
    camadas = _camadas(2, rng.uniform(0.07, 0.1), n, 1.2, 6.0, 6.0, 0.012, passo=0.88, giro_passo=math.pi / n)
    partes = [haste] + corola([0, 0, altura], [0, 0, 1], camadas, cor, MIOLO_AMARELO, camadas[0]["raio"] * 0.3)
    partes.append(_folha(rng, [0, 0, altura * 0.2], [0, 0, 1], 0.1, 0.18, forca=1.4))
    return partes, [dict(start=np.zeros(3), end=np.array([0.0, 0.0, altura]), r0=0.008, r1=0.006, depth=0)]


def gerar_girassol(rng):
    """Girassol: haste alta e grossa, cabeça grande tombada, disco escuro e
    pétalas amarelas em duas voltas, folhas grandes."""
    altura = rng.uniform(0.9, 1.4)
    rumo = rng.uniform(0, 2 * math.pi)
    topo = np.array([0.04 * math.cos(rumo), 0.04 * math.sin(rumo), altura])
    partes = [_haste([0, 0, 0], topo, 0.022, 0.016, lados=7)]
    cor = sortear_cor(rng, "girassol")
    tomba = rng.uniform(0.45, 0.75)
    direcao = [math.cos(rumo) * math.sin(tomba), math.sin(rumo) * math.sin(tomba), math.cos(tomba)]
    camadas = _camadas(2, rng.uniform(0.2, 0.28), 21, 1.0, 4.0, 4.0, 0.03, passo=0.86, giro_passo=math.pi / 21)
    partes += corola(topo, direcao, camadas, cor, MIOLO_MARROM, camadas[0]["raio"] * 0.42)
    for k in range(rng.randint(5, 7)):
        z = altura * (0.15 + 0.7 * k / 6)
        partes.append(_folha(rng, [0, 0, z], [0, 0, 1], rng.uniform(0.22, 0.34), 0.5, forca=0.8, queda=rng.uniform(25, 55)))
    return partes, [dict(start=np.zeros(3), end=topo, r0=0.022, r1=0.016, depth=0)]


def gerar_rosa(rng):
    """Rosa: botão de várias camadas que se fecham no miolo, haste com
    espinhos e folhas compostas de três folíolos."""
    altura = rng.uniform(0.4, 0.6)
    topo = np.array([rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), altura])
    partes = [_haste([0, 0, 0], topo, 0.011, 0.008)]
    cor = sortear_cor(rng, "rosa")
    n = rng.randint(4, 6)
    camadas = _camadas(n, rng.uniform(0.07, 0.1), 5, 0.8, 1.4, 1.4, 0.012, passo=0.8, giro_passo=0.7, fecha=1.2)
    partes += corola(topo, [0, 0, 1], camadas, cor, None)
    for _ in range(rng.randint(6, 10)):  # espinhos
        z = rng.uniform(0.05, altura * 0.9)
        ang = rng.uniform(0, 2 * math.pi)
        base = np.array([0.0, 0.0, z]) + topo * (z / altura) * 0.0
        ponta = base + np.array([0.035 * math.cos(ang), 0.035 * math.sin(ang), -0.01])
        seg = dict(start=base, end=ponta, r0=0.006, r1=0.001, depth=1)
        v, f = tube_mesh(seg, n_sides=4, cross_section_n=2.0)
        if len(v):
            partes.append((v, f, mais_escuro(VERDE_HASTE, 0.2)))
    for z in (altura * 0.3, altura * 0.55, altura * 0.78):  # folha composta: 3 folíolos
        giro = rng.uniform(0, 2 * math.pi)
        for d in (-0.5, 0.0, 0.5):
            partes.append(_folha(rng, [0, 0, z], [0, 0, 1], rng.uniform(0.06, 0.09), 0.4, forca=1.6, giro=giro + d, queda=rng.uniform(20, 40)))
    return partes, [dict(start=np.zeros(3), end=topo, r0=0.011, r1=0.008, depth=0)]


def gerar_dalia(rng):
    """Dália: muitas camadas de pétalas pontudas, apertadas, em tons que
    clareiam pro centro."""
    altura = rng.uniform(0.35, 0.6)
    haste = _haste([0, 0, 0], [0, 0, altura], 0.012, 0.01)
    cor = sortear_cor(rng, "dalia")
    n = rng.randint(6, 8)
    camadas = _camadas(n, rng.uniform(0.12, 0.16), rng.choice([12, 14, 16]), 0.8, 3.5, 3.5, 0.008, passo=0.82, fecha=0.25)
    partes = [haste] + corola([0, 0, altura], [0, 0, 1], camadas, cor, None)
    for z in (altura * 0.3, altura * 0.55):
        partes.append(_folha(rng, [0, 0, z], [0, 0, 1], rng.uniform(0.1, 0.16), 0.4, forca=1.5))
    return partes, [dict(start=np.zeros(3), end=np.array([0.0, 0.0, altura]), r0=0.012, r1=0.01, depth=0)]


def gerar_tulipa(rng):
    """Tulipa: taça fechada de seis pétalas (dois anéis de três) e duas
    folhas longas saindo da base."""
    altura = rng.uniform(0.3, 0.45)
    haste = _haste([0, 0, 0], [0, 0, altura], 0.009, 0.008)
    cor = sortear_cor(rng, "tulipa")
    camadas = [
        dict(raio=0.05, petalas=3, n1=0.5, n2=1.6, n3=1.6, elevacao=0.095, giro=0.0, claro=False),
        dict(raio=0.044, petalas=3, n1=0.5, n2=1.6, n3=1.6, elevacao=0.09, giro=math.pi / 3),
    ]
    partes = [haste] + corola([0, 0, altura], [0, 0, 1], camadas, cor, None)
    for k in range(2):
        partes.append(_folha(rng, [0, 0, 0.01], [0, 0, 1], rng.uniform(0.28, 0.4), 0.14, forca=1.1, giro=k * math.pi + rng.uniform(-0.3, 0.3), queda=rng.uniform(15, 35)))
    return partes, [dict(start=np.zeros(3), end=np.array([0.0, 0.0, altura]), r0=0.009, r1=0.008, depth=0)]


def gerar_lavanda(rng):
    """Touceira de lavanda: de 5 a 9 espigas abertas em leque, cada uma com
    anéis de florzinhas roxas no alto, e folhas finas acinzentadas na base."""
    partes = []
    segmentos = []
    cor = sortear_cor(rng, "lavanda")
    for _ in range(rng.randint(5, 9)):
        inclina = rng.uniform(0.08, 0.3)
        rumo = rng.uniform(0, 2 * math.pi)
        altura = rng.uniform(0.35, 0.55)
        topo = np.array([altura * math.sin(inclina) * math.cos(rumo), altura * math.sin(inclina) * math.sin(rumo), altura * math.cos(inclina)])
        h = _haste([0, 0, 0], topo, 0.006, 0.004, lados=4)
        partes.append(h)
        segmentos.append(dict(start=np.zeros(3), end=topo, r0=0.006, r1=0.004, depth=0))
        eixo = topo / np.linalg.norm(topo)
        u, v = orthonormal_basis(eixo)
        for k in range(rng.randint(7, 10)):
            t = 0.62 + 0.38 * k / 9.0
            centro = topo * t
            for j in range(4):
                a = j * math.pi / 2 + k * 0.7
                pos = centro + (u * math.cos(a) + v * math.sin(a)) * 0.014
                ev, ef = _esfera(pos, 0.014 - 0.0008 * k, achatamento=1.3, n_lat=3, n_lon=6)
                partes.append((ev, ef, mais_claro(cor, rng.uniform(0.0, 0.2))))
    for _ in range(10):
        partes.append(_folha(rng, [0, 0, 0.01], [0, 0, 1], rng.uniform(0.15, 0.26), 0.07, forca=1.0, queda=rng.uniform(25, 60), cor=VERDE_PRATA))
    return partes, segmentos


def gerar_nenufar(rng):
    """Nenúfar: folha redonda e chata, com uma fenda, boiando, e uma flor de
    camadas pálidas no meio (ou só a folha, em um quarto das vezes)."""
    raio = rng.uniform(0.28, 0.42)
    n = 28
    fenda = rng.uniform(0, 2 * math.pi)
    verts = [[0.0, 0.0, 0.02]] + [[raio * math.cos(a), raio * math.sin(a), 0.02] for a in (fenda + 0.18 + (2 * math.pi - 0.36) * k / (n - 1) for k in range(n))]
    faces = [[0, 1 + k, 2 + k] for k in range(n - 1)]
    partes = [(np.array(verts), np.array(faces, dtype=int), VERDE_FOLHA)]
    if rng.random() < 0.75:
        cor = sortear_cor(rng, "nenufar")
        camadas = _camadas(3, rng.uniform(0.1, 0.14), rng.choice([8, 10]), 0.22, 1.4, 1.4, 0.05, passo=0.72, fecha=0.4)
        partes += corola([0, 0, 0.02], [0, 0, 1], camadas, cor, MIOLO_AMARELO, camadas[0]["raio"] * 0.2)
    stub = dict(start=np.zeros(3), end=np.array([0.0, 0.0, 0.02]), r0=0.01, r1=0.01, depth=0)
    return partes, [stub]


def gerar_orquidea(rng):
    """Orquídea: haste que arqueia, com 5 a 9 flores de três sépalas, três
    pétalas e um labelo de outra cor, e folhas largas na base."""
    altura = rng.uniform(0.35, 0.55)
    rumo = rng.uniform(0, 2 * math.pi)
    lado = np.array([math.cos(rumo), math.sin(rumo), 0.0])
    pontos = [np.array([0.0, 0.0, altura * s]) + lado * (altura * 0.35 * s**2) for s in np.linspace(0, 1, 6)]
    partes = []
    for a, b in zip(pontos, pontos[1:]):
        partes.append(_haste(a, b, 0.006, 0.005, lados=5))
    cor = sortear_cor(rng, "orquidea")
    labelo = mais_escuro(_mistura(cor, (0.85, 0.2, 0.55), 0.6), 0.1)
    n = rng.randint(5, 9)
    for k in range(n):
        s = 0.35 + 0.65 * k / max(1, n - 1)
        pos = np.array([0.0, 0.0, altura * s]) + lado * (altura * 0.35 * s**2)
        rumo_flor = rumo + rng.uniform(-0.6, 0.6)
        direcao = [0.75 * math.cos(rumo_flor), 0.75 * math.sin(rumo_flor), 0.45]
        r = 0.05 - 0.018 * (k / max(1, n - 1))
        camadas = [
            dict(raio=r, petalas=3, n1=0.45, n2=1.5, n3=1.5, elevacao=0.012, giro=math.pi / 2),
            dict(raio=r * 0.85, petalas=3, n1=0.45, n2=1.5, n3=1.5, elevacao=0.014, giro=math.pi / 2 + math.pi / 3),
        ]
        partes += corola(pos, direcao, camadas, cor, labelo, r * 0.28)
    for k in range(rng.randint(2, 3)):
        partes.append(_folha(rng, [0, 0, 0.01], [0, 0, 1], rng.uniform(0.2, 0.3), 0.3, forca=1.0, giro=k * 2.1 + rng.uniform(-0.3, 0.3), queda=rng.uniform(30, 55)))
    return partes, [dict(start=np.zeros(3), end=pontos[-1], r0=0.006, r1=0.005, depth=0)]


GERADORES_FLOR = {
    "flor": gerar_flor,
    "margarida": gerar_margarida,
    "girassol": gerar_girassol,
    "rosa": gerar_rosa,
    "dalia": gerar_dalia,
    "tulipa": gerar_tulipa,
    "lavanda": gerar_lavanda,
    "nenufar": gerar_nenufar,
    "orquidea": gerar_orquidea,
}
