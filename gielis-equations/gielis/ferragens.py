"""Ferragens e parapeitos: grades art nouveau, balaustradas e jarros.

Inspirado nas portas de ferro forjado de Ernest Blerot (Bruxelas, c. 1900) —
hastes que sobem em curvas de chicote, gavinhas em espiral, botões e folhas,
sempre simétricas em volta de um eixo — e nos jardins abandonados à italiana:
balaustradas de pedra com jarros, corrimãos rústicos de ripas, tudo coberto de
musgo. Nem toda estrutura é do mesmo "estilo" (`ESTILOS`), e a maioria está em
ruína: balaústres e painéis caem, jarros tombam, trechos de corrimão somem.

Cada função devolve um dict `grupo -> lista de partes (vértices, faces)`, pra
quem monta a estrutura somar nos seus grupos de material (`ferro`, `pedra`,
`madeira`, `musgo`, `jarro`). Coordenadas de construção: Z pra cima.
"""

import math

import numpy as np

from .plants.generator import _uv_sphere
from .plants.mesh_utils import tube_mesh

ESTILOS = ("art_nouveau", "rustico", "classico")
ESTILOS_PESOS = (3, 3, 4)
GRUPOS = ("ferro", "pedra", "madeira", "musgo", "jarro")

RUINA_PERDE_BALAUSTRE = 0.38
RUINA_PERDE_PAINEL = 0.4
RUINA_PERDE_POSTE = 0.18
RUINA_JARRO_TOMBADO = 0.35
RUINA_JARRO_SUMIDO = 0.25


def sortear_estilo(rng):
    return rng.choices(ESTILOS, weights=ESTILOS_PESOS)[0]


def _novo():
    return {g: [] for g in GRUPOS}


def _tubo(grupos, grupo, a, b, r0, r1=None, lados=5):
    seg = dict(start=np.asarray(a, float), end=np.asarray(b, float), r0=r0, r1=r0 if r1 is None else r1, depth=0)
    v, f = tube_mesh(seg, n_sides=lados, cross_section_n=2.0)
    if len(v):
        grupos[grupo].append((v, f))


def _bezier(p0, p1, p2, p3, n=14):
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3


def _espiral(centro, raio, voltas, giro0, sentido, n=12):
    """Gavinha: espiral que fecha de `raio` até perto do centro, no plano do painel."""
    t = np.linspace(0.0, 1.0, n)
    ang = giro0 + sentido * 2 * math.pi * voltas * t
    r = raio * (1.0 - 0.8 * t)
    return np.column_stack([centro[0] + r * np.cos(ang), centro[1] + r * np.sin(ang)])


def _polilinha(grupos, grupo, pontos2d, origem, u, v, raio, lados=4):
    """Desenha uma polilinha (pontos no plano local) como uma fieira de tubos."""
    pts = [origem + u * x + v * y for x, y in pontos2d]
    for a, b in zip(pts, pts[1:]):
        _tubo(grupos, grupo, a, b, raio, lados=lados)


def painel_art_nouveau(rng, origem, u, v, largura, altura, grupo="ferro", ruina=False):
    """Grade art nouveau simétrica no plano (u, v) a partir de `origem` (canto
    inferior esquerdo): um caule central que sobe até um botão, e de 2 a 4 pares de
    hastes em curva de chicote que se abrem pros lados e terminam em gavinha, mais
    folhas. Na ruína, hastes se perdem e o painel fica incompleto. Devolve um dict de grupos."""
    grupos = _novo()
    u = np.asarray(u, float)
    v = np.asarray(v, float)
    origem = np.asarray(origem, float)
    meio = largura / 2.0
    raio = max(0.012, min(largura, altura) * 0.014)

    def perde():
        return ruina and rng.random() < RUINA_PERDE_PAINEL * 0.6

    # moldura fina em volta
    for a, b in (((0, 0), (largura, 0)), ((largura, 0), (largura, altura)), ((largura, altura), (0, altura)), ((0, altura), (0, 0))):
        if not (ruina and rng.random() < 0.15):
            _tubo(grupos, grupo, origem + u * a[0] + v * a[1], origem + u * b[0] + v * b[1], raio * 1.2, lados=4)

    # caule central e botão
    topo = altura * rng.uniform(0.72, 0.85)
    if not perde():
        _polilinha(grupos, grupo, [(meio, altura * 0.04), (meio, topo)], origem, u, v, raio * 1.3)
        botao_centro = origem + u * meio + v * (topo + altura * 0.03)
        bv, bf = _uv_sphere(botao_centro, raio * 3.0, squash=1.4, n_lat=4, n_lon=6)
        grupos[grupo].append((bv, bf))
    # hastes em chicote, espelhadas (o painel é simétrico)
    n_pares = rng.randint(2, 4)
    for k in range(n_pares):
        abre = 0.18 + 0.3 * (k + 1) / n_pares
        alto = altura * rng.uniform(0.45, 0.88)
        for lado in (-1, 1):
            if perde():
                continue
            p0 = np.array([meio, altura * 0.05])
            p1 = np.array([meio + lado * largura * abre * 0.6, altura * rng.uniform(0.15, 0.35)])
            p2 = np.array([meio + lado * largura * abre * 1.15, altura * rng.uniform(0.4, 0.62)])
            p3 = np.array([meio + lado * largura * abre * 0.8, alto])
            curva = _bezier(p0, p1, p2, p3)
            _polilinha(grupos, grupo, curva, origem, u, v, raio)
            gav = _espiral(p3, largura * rng.uniform(0.04, 0.07), rng.uniform(1.0, 1.6), rng.uniform(0, 2 * math.pi), -lado)
            _polilinha(grupos, grupo, gav, origem, u, v, raio * 0.85)
            # folha: um losango pequeno na curva
            f_c = curva[len(curva) // 2]
            fl = np.array([[f_c[0], f_c[1]], [f_c[0] + lado * largura * 0.05, f_c[1] + altura * 0.03], [f_c[0] + lado * largura * 0.1, f_c[1]]])
            pts3 = np.array([origem + u * x + v * y for x, y in fl])
            grupos[grupo].append((pts3, np.array([[0, 1, 2], [0, 2, 1]])))
    return grupos


def grade_simples(rng, origem, u, v, largura, altura, grupo="ferro", ruina=False, madeira=False):
    """Grade de barras verticais com duas travessas — o mais simples (janela de
    porão, portinhola); na ruína, algumas barras faltam."""
    grupos = _novo()
    origem = np.asarray(origem, float)
    u, v = np.asarray(u, float), np.asarray(v, float)
    n = max(3, int(largura / 0.14))
    raio = 0.012
    grp = "madeira" if madeira else grupo
    for k in range(n + 1):
        if ruina and rng.random() < 0.3:
            continue
        x = largura * k / n
        _tubo(grupos, grp, origem + u * x, origem + u * x + v * altura, raio)
    for y in (0.0, altura * 0.5, altura):
        _tubo(grupos, grp, origem + v * y, origem + u * largura + v * y, raio * 1.2)
    return grupos


# ---------------------------------------------------------------------- jarros
def jarro(rng, centro, escala=1.0, tombado=False):
    """Jarro de pedra: pé, bojo largo, gargalo e boca — um vaso de jardim.
    Tombado, fica deitado no chão. Devolve partes `(vértices, faces)`."""
    perfil = [(0.0, 0.16), (0.1, 0.12), (0.28, 0.22), (0.5, 0.26), (0.7, 0.2), (0.85, 0.12), (0.92, 0.14), (1.0, 0.2)]
    s = escala * rng.uniform(0.85, 1.15)
    partes = []
    ang_tomba = rng.uniform(0, 2 * math.pi)
    for (z0, r0), (z1, r1) in zip(perfil, perfil[1:]):
        a = np.array([0.0, 0.0, z0 * 0.8 * s])
        b = np.array([0.0, 0.0, z1 * 0.8 * s])
        seg = dict(start=a, end=b, r0=r0 * s, r1=r1 * s, depth=0)
        v, f = tube_mesh(seg, n_sides=10, cross_section_n=2.0)
        partes.append((v, f))
    if tombado:
        # deita o jarro (gira 80° em torno de um eixo horizontal) e o apoia no chão
        eixo = np.array([math.cos(ang_tomba), math.sin(ang_tomba), 0.0])
        out = []
        for v, f in partes:
            rot = _rotacao(eixo, math.radians(80))
            vv = v @ rot.T
            vv[:, 2] -= vv[:, 2].min() - 0.02
            out.append((vv + np.array([centro[0], centro[1], 0.0]) + np.array([0.0, 0.0, centro[2]]), f))
        return out
    return [(v + np.asarray(centro, float), f) for v, f in partes]


def _rotacao(eixo, ang):
    eixo = eixo / np.linalg.norm(eixo)
    c, s = math.cos(ang), math.sin(ang)
    x, y, z = eixo
    return np.array(
        [
            [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
            [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
        ]
    )


# ------------------------------------------------------------------ parapeito
def parapeito(rng, a, b, z, altura=0.95, estilo="classico", ruina=False, com_jarros=True):
    """Parapeito (balaustrada) do ponto `a` ao `b` (XY) com a base em `z`: no
    estilo `classico`, balaústres de pedra entre dois corrimãos, postes com
    jarros; `rustico`, postes e corrimão de madeira com treliça em X;
    `art_nouveau`, painéis de ferro entre postes de pedra. Com `ruina`,
    balaústres, painéis e postes caem, trechos do corrimão somem, jarros tombam
    ou desaparecem e o musgo cobre a base. Devolve um dict de grupos."""
    grupos = _novo()
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    comp = float(np.linalg.norm(b - a))
    if comp < 0.05:
        return grupos
    u = np.array([*((b - a) / comp), 0.0])
    up = np.array([0.0, 0.0, 1.0])
    base = np.array([a[0], a[1], z])
    material_poste = "madeira" if estilo == "rustico" else "pedra"

    n_postes = max(2, int(round(comp / 2.0)) + 1)
    xs = np.linspace(0.0, comp, n_postes)
    postes_ok = [True] * n_postes
    if ruina:
        for k in range(n_postes):
            if 0 < k < n_postes - 1 and rng.random() < RUINA_PERDE_POSTE:
                postes_ok[k] = False

    # postes e jarros
    for k, x in enumerate(xs):
        if not postes_ok[k]:
            continue
        p = base + u * x
        r = 0.09 if estilo == "rustico" else 0.12
        topo = altura * (1.0 if estilo != "classico" else 1.05)
        if ruina and rng.random() < 0.3:
            topo *= rng.uniform(0.4, 0.85)  # poste quebrado
        _tubo(grupos, material_poste, p, p + up * topo, r, lados=4)
        if com_jarros and estilo != "rustico" and (not ruina or rng.random() > RUINA_JARRO_SUMIDO):
            tombado = ruina and rng.random() < RUINA_JARRO_TOMBADO
            centro = p + up * (topo if not tombado else 0.0)
            if tombado:
                centro = p + u * rng.uniform(-0.4, 0.4) + np.array([rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0.0])
            for v_, f_ in jarro(rng, centro, escala=0.7, tombado=tombado):
                grupos["jarro"].append((v_, f_))

    # corrimãos (inteiros, ou em pedaços na ruína)
    def trecho(x0, x1, y):
        if x1 - x0 < 0.05:
            return
        corr = "madeira" if estilo == "rustico" else ("ferro" if estilo == "art_nouveau" else "pedra")
        r = 0.045 if estilo == "rustico" else 0.06
        _tubo(grupos, corr, base + u * x0 + up * y, base + u * x1 + up * y, r, lados=4)

    for y in (altura, altura * 0.12):
        if not ruina:
            trecho(0.0, comp, y)
        else:
            x = 0.0
            while x < comp:
                comprimento = rng.uniform(0.6, 2.2)
                if rng.random() < 0.7:
                    trecho(x, min(comp, x + comprimento), y)
                x += comprimento + (rng.uniform(0.3, 1.0) if rng.random() < 0.5 else 0.0)

    # enchimento entre os postes
    for k in range(n_postes - 1):
        x0, x1 = xs[k] + 0.12, xs[k + 1] - 0.12
        if x1 - x0 < 0.3:
            continue
        if estilo == "classico":
            n = max(2, int((x1 - x0) / 0.22))
            for j in range(n + 1):
                if ruina and rng.random() < RUINA_PERDE_BALAUSTRE:
                    continue
                x = x0 + (x1 - x0) * j / n
                p = base + u * x
                _tubo(grupos, "pedra", p + up * altura * 0.12, p + up * altura * 0.94, 0.036, 0.036, lados=6)
                bv, bf = _uv_sphere(p + up * altura * 0.38, 0.052, squash=1.2, n_lat=4, n_lon=7)
                grupos["pedra"].append((bv, bf))
        elif estilo == "rustico":
            if ruina and rng.random() < RUINA_PERDE_PAINEL:
                continue
            p0, p1 = base + u * x0, base + u * x1
            for ponta0, ponta1 in ((0.1, 0.92), (0.92, 0.1)):
                if ruina and rng.random() < 0.3:
                    continue
                _tubo(grupos, "madeira", p0 + up * altura * ponta0, p1 + up * altura * ponta1, 0.03, lados=4)
        else:  # art nouveau
            if ruina and rng.random() < RUINA_PERDE_PAINEL:
                continue
            painel = painel_art_nouveau(
                rng, base + u * x0 + up * altura * 0.14, u, up, x1 - x0, altura * 0.78, ruina=ruina
            )
            for grupo, partes in painel.items():
                grupos[grupo] += partes

    # musgo na base (só na ruína): manchas chatas sobre o chão junto do parapeito
    if ruina:
        for _ in range(max(1, int(comp / 1.2))):
            x = rng.uniform(0.0, comp)
            c = base + u * x + np.array([rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), 0.0]) + up * 0.015
            r = rng.uniform(0.18, 0.45)
            ring = [[c[0] + r * math.cos(t), c[1] + r * math.sin(t), c[2]] for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
            pts = np.vstack([ring, [c]])
            grupos["musgo"].append((pts, np.array([[8, i, (i + 1) % 8] for i in range(8)])))
    return grupos


def somar(destino, grupos, mapa=None):
    """Soma os grupos de uma ferragem em `destino` (dict de material -> lista de
    partes). `mapa` renomeia grupos (ex. {"pedra": "tijolo"})."""
    mapa = mapa or {}
    for grupo, partes in grupos.items():
        if partes:
            destino.setdefault(mapa.get(grupo, grupo), []).extend(partes)
    return destino
