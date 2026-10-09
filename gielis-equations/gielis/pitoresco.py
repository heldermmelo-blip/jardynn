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

from . import ferragens
from .plants import exoticas, flowers
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
    """Acumula malhas por grupo (material) e escreve um .obj por grupo.

    `principal` é o grupo cujo .obj leva o próprio caminho de saída (ver
    `group_path`). Todos os métodos de construção recebem o nome do `grupo`
    como primeiro argumento e usam coordenadas mundiais Z-up."""

    def __init__(self, principal):
        self.principal = principal
        self.grupos = {principal: []}

    def add(self, grupo, verts, faces):
        """Acrescenta uma malha (vértices Nx3, faces Mx3) ao `grupo`, criando-o se preciso."""
        self.grupos.setdefault(grupo, []).append((np.asarray(verts, float), np.asarray(faces, int)))

    def box(self, grupo, cx, cy, z0, sx, sy, sz, giro=0.0):
        """Caixa de base `sx` x `sy` centrada em (cx, cy), de z0 a z0 + sz,
        girada `giro` radianos em Z."""
        c, s = math.cos(giro), math.sin(giro)
        verts = []
        # vértices 0-3: quadrado da base; 4-7: o mesmo quadrado no topo (rotação 2D em XY)
        for dz in (0.0, sz):
            for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
                verts.append([cx + dx * c - dy * s, cy + dx * s + dy * c, z0 + dz])
        faces = [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7]]  # base e tampa
        for i in range(4):
            j = (i + 1) % 4
            faces += [[i, j, 4 + j], [i, 4 + j, 4 + i]]
        self.add(grupo, verts, faces)

    def frustum(self, grupo, cx, cy, z0, z1, r0, r1, lados=16, tampa=True):
        """Tronco de cone (ou cilindro) entre as alturas z0 e z1, com raios
        r0 embaixo e r1 em cima; `tampa` fecha o topo."""
        verts = []
        # dois anéis de `lados` vértices: o de baixo (0..lados-1) e o de cima (lados..2*lados-1)
        for z, r in ((z0, r0), (z1, r1)):
            for k in range(lados):
                a = 2 * math.pi * k / lados
                verts.append([cx + r * math.cos(a), cy + r * math.sin(a), z])
        faces = []
        for k in range(lados):
            j = (k + 1) % lados
            faces += [[k, j, lados + j], [k, lados + j, lados + k]]  # faixa lateral
        if tampa:
            verts.append([cx, cy, z1])
            topo = len(verts) - 1
            for k in range(lados):
                faces.append([lados + k, lados + (k + 1) % lados, topo])
        self.add(grupo, verts, faces)

    def disc(self, grupo, cx, cy, z, r, lados=28):
        """Disco plano de raio `r` em `z`, centrado em (cx, cy), de face única
        (leque a partir do centro, vértice 0)."""
        verts = [[cx, cy, z]] + [
            [cx + r * math.cos(2 * math.pi * k / lados), cy + r * math.sin(2 * math.pi * k / lados), z] for k in range(lados)
        ]
        faces = [[0, 1 + k, 1 + (k + 1) % lados] for k in range(lados)]
        self.add(grupo, verts, faces)

    def ball(self, grupo, cx, cy, cz, r, achatamento=1.0, n_lat=6, n_lon=12):
        """Esfera de raio `r` centrada em (cx, cy, cz); `achatamento` escala só o
        eixo Z (< 1 achata, > 1 alonga). Usa `generator._uv_sphere`."""
        v, f = _uv_sphere(np.array([cx, cy, cz], float), r, squash=achatamento, n_lat=n_lat, n_lon=n_lon)
        self.add(grupo, v, f)

    def tube(self, grupo, a, b, r0, r1=None, lados=6):
        """Tubo reto de `a` a `b`, com raio r0 em `a` e r1 em `b` (igual a r0
        se omitido) e seção circular de `lados` lados."""
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
        """Grava um .obj por grupo não vazio (o principal em `out_path`, os
        outros ao lado) e devolve o dict grupo -> caminho gravado."""
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
    """`out_path` se dado; senão `examples/output/<nome>.obj` do projeto."""
    if out_path is not None:
        return out_path
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "output")
    return os.path.join(base, f"{nome}.obj")


# --------------------------------------------------------------------- fonte
def generate_fountain(rng, out_path=None, seca=None, ruina=False, estilo=None):
    """Fonte de três bacias empilhadas, num pedestal. `seca`: sem água
    (padrão: 30% das vezes). Com `ruina`, a fonte fica seca, a bacia de cima
    pode ter caído (50%) e o musgo cobre o fundo e a borda. `estilo` é aceito
    só por uniformidade com os outros geradores (não tem efeito aqui).
    Grupos: `pedra`, `agua`, `musgo`. A info traz `seca` e `quebrada`."""
    seca = (rng.random() < 0.3) if seca is None else seca
    seca = seca or ruina  # fonte em ruína está seca
    p = _Peças("pedra")
    raios = [rng.uniform(1.8, 2.3), rng.uniform(1.05, 1.3), rng.uniform(0.5, 0.65)]
    alturas = [0.0, 0.85, 1.65]
    quebrada = ruina and rng.random() < 0.5  # a bacia de cima caiu
    p.frustum("pedra", 0, 0, 0.0, 0.18, raios[0] * 1.12, raios[0] * 1.12, lados=24)  # soco redondo
    # Cada bacia é: cuba (tronco de cone aberto), borda, fundo, água e uma haste
    # até a bacia de cima. A primeira (z == 0) sobe 0,18 m pelo soco redondo.
    for r, z in zip(raios, alturas):
        if quebrada and z == alturas[-1]:
            continue
        base = z + 0.18 if z == 0 else z
        p.frustum("pedra", 0, 0, base, base + 0.45, r * 0.72, r, lados=24, tampa=False)  # bacia
        p.frustum("pedra", 0, 0, base + 0.45, base + 0.5, r, r, lados=24, tampa=False)  # borda
        p.disc("pedra", 0, 0, base + 0.05, r * 0.72, lados=24)  # fundo
        if not seca:
            p.disc("agua", 0, 0, base + 0.36, r * 0.93, lados=24)
        if z < alturas[-1]:
            p.frustum("pedra", 0, 0, base + 0.05, base + 0.9, 0.2, 0.17)  # haste até a bacia de cima
    if not quebrada:
        p.frustum("pedra", 0, 0, 1.65 + 0.5, 2.3, 0.14, 0.1)
        p.ball("pedra", 0, 0, 2.45, 0.2)
    if ruina:  # musgo no chão da fonte e nas bordas
        p.disc("musgo", 0, 0, 0.2, raios[0] * 0.55, lados=14)
        for _ in range(6):
            a = rng.uniform(0, 2 * math.pi)
            p.disc("musgo", raios[0] * 1.05 * math.cos(a), raios[0] * 1.05 * math.sin(a), 0.2, rng.uniform(0.15, 0.3), lados=7)
    malhas = p.escrever(_caminho_padrao("fonte", out_path) if out_path is None else out_path)
    path = malhas["pedra"]
    return path, {"malhas": malhas, "raio_ocupado": raios[0] * 1.12 + 0.6, "seca": seca, "quebrada": quebrada}


# ------------------------------------------------------------------ estátuas
def _estatua(p, x, y, giro, rng, altura, derrubada=False, sem_cabeca=False):
    """Estátua de mármore (grupo `marmore`) em (x, y) sobre um pedestal
    quadrado de altura `altura`; `giro` (rad, em Z) é a direção para onde ela
    olha. Tem corpo em túnica, cabeça, braços (às vezes um erguido) e um
    nariz. `derrubada`: o corpo jaz no chão ao lado do pedestal (que continua
    de pé), com a cabeça rolada para o lado; `sem_cabeca`: omite a cabeça."""
    p.box("marmore", x, y, 0.0, 0.8, 0.8, altura, giro)
    if derrubada:  # caiu do pedestal e jaz no chão, com a cabeça rolada pro lado
        dx, dy = math.cos(giro + 1.0), math.sin(giro + 1.0)
        base = np.array([x + dx * 0.5, y + dy * 0.5, altura * 0.0 + 0.16])
        p.tube("marmore", base, base + np.array([dx, dy, 0.0]) * 1.2, 0.2, 0.13, lados=8)
        if not sem_cabeca:
            p.ball("marmore", x + dx * 2.0, y + dy * 2.0, 0.14, 0.13, n_lat=5, n_lon=8)
        return
    z = altura
    p.frustum("marmore", x, y, z, z + 1.15, 0.25, 0.15, lados=10)  # corpo de túnica
    if not sem_cabeca:
        p.ball("marmore", x, y, z + 1.3, 0.13, n_lat=5, n_lon=8)  # cabeça
    for lado in (-1, 1):  # braços
        ang = giro + lado * math.pi / 2
        ombro = np.array([x + 0.14 * math.cos(ang), y + 0.14 * math.sin(ang), z + 1.0])
        erguido = rng.random() < 0.3 and lado == 1
        ponta = ombro + (np.array([0.05 * math.cos(ang), 0.05 * math.sin(ang), 0.5]) if erguido else np.array([0.12 * math.cos(ang), 0.12 * math.sin(ang), -0.45]))
        p.tube("marmore", ombro, ponta, 0.04, lados=5)
    nariz = np.array([x + 0.14 * math.cos(giro), y + 0.14 * math.sin(giro), z + 1.3])
    p.tube("marmore", nariz, nariz + np.array([0.07 * math.cos(giro), 0.07 * math.sin(giro), 0.0]), 0.025, 0.005, lados=4)


def generate_statuary(rng, out_path=None, de_costas=None, ruina=False, estilo=None):
    """Terraço quadrado de pedra com estátuas de mármore sobre pedestais, em
    anel. `de_costas`: viradas pra fora (padrão: 35% das vezes). O terraço
    tem um parapeito em três dos quatro lados (o de y negativo, a entrada,
    fica livre), no `estilo` dado (sorteado se None); `ruina` derruba e
    decapita algumas estátuas e espalha musgo."""
    de_costas = (rng.random() < 0.35) if de_costas is None else de_costas
    estilo = estilo or ferragens.sortear_estilo(rng)
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
        _estatua(p, x, y, giro, rng, altura=rng.uniform(0.7, 1.0), derrubada=ruina and rng.random() < 0.3, sem_cabeca=ruina and rng.random() < 0.4)
    p.frustum("pedra", 0, 0, 0.26, 0.7, 0.5, 0.4, lados=8)  # pedestal vazio no centro
    # parapeito em volta do terraço (menos o lado da entrada), no estilo sorteado, com jarros
    cantos = [(-meia, -meia), (meia, -meia), (meia, meia), (-meia, meia)]
    for k in range(4):
        if k == 0:
            continue  # lado da entrada
        a_, b_ = cantos[k], cantos[(k + 1) % 4]
        ferragens.somar(p.grupos, ferragens.parapeito(rng, a_, b_, 0.26, altura=0.95, estilo=estilo, ruina=ruina))
    if ruina:
        for _ in range(10):
            p.disc("musgo", rng.uniform(-meia, meia), rng.uniform(-meia, meia), 0.27, rng.uniform(0.2, 0.55), lados=8)
    malhas = p.escrever(_caminho_padrao("estatuas", out_path) if out_path is None else out_path)
    return malhas["pedra"], {
        "malhas": malhas,
        "raio_ocupado": meia * math.sqrt(2) + 0.6,
        "estatuas": n,
        "de_costas": de_costas,
        "estilo": estilo,
        "ruina": ruina,
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


def generate_hedge_maze(rng, out_path=None, n=None, ruina=False, estilo=None):
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
        """Sebe (caixa) de (x0, y0) a (x1, y1); `esp` a mais no comprimento fecha as quinas."""
        if ruina and rng.random() < 0.13:
            return  # a sebe secou e caiu: um atalho no labirinto
        comprimento = math.hypot(x1 - x0, y1 - y0) + esp
        giro = math.atan2(y1 - y0, x1 - x0)
        p.box("sebe", (x0 + x1) / 2, (y0 + y1) / 2, 0.05, comprimento, esp, alt, giro)

    # Paredes entre células: as horizontais (ao longo de X) em n+1 linhas de grade,
    # depois as verticais (ao longo de Y). Uma parede interna só existe se a
    # passagem entre as duas células vizinhas NÃO está em `abertas`; no contorno,
    # só o vão de entrada (j == 0, coluna `entrada`) fica aberto.
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
    # pedestal com esfera na célula central (ou a logo depois do meio, se n é par)
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
def generate_mausoleum(rng, out_path=None, ruina=False, estilo=None):
    """Mausoléu de mármore: degraus, bloco com porta escura em arco, quatro
    colunas e frontão, com trepadeiras subindo pelas paredes. A frente é o lado
    de y negativo. Na ruína, o frontão e colunas podem ter caído (as colunas
    ficam deitadas diante da porta). Grupos: `marmore`, `porta`, `hera`."""
    p = _Peças("marmore")
    larg, prof = rng.uniform(4.2, 5.0), rng.uniform(3.2, 3.8)
    alt = rng.uniform(2.8, 3.3)
    p.box("marmore", 0, 0, 0.0, larg + 1.6, prof + 2.4, 0.2)
    p.box("marmore", 0, 0, 0.2, larg + 0.8, prof + 1.6, 0.2)
    base = 0.4
    p.box("marmore", 0, 0, base, larg, prof, alt)
    if not ruina or rng.random() < 0.5:  # na ruína, o frontão costuma ter desabado
        p.prisma_triangular("marmore", 0, 0, base + alt, larg + 0.5, prof + 0.5, 1.1)
    frente = -prof / 2  # a frente é o lado de y negativo
    for cx in (-larg / 2 + 0.3, -larg / 6, larg / 6, larg / 2 - 0.3):
        if ruina and rng.random() < 0.3:
            # coluna caída: deitada diante da porta
            p.tube("marmore", [cx, frente - 1.4, 0.2], [cx + rng.uniform(-0.8, 0.8), frente - 2.6, 0.2], 0.2, 0.17, lados=8)
            continue
        p.frustum("marmore", cx, frente - 0.5, base, base + alt, 0.2, 0.17, lados=10)
    p.box("marmore", 0, frente - 0.5, base + alt, larg + 0.3, 0.45, 0.18)
    # porta escura em arco no centro da frente: retângulo + semicírculo em leque,
    # colados 1 cm à frente da parede para não brigar com ela (z-fighting)
    pw, ph = 1.3, 2.2
    p.add("porta", [[-pw / 2, frente - 0.01, base], [pw / 2, frente - 0.01, base], [pw / 2, frente - 0.01, base + ph], [-pw / 2, frente - 0.01, base + ph]], [[0, 1, 2], [0, 2, 3]])
    pts = [[(pw / 2) * math.cos(t), frente - 0.01, base + ph + (pw / 2) * math.sin(t)] for t in np.linspace(0, math.pi, 9)]
    for a, b in zip(pts, pts[1:]):
        p.add("porta", [[0, frente - 0.01, base + ph], a, b], [[0, 1, 2]])
    # trepadeiras nas paredes laterais e no fundo: cada uma é uma cadeia de
    # tubos que sobe com leve desvio lateral, com folhas (esferas achatadas)
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
def generate_pond(rng, out_path=None, gelado=False, ruina=False, estilo=None):
    """Lago circular com pedras na margem e nenúfares (ou uma capa de gelo,
    com `gelado`). O disco de água/gelo fica em z = 0,14, acima das trilhas
    do jardim. Grupos: `agua` ou `gelo`, `pedra`, `folha` (folhas de nenúfar
    e juncos), `flor`."""
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
            # sqrt no sorteio do raio: distribui os pontos uniformemente na área do disco
            a, d = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * (raio - 0.6)
            p.disc("folha", d * math.cos(a), d * math.sin(a), 0.16, rng.uniform(0.22, 0.42), lados=10)
        # de 1 a 3 vitórias-régias, as folhas gigantes de borda erguida, encostadas na água
        for _ in range(rng.randint(1, 3)):
            r_folha = rng.uniform(0.7, 1.1)
            a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.0, max(0.0, raio - r_folha - 0.5))
            for v, f in exoticas.almofada_vitoria(rng, (d * math.cos(a), d * math.sin(a)), r_folha, z=0.17):
                p.add("folha", v, f)
        for _ in range(rng.randint(2, 6)):  # flores de nenúfar sobre a água
            a, d = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * (raio - 1.0)
            camadas = flowers._camadas(3, rng.uniform(0.14, 0.2), rng.choice([8, 10]), 0.22, 1.4, 1.4, 0.07, passo=0.72, fecha=0.4)
            for v, f in flowers.corola_sem_cor([d * math.cos(a), d * math.sin(a), 0.18], [0, 0, 1], camadas):
                p.add("flor", v, f)
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
    """Peça de xadrez estilizada (`tipo`: peao, torre, bispo, cavalo, rainha;
    qualquer outro valor vira o rei) em (x, y), no `grupo` de material, com a
    base no chão (z = 0). Todas as medidas multiplicam `escala`. É montada de
    troncos de cone, esferas e caixas; `rng` não é usado."""
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


def generate_chess_lawn(rng, out_path=None, n=8, cel=1.7, ruina=False, estilo=None):
    """Gramado de xadrez: n x n quadrados de grama alternados com lajes de
    pedra preta, e algumas peças gigantes (mármore branco e obsidiana)
    espalhadas, cada uma com o dobro da altura de uma pessoa."""
    p = _Peças("gramado")
    meia = n * cel / 2.0
    for i in range(n):
        for j in range(n):
            cx, cy = -meia + (i + 0.5) * cel, -meia + (j + 0.5) * cel
            if ruina and rng.random() < 0.1:
                continue  # laje afundada ou levada
            if (i + j) % 2 == 0:
                p.box("gramado", cx, cy, 0.0, cel, cel, 0.05)
            else:
                p.box("pedra_preta", cx, cy, 0.0, cel, cel, 0.12)
                if ruina and rng.random() < 0.3:
                    p.disc("musgo", cx + rng.uniform(-0.3, 0.3), cy + rng.uniform(-0.3, 0.3), 0.13, rng.uniform(0.2, 0.45), lados=8)
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


# ------------------------------------------------------------------ escadaria
def generate_stair_terrace(rng, out_path=None, ruina=False, estilo=None):
    """Escadaria curva, em anfiteatro, que sobe de um gramado redondo até um
    terraço de contenção — degraus de pedra largos, abertos em arco — com um
    muro de arrimo em volta e, no alto, um parapeito (com jarros) no estilo
    sorteado. Na ruína, os degraus afundam, caem pedaços do muro e do parapeito,
    e o musgo cobre tudo (`musgo`)."""
    estilo = estilo or ferragens.sortear_estilo(rng)
    p = _Peças("pedra")
    n = rng.randint(5, 8)
    r0 = rng.uniform(2.6, 3.4)
    larg = rng.uniform(0.62, 0.78)
    alt = rng.uniform(0.2, 0.26)
    arco = math.radians(rng.uniform(190, 230))
    inicio = -arco / 2.0 - math.pi / 2  # abre pro lado de y negativo (a "plateia" olha pro gramado)
    seg = 20
    p.disc("gramado", 0, 0, 0.03, r0, lados=24)
    afundado = lambda: ruina and rng.random() < 0.25
    # Cada degrau é um anel (de raio interno `ri` a externo `ro`) cortado em
    # `seg` fatias angulares, cada uma com o piso (quad) e o espelho (riser);
    # o k-ésimo degrau sobe `alt` a mais que o anterior.
    for k in range(n):
        z_topo = alt * (k + 1) - (alt * rng.uniform(0.3, 0.8) if afundado() else 0.0)
        ri, ro = r0 + larg * k, r0 + larg * (k + 1)
        for j in range(seg):
            if ruina and rng.random() < 0.06:
                continue  # pedaço do degrau que se foi
            a0 = inicio + arco * j / seg
            a1 = inicio + arco * (j + 1) / seg
            quad = [
                [ri * math.cos(a0), ri * math.sin(a0), z_topo], [ro * math.cos(a0), ro * math.sin(a0), z_topo],
                [ro * math.cos(a1), ro * math.sin(a1), z_topo], [ri * math.cos(a1), ri * math.sin(a1), z_topo],
            ]
            p.add("pedra", quad, [[0, 1, 2], [0, 2, 3]])
            riser = [
                [ri * math.cos(a0), ri * math.sin(a0), 0.0], [ri * math.cos(a1), ri * math.sin(a1), 0.0],
                [ri * math.cos(a1), ri * math.sin(a1), z_topo], [ri * math.cos(a0), ri * math.sin(a0), z_topo],
            ]
            p.add("pedra", riser, [[0, 1, 2], [0, 2, 3]])
        if ruina:  # musgo cobrindo o degrau
            for _ in range(rng.randint(2, 5)):
                a = inicio + arco * rng.random()
                rm = (ri + ro) / 2
                p.disc("musgo", rm * math.cos(a), rm * math.sin(a), z_topo + 0.01, rng.uniform(0.18, 0.4), lados=7)
    r_topo = r0 + larg * n
    z_topo = alt * n
    # muro de arrimo e parapeito no alto, ao longo do arco (cordas)
    n_cordas = 8
    for k in range(n_cordas):
        a0 = inicio + arco * k / n_cordas
        a1 = inicio + arco * (k + 1) / n_cordas
        a_xy = (r_topo * math.cos(a0), r_topo * math.sin(a0))
        b_xy = (r_topo * math.cos(a1), r_topo * math.sin(a1))
        if not (ruina and rng.random() < 0.15):
            comprimento = math.hypot(b_xy[0] - a_xy[0], b_xy[1] - a_xy[1])
            giro = math.atan2(b_xy[1] - a_xy[1], b_xy[0] - a_xy[0])
            p.box("pedra", (a_xy[0] + b_xy[0]) / 2, (a_xy[1] + b_xy[1]) / 2, 0.0, comprimento + 0.1, 0.45, z_topo, giro)
        ferragens.somar(p.grupos, ferragens.parapeito(rng, a_xy, b_xy, z_topo, altura=0.95, estilo=estilo, ruina=ruina))
    malhas = p.escrever(_caminho_padrao("escadaria", out_path) if out_path is None else out_path)
    return malhas["pedra"], {
        "malhas": malhas,
        "raio_ocupado": r_topo + 1.2,
        "degraus": n,
        "estilo": estilo,
        "ruina": ruina,
        "porta_angulo": -math.pi / 2,  # a boca do anfiteatro, voltada pro caminho
    }


# ------------------------------------------------------------ casa inclinada
def _parede_com_abertura(p, grupo, a, b, z0, z1, abertura=None):
    """Parede de `a` a `b` (XY) de z0 a z1, com uma abertura retangular
    (t0, t1, zlo, zhi) em fração da largura (ou sem)."""
    a, b = np.asarray(a, float), np.asarray(b, float)

    def pt(t, z):
        """Ponto da parede à fração `t` da largura e à altura `z`."""
        q = a + (b - a) * t
        return [q[0], q[1], z]

    def quad(t0, t1, za, zb):
        """Retalho de parede entre as frações t0..t1 da largura e as alturas
        za..zb; ignora retalhos de tamanho ~0."""
        if t1 - t0 > 1e-6 and zb - za > 1e-6:
            p.add(grupo, [pt(t0, za), pt(t1, za), pt(t1, zb), pt(t0, zb)], [[0, 1, 2], [0, 2, 3]])

    if abertura is None:
        quad(0.0, 1.0, z0, z1)
        return
    # a parede vira 4 retalhos em volta do buraco: esquerda, direita, abaixo e acima dele
    t0, t1, zlo, zhi = abertura
    quad(0.0, t0, z0, z1)
    quad(t1, 1.0, z0, z1)
    quad(t0, t1, z0, zlo)
    quad(t0, t1, zhi, z1)


def generate_leaning_house(rng, out_path=None, ruina=True, estilo=None):
    """Casa de jardim abandonada e torta, de dois andares: paredes de reboco
    com portas e janelas vazias, telhado de telhas (com um rombo), degraus de
    pedra na entrada e uma inclinação de 5 a 12° que afunda um canto no chão —
    como a casinha torta de um jardim em ruínas. `ruina` abre mais rombos nas
    paredes e no telhado e cobre a base de musgo."""
    p = _Peças("reboco")
    w, d = rng.uniform(4.2, 5.2), rng.uniform(3.6, 4.4)
    andar = 3.0
    n_and = 2
    base_xy = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    for k in range(4):
        a, b = base_xy[k], base_xy[(k + 1) % 4]
        for f in range(n_and):
            z0, z1 = f * andar, (f + 1) * andar
            if ruina and f == n_and - 1 and rng.random() < 0.25:
                z1 = z0 + rng.uniform(0.8, 2.2)  # pano de parede de cima desabado
            if k == 0 and f == 0:
                _parede_com_abertura(p, "reboco", a, b, z0, z1, (0.38, 0.62, 0.0, 2.1))  # porta na frente
            else:
                _parede_com_abertura(p, "reboco", a, b, z0, z1, (0.35, 0.65, z0 + 1.0, z0 + 2.1))  # janela vazia
            # moldura de pedra da janela/porta
            if not (k == 0 and f == 0):
                t0, t1 = 0.35, 0.65
                ab = np.array(b) - np.array(a)
                for t in (t0, t1):
                    q = np.array(a) + ab * t
                    p.tube("pedra", [q[0], q[1], z0 + 1.0], [q[0], q[1], z0 + 2.1], 0.05, lados=4)
    # telhado de quatro águas, com rombo: a cumeeira corre ao longo de X (de topo_a
    # a topo_b, ocupando o meio de 40% da largura); as águas dos lados em X têm v2 == v3 e viram
    # triângulos (empenas). Cada água some com 30% de chance na ruína.
    z_beiral = n_and * andar
    cume = z_beiral + rng.uniform(1.8, 2.4)
    beiral = 0.5
    cantos = [(x * (1 + beiral / (w / 2)) if i in (0, 1, 2, 3) else x, y * (1 + beiral / (d / 2))) for i, (x, y) in enumerate(base_xy)]
    topo_a, topo_b = (-w * 0.2, 0.0), (w * 0.2, 0.0)
    faces_telhado = [
        (cantos[0], cantos[1], topo_b, topo_a), (cantos[1], cantos[2], topo_b, topo_b), (cantos[2], cantos[3], topo_a, topo_b), (cantos[3], cantos[0], topo_a, topo_a)
    ]
    for (c0, c1, t_1, t_0) in faces_telhado:
        if ruina and rng.random() < 0.3:
            continue  # água do telhado caída
        v0 = [c0[0], c0[1], z_beiral]
        v1 = [c1[0], c1[1], z_beiral]
        v2 = [t_1[0], t_1[1], cume]
        v3 = [t_0[0], t_0[1], cume]
        p.add("telha", [v0, v1, v2, v3], [[0, 1, 2], [0, 2, 3]])
    # degraus da entrada e musgo na base
    for k in range(3):
        p.box("pedra", 0.0, -d / 2 - 0.3 - k * 0.35, 0.0, 1.6, 0.4, 0.18 * (3 - k))
    if ruina:
        for _ in range(8):
            a = rng.uniform(0, 2 * math.pi)
            p.disc("musgo", (w / 2) * 1.02 * math.cos(a), (d / 2) * 1.02 * math.sin(a), 0.02, rng.uniform(0.25, 0.6), lados=8)
    # inclina a casa toda em torno de um eixo horizontal (rotação de Rodrigues, via
    # `ferragens._rotacao`) e desce tudo até o ponto mais baixo ficar 0,5 m abaixo
    # do chão (z = 0), o que "afunda" o canto mais baixo na terra
    graus = rng.uniform(5.0, 12.0)
    az = rng.uniform(0, 2 * math.pi)
    eixo = np.array([-math.sin(az), math.cos(az), 0.0])
    rot = ferragens._rotacao(eixo, math.radians(graus))
    for grupo, partes in p.grupos.items():
        novas = []
        for v, f in partes:
            novas.append((np.asarray(v, float) @ rot.T, f))
        p.grupos[grupo] = novas
    baixo = min(float(v[:, 2].min()) for partes in p.grupos.values() for v, _ in partes)
    for grupo, partes in p.grupos.items():
        p.grupos[grupo] = [(v + np.array([0.0, 0.0, -baixo - 0.5]), f) for v, f in partes]
    malhas = p.escrever(_caminho_padrao("casa_inclinada", out_path) if out_path is None else out_path)
    # a porta fica no lado de y negativo (frente); depois da inclinação o ângulo só muda um pouco
    return malhas["reboco"], {
        "malhas": malhas,
        "raio_ocupado": math.hypot(w, d) / 2 + 1.0 + (cume + 0.5) * math.sin(math.radians(graus)) + 0.5,  # beiral + o topo que se desloca com a inclinação
        "inclinacao_graus": graus,
        "ruina": ruina,
        "porta_angulo": -math.pi / 2,
    }


# Nome da estrutura -> gerador `generate_*(rng, out_path=None, ...)`, todos
# devolvendo `(out_path, info)`.
GERADORES = {
    "fonte": generate_fountain,
    "estatuas": generate_statuary,
    "labirinto": generate_hedge_maze,
    "mausoleu": generate_mausoleum,
    "lago": generate_pond,
    "lago_gelado": lambda rng, out_path=None, **kw: generate_pond(rng, out_path=out_path, gelado=True, **kw),
    "xadrez": generate_chess_lawn,
    "escadaria": generate_stair_terrace,
    "casa_inclinada": generate_leaning_house,
}
