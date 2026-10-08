"""Estruturas pitorescas de jardim, inspiradas nos locais do livro: fonte de
três bacias, terraço de estátuas, labirinto de sebes, mausoléu coberto de
hera, lago com nenúfares (ou congelado) e gramado de xadrez com peças
gigantes.

Cada função devolve `(out_path, info)`. Como na estufa, a malha sai em peças
separadas, uma por material (`info["malhas"]` mapeia grupo -> .obj; o grupo
principal é o próprio `out_path`, os outros ficam ao lado como
`<nome>_<grupo>.obj`), pra quem consome pintar cada uma de uma cor.
`info["raio_ocupado"]` é o raio do círculo que a estrutura ocupa no chão.

Coordenadas de construção: plano XY no chão, Z pra cima; `write_obj`
remapeia pra Y-up na escrita.
"""

import math
import os

import numpy as np

from .plants.generator import _uv_sphere
from .plants.mesh_utils import tube_mesh, write_obj

UP = np.array([0.0, 0.0, 1.0])


def group_path(base_path, group, principal):
    """Caminho do .obj de um grupo: o grupo `principal` é o próprio
    `base_path`; os outros ficam ao lado."""
    if group == principal:
        return base_path
    root, ext = os.path.splitext(base_path)
    return f"{root}_{group}{ext}"


class _Peças:
    """Acumula malhas por grupo (material) e escreve um .obj por grupo."""

    def __init__(self, principal):
        self.principal = principal
        self.grupos = {principal: []}

    def add(self, grupo, verts, faces):
        self.grupos.setdefault(grupo, []).append((np.asarray(verts, float), np.asarray(faces, int)))

    def box(self, grupo, cx, cy, z0, sx, sy, sz, giro=0.0):
        """Caixa de base `sx` x `sy` centrada em (cx, cy), de z0 a z0 + sz,
        girada `giro` radianos em Z."""
        c, s = math.cos(giro), math.sin(giro)
        verts = []
        for dz in (0.0, sz):
            for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
                verts.append([cx + dx * c - dy * s, cy + dx * s + dy * c, z0 + dz])
        faces = [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7]]
        for i in range(4):
            j = (i + 1) % 4
            faces += [[i, j, 4 + j], [i, 4 + j, 4 + i]]
        self.add(grupo, verts, faces)

    def frustum(self, grupo, cx, cy, z0, z1, r0, r1, lados=16, tampa=True):
        """Tronco de cone (ou cilindro) entre as alturas z0 e z1, com raios
        r0 embaixo e r1 em cima; `tampa` fecha o topo."""
        verts = []
        for z, r in ((z0, r0), (z1, r1)):
            for k in range(lados):
                a = 2 * math.pi * k / lados
                verts.append([cx + r * math.cos(a), cy + r * math.sin(a), z])
        faces = []
        for k in range(lados):
            j = (k + 1) % lados
            faces += [[k, j, lados + j], [k, lados + j, lados + k]]
        if tampa:
            verts.append([cx, cy, z1])
            topo = len(verts) - 1
            for k in range(lados):
                faces.append([lados + k, lados + (k + 1) % lados, topo])
        self.add(grupo, verts, faces)

    def disc(self, grupo, cx, cy, z, r, lados=28):
        verts = [[cx, cy, z]] + [
            [cx + r * math.cos(2 * math.pi * k / lados), cy + r * math.sin(2 * math.pi * k / lados), z] for k in range(lados)
        ]
        faces = [[0, 1 + k, 1 + (k + 1) % lados] for k in range(lados)]
        self.add(grupo, verts, faces)

    def ball(self, grupo, cx, cy, cz, r, achatamento=1.0, n_lat=6, n_lon=12):
        v, f = _uv_sphere(np.array([cx, cy, cz], float), r, squash=achatamento, n_lat=n_lat, n_lon=n_lon)
        self.add(grupo, v, f)

    def tube(self, grupo, a, b, r0, r1=None, lados=6):
        seg = dict(start=np.asarray(a, float), end=np.asarray(b, float), r0=r0, r1=r0 if r1 is None else r1, depth=0)
        v, f = tube_mesh(seg, n_sides=lados, cross_section_n=2.0)
        if len(v):
            self.add(grupo, v, f)

    def prisma_triangular(self, grupo, cx, cy, z0, largura, profundidade, altura):
        """Frontão: prisma de base `largura` (em X), `profundidade` (em Y) e
        cume `altura` acima de z0."""
        x0, x1 = cx - largura / 2, cx + largura / 2
        y0, y1 = cy - profundidade / 2, cy + profundidade / 2
        verts = [
            [x0, y0, z0], [x1, y0, z0], [cx, y0, z0 + altura],
            [x0, y1, z0], [x1, y1, z0], [cx, y1, z0 + altura],
        ]
        faces = [[0, 2, 1], [3, 4, 5], [0, 1, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2], [1, 2, 5], [1, 5, 4]]
        self.add(grupo, verts, faces)

    def escrever(self, out_path):
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        malhas = {}
        for grupo, partes in self.grupos.items():
            if not partes:
                continue
            path = group_path(out_path, grupo, self.principal)
            write_obj(path, partes)
            malhas[grupo] = path
        return malhas


def _caminho_padrao(nome, out_path):
    if out_path is not None:
        return out_path
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "output")
    return os.path.join(base, f"{nome}.obj")


# --------------------------------------------------------------------- fonte
def generate_fountain(rng, out_path=None, seca=None):
    """Fonte de três bacias empilhadas, num pedestal. `seca`: sem água
    (padrão: 30% das vezes)."""
    seca = (rng.random() < 0.3) if seca is None else seca
    p = _Peças("pedra")
    raios = [rng.uniform(1.8, 2.3), rng.uniform(1.05, 1.3), rng.uniform(0.5, 0.65)]
    alturas = [0.0, 0.85, 1.65]
    p.frustum("pedra", 0, 0, 0.0, 0.18, raios[0] * 1.12, raios[0] * 1.12, lados=24)  # soco redondo
    for r, z in zip(raios, alturas):
        base = z + 0.18 if z == 0 else z
        p.frustum("pedra", 0, 0, base, base + 0.45, r * 0.72, r, lados=24, tampa=False)  # bacia
        p.frustum("pedra", 0, 0, base + 0.45, base + 0.5, r, r, lados=24, tampa=False)  # borda
        p.disc("pedra", 0, 0, base + 0.05, r * 0.72, lados=24)  # fundo
        if not seca:
            p.disc("agua", 0, 0, base + 0.36, r * 0.93, lados=24)
        if z < alturas[-1]:
            p.frustum("pedra", 0, 0, base + 0.05, base + 0.9, 0.2, 0.17)  # haste até a bacia de cima
    p.frustum("pedra", 0, 0, 1.65 + 0.5, 2.3, 0.14, 0.1)
    p.ball("pedra", 0, 0, 2.45, 0.2)
    malhas = p.escrever(_caminho_padrao("fonte", out_path) if out_path is None else out_path)
    path = malhas["pedra"]
    return path, {"malhas": malhas, "raio_ocupado": raios[0] * 1.12 + 0.6, "seca": seca}


# ------------------------------------------------------------------ estátuas
def _estatua(p, x, y, giro, rng, altura):
    p.box("marmore", x, y, 0.0, 0.8, 0.8, altura, giro)
    z = altura
    p.frustum("marmore", x, y, z, z + 1.15, 0.25, 0.15, lados=10)  # corpo de túnica
    p.ball("marmore", x, y, z + 1.3, 0.13, n_lat=5, n_lon=8)  # cabeça
    for lado in (-1, 1):  # braços
        ang = giro + lado * math.pi / 2
        ombro = np.array([x + 0.14 * math.cos(ang), y + 0.14 * math.sin(ang), z + 1.0])
        erguido = rng.random() < 0.3 and lado == 1
        ponta = ombro + (np.array([0.05 * math.cos(ang), 0.05 * math.sin(ang), 0.5]) if erguido else np.array([0.12 * math.cos(ang), 0.12 * math.sin(ang), -0.45]))
        p.tube("marmore", ombro, ponta, 0.04, lados=5)
    nariz = np.array([x + 0.14 * math.cos(giro), y + 0.14 * math.sin(giro), z + 1.3])
    p.tube("marmore", nariz, nariz + np.array([0.07 * math.cos(giro), 0.07 * math.sin(giro), 0.0]), 0.025, 0.005, lados=4)


def generate_statuary(rng, out_path=None, de_costas=None):
    """Terraço quadrado de pedra com estátuas de mármore sobre pedestais, em
    anel. `de_costas`: viradas pra fora (padrão: 35% das vezes)."""
    de_costas = (rng.random() < 0.35) if de_costas is None else de_costas
    p = _Peças("pedra")
    meia = rng.uniform(4.2, 5.4)
    p.box("pedra", 0, 0, 0.0, 2 * meia + 0.8, 2 * meia + 0.8, 0.12)
    p.box("pedra", 0, 0, 0.12, 2 * meia, 2 * meia, 0.14)
    n = rng.randint(5, 9)
    anel = meia * 0.68
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.08, 0.08)
        x, y = anel * math.cos(a), anel * math.sin(a)
        giro = a if de_costas else a + math.pi
        _estatua(p, x, y, giro, rng, altura=rng.uniform(0.7, 1.0))
    p.frustum("pedra", 0, 0, 0.26, 0.7, 0.5, 0.4, lados=8)  # pedestal vazio no centro
    malhas = p.escrever(_caminho_padrao("estatuas", out_path) if out_path is None else out_path)
    return malhas["pedra"], {
        "malhas": malhas,
        "raio_ocupado": meia * math.sqrt(2) + 0.6,
        "estatuas": n,
        "de_costas": de_costas,
    }


# ----------------------------------------------------------------- labirinto
def sortear_labirinto(rng, n):
    """Labirinto perfeito n x n (busca em profundidade). Devolve o conjunto de
    passagens abertas entre células vizinhas, como pares ordenados
    `((x, y), (x2, y2))` com a primeira menor."""
    visitadas = {(0, 0)}
    pilha = [(0, 0)]
    abertas = set()
    while pilha:
        x, y = pilha[-1]
        vizinhas = [
            (x + dx, y + dy)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in visitadas
        ]
        if not vizinhas:
            pilha.pop()
            continue
        v = rng.choice(vizinhas)
        visitadas.add(v)
        abertas.add(tuple(sorted(((x, y), v))))
        pilha.append(v)
    return abertas


def generate_hedge_maze(rng, out_path=None, n=None):
    """Labirinto de sebes aparadas: n x n células de 2 m, um vão de entrada no
    lado de y negativo e um pedestal com uma esfera no centro."""
    n = n or rng.randint(6, 9)
    cel, esp, alt = 2.0, 0.55, 2.1
    abertas = sortear_labirinto(rng, n)
    entrada = rng.randrange(n)
    p = _Peças("sebe")
    meia = n * cel / 2.0
    p.box("piso", 0, 0, 0.0, n * cel + 1.0, n * cel + 1.0, 0.05)

    def parede(x0, y0, x1, y1):
        comprimento = math.hypot(x1 - x0, y1 - y0) + esp
        giro = math.atan2(y1 - y0, x1 - x0)
        p.box("sebe", (x0 + x1) / 2, (y0 + y1) / 2, 0.05, comprimento, esp, alt, giro)

    for i in range(n):
        for j in range(n + 1):
            gx, gy = -meia + i * cel, -meia + j * cel
            # parede horizontal entre (i, j-1) e (i, j)
            if j in (0, n):
                aberta = j == 0 and i == entrada
            else:
                aberta = tuple(sorted(((i, j - 1), (i, j)))) in abertas
            if not aberta:
                parede(gx, gy, gx + cel, gy)
    for i in range(n + 1):
        for j in range(n):
            gx, gy = -meia + i * cel, -meia + j * cel
            if i in (0, n):
                aberta = False
            else:
                aberta = tuple(sorted(((i - 1, j), (i, j)))) in abertas
            if not aberta:
                parede(gx, gy, gx, gy + cel)
    cx = -meia + (n // 2 + 0.5) * cel
    cy = -meia + (n // 2 + 0.5) * cel
    p.frustum("pedra", cx, cy, 0.05, 0.9, 0.4, 0.3, lados=8)
    p.ball("pedra", cx, cy, 1.15, 0.28)
    malhas = p.escrever(_caminho_padrao("labirinto", out_path) if out_path is None else out_path)
    return malhas["sebe"], {
        "malhas": malhas,
        "raio_ocupado": (meia + 0.5) * math.sqrt(2) + 0.2,  # inclui o piso, que passa 0,5 m da sebe
        "n": n,
        "entrada": entrada,
        "passagens": len(abertas),
        "porta_angulo": -math.pi / 2,  # vão voltado pra y negativo (no plano de construção)
    }


# ------------------------------------------------------------------ mausoléu
def generate_mausoleum(rng, out_path=None):
    """Mausoléu de mármore: degraus, bloco com porta escura em arco, quatro
    colunas e frontão, com trepadeiras subindo pelas paredes."""
    p = _Peças("marmore")
    larg, prof = rng.uniform(4.2, 5.0), rng.uniform(3.2, 3.8)
    alt = rng.uniform(2.8, 3.3)
    p.box("marmore", 0, 0, 0.0, larg + 1.6, prof + 2.4, 0.2)
    p.box("marmore", 0, 0, 0.2, larg + 0.8, prof + 1.6, 0.2)
    base = 0.4
    p.box("marmore", 0, 0, base, larg, prof, alt)
    p.prisma_triangular("marmore", 0, 0, base + alt, larg + 0.5, prof + 0.5, 1.1)
    frente = -prof / 2  # a frente é o lado de y negativo
    for cx in (-larg / 2 + 0.3, -larg / 6, larg / 6, larg / 2 - 0.3):
        p.frustum("marmore", cx, frente - 0.5, base, base + alt, 0.2, 0.17, lados=10)
    p.box("marmore", 0, frente - 0.5, base + alt, larg + 0.3, 0.45, 0.18)
    # porta escura em arco no centro da frente
    pw, ph = 1.3, 2.2
    p.add("porta", [[-pw / 2, frente - 0.01, base], [pw / 2, frente - 0.01, base], [pw / 2, frente - 0.01, base + ph], [-pw / 2, frente - 0.01, base + ph]], [[0, 1, 2], [0, 2, 3]])
    pts = [[(pw / 2) * math.cos(t), frente - 0.01, base + ph + (pw / 2) * math.sin(t)] for t in np.linspace(0, math.pi, 9)]
    for a, b in zip(pts, pts[1:]):
        p.add("porta", [[0, frente - 0.01, base + ph], a, b], [[0, 1, 2]])
    # trepadeiras nas paredes laterais e no fundo
    for _ in range(rng.randint(10, 16)):
        lado = rng.choice(["esq", "dir", "fundo"])
        t0 = rng.uniform(-0.8, 0.8)
        if lado == "fundo":
            x, y = t0 * larg / 2, prof / 2 + 0.03
        else:
            x, y = (larg / 2 + 0.03) * (1 if lado == "dir" else -1), t0 * prof / 2
        z = base + 0.05
        ponto = np.array([x, y, z])
        for _ in range(rng.randint(3, 6)):
            prox = ponto + np.array([rng.uniform(-0.25, 0.25) if lado == "fundo" else 0.0, rng.uniform(-0.25, 0.25) if lado != "fundo" else 0.0, rng.uniform(0.35, 0.7)])
            p.tube("hera", ponto, prox, 0.025, 0.018, lados=4)
            if rng.random() < 0.7:
                p.ball("hera", prox[0], prox[1], prox[2], 0.07, achatamento=0.5, n_lat=3, n_lon=6)
            ponto = prox
    malhas = p.escrever(_caminho_padrao("mausoleu", out_path) if out_path is None else out_path)
    return malhas["marmore"], {
        "malhas": malhas,
        "raio_ocupado": math.hypot((larg + 1.6) / 2, (prof + 2.4) / 2) + 0.5,
        "porta_angulo": -math.pi / 2,
    }


# ---------------------------------------------------------------------- lago
def generate_pond(rng, out_path=None, gelado=False):
    """Lago circular com pedras na margem e nenúfares (ou uma capa de gelo,
    com `gelado`)."""
    p = _Peças("gelo" if gelado else "agua")
    raio = rng.uniform(4.0, 6.5)
    p.disc("gelo" if gelado else "agua", 0, 0, 0.14, raio, lados=36)  # acima das trilhas, que passam rente ao chão
    n_pedras = rng.randint(14, 22)
    for k in range(n_pedras):
        a = 2 * math.pi * k / n_pedras + rng.uniform(-0.1, 0.1)
        r = raio + rng.uniform(-0.1, 0.25)
        p.ball("pedra", r * math.cos(a), r * math.sin(a), 0.1, rng.uniform(0.28, 0.5), achatamento=0.6, n_lat=4, n_lon=8)
    if not gelado:
        for _ in range(rng.randint(8, 18)):
            a, d = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * (raio - 0.6)
            p.disc("folha", d * math.cos(a), d * math.sin(a), 0.16, rng.uniform(0.22, 0.42), lados=10)
        for _ in range(rng.randint(4, 9)):  # juncos na margem
            a = rng.uniform(0, 2 * math.pi)
            base = np.array([(raio - 0.2) * math.cos(a), (raio - 0.2) * math.sin(a), 0.05])
            p.tube("folha", base, base + np.array([0.0, 0.0, rng.uniform(0.9, 1.5)]), 0.02, 0.012, lados=4)
    malhas = p.escrever(_caminho_padrao("lago", out_path) if out_path is None else out_path)
    return malhas["gelo" if gelado else "agua"], {
        "malhas": malhas,
        "raio_ocupado": raio + 1.0,
        "raio_agua": raio,
        "gelado": gelado,
    }


# --------------------------------------------------------------------- xadrez
def _peca(p, grupo, tipo, x, y, rng, escala=1.0):
    s = escala
    p.frustum(grupo, x, y, 0.0, 0.25 * s, 0.6 * s, 0.55 * s, lados=14)
    if tipo == "peao":
        p.frustum(grupo, x, y, 0.25 * s, 1.5 * s, 0.38 * s, 0.14 * s, lados=14, tampa=False)
        p.ball(grupo, x, y, 1.75 * s, 0.32 * s)
    elif tipo == "torre":
        p.frustum(grupo, x, y, 0.25 * s, 2.2 * s, 0.42 * s, 0.34 * s, lados=12)
        p.frustum(grupo, x, y, 2.2 * s, 2.5 * s, 0.5 * s, 0.5 * s, lados=12)
        for k in range(4):
            a = k * math.pi / 2
            p.box(grupo, x + 0.4 * s * math.cos(a), y + 0.4 * s * math.sin(a), 2.5 * s, 0.22 * s, 0.22 * s, 0.25 * s, a)
    elif tipo == "bispo":
        p.frustum(grupo, x, y, 0.25 * s, 2.0 * s, 0.4 * s, 0.12 * s, lados=14)
        p.ball(grupo, x, y, 2.3 * s, 0.3 * s, achatamento=1.4)
        p.ball(grupo, x, y, 2.75 * s, 0.1 * s)
    elif tipo == "cavalo":
        p.frustum(grupo, x, y, 0.25 * s, 1.5 * s, 0.4 * s, 0.25 * s, lados=12)
        p.box(grupo, x + 0.18 * s, y, 1.45 * s, 0.9 * s, 0.35 * s, 0.4 * s, 0.0)
        p.box(grupo, x + 0.55 * s, y, 1.0 * s, 0.35 * s, 0.3 * s, 0.7 * s, 0.0)
        p.box(grupo, x - 0.02 * s, y, 1.85 * s, 0.1 * s, 0.3 * s, 0.4 * s, 0.0)
    elif tipo == "rainha":
        p.frustum(grupo, x, y, 0.25 * s, 2.5 * s, 0.42 * s, 0.14 * s, lados=14)
        p.frustum(grupo, x, y, 2.5 * s, 2.8 * s, 0.45 * s, 0.3 * s, lados=14)
        for k in range(7):
            a = 2 * math.pi * k / 7
            p.ball(grupo, x + 0.38 * s * math.cos(a), y + 0.38 * s * math.sin(a), 2.95 * s, 0.1 * s, n_lat=3, n_lon=6)
        p.ball(grupo, x, y, 3.1 * s, 0.14 * s)
    else:  # rei
        p.frustum(grupo, x, y, 0.25 * s, 2.5 * s, 0.44 * s, 0.18 * s, lados=14)
        p.frustum(grupo, x, y, 2.5 * s, 2.8 * s, 0.38 * s, 0.3 * s, lados=14)
        p.box(grupo, x, y, 2.8 * s, 0.14 * s, 0.14 * s, 0.7 * s)
        p.box(grupo, x, y, 3.3 * s, 0.5 * s, 0.14 * s, 0.14 * s)


def generate_chess_lawn(rng, out_path=None, n=8, cel=1.7):
    """Gramado de xadrez: n x n quadrados de grama alternados com lajes de
    pedra preta, e algumas peças gigantes (mármore branco e obsidiana)
    espalhadas, cada uma com o dobro da altura de uma pessoa."""
    p = _Peças("gramado")
    meia = n * cel / 2.0
    for i in range(n):
        for j in range(n):
            cx, cy = -meia + (i + 0.5) * cel, -meia + (j + 0.5) * cel
            if (i + j) % 2 == 0:
                p.box("gramado", cx, cy, 0.0, cel, cel, 0.05)
            else:
                p.box("pedra_preta", cx, cy, 0.0, cel, cel, 0.12)
    casas = [(i, j) for i in range(n) for j in range(n)]
    rng.shuffle(casas)
    n_pecas = rng.randint(6, 12)
    tipos = ["peao", "peao", "peao", "torre", "bispo", "cavalo", "rainha", "rei"]
    usadas = []
    for i, j in casas[:n_pecas]:
        cx, cy = -meia + (i + 0.5) * cel, -meia + (j + 0.5) * cel
        branca = rng.random() < 0.5
        tipo = rng.choice(tipos)
        _peca(p, "marmore" if branca else "obsidiana", tipo, cx, cy, rng, escala=rng.uniform(0.7, 0.85))
        usadas.append({"x": round(cx, 2), "y": round(cy, 2), "tipo": tipo, "branca": branca})
    malhas = p.escrever(_caminho_padrao("xadrez", out_path) if out_path is None else out_path)
    return malhas["gramado"], {"malhas": malhas, "raio_ocupado": meia * math.sqrt(2) + 0.5, "pecas": usadas}


GERADORES = {
    "fonte": generate_fountain,
    "estatuas": generate_statuary,
    "labirinto": generate_hedge_maze,
    "mausoleu": generate_mausoleum,
    "lago": generate_pond,
    "lago_gelado": lambda rng, out_path=None: generate_pond(rng, out_path=out_path, gelado=True),
    "xadrez": generate_chess_lawn,
}
