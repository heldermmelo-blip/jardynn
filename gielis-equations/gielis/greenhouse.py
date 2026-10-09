"""Estufas de ferro e vidro: moldura, painéis de vidro, soco, entrada em arco,
vários pavimentos, cúpulas em camadas, abóbadas, telhados de duas águas e
muitas alas — de uma estufinha minúscula a um conjunto imenso.

Cada estufa é um conjunto de blocos: um **núcleo** (polígono regular com
cúpula em camadas — tambor, cúpula superior e pináculo —, ou um salão
retangular) e **alas** (salões retangulares de um pavimento, que podem sair
das paredes do núcleo ou de outras alas). Tudo sai em peças separadas, uma
por material: moldura, vidro, soco, piso em xadrez (preto e branco) e
trepadeiras mortas (estufa em ruínas, onde faltam painéis e peças).

Coordenadas de construção: plano XY no chão, Z pra cima; `write_obj`
remapeia pra Y-up na escrita.
"""

import math
import os

import numpy as np

from .plants.mesh_utils import tube_mesh, write_obj

STORY = 2.6
PLINTH = 0.9
BAY = 1.25
DOOR_HEIGHT = 2.5
GROUPS = ("moldura", "vidro", "soco", "piso_preto", "piso_branco", "morto")
UP = np.array([0.0, 0.0, 1.0])


def group_path(base_path, group):
    """Caminho do .obj de um grupo: a moldura é o próprio `base_path`, os
    outros ficam ao lado (`<nome>_vidro.obj` etc.)."""
    if group == "moldura":
        return base_path
    root, ext = os.path.splitext(base_path)
    return f"{root}_{group}{ext}"


def _v(xy, z):
    """Ponto 3D (Z-up) a partir de um ponto XY e uma altura `z`."""
    return np.array([xy[0], xy[1], z], dtype=float)


def _convex_overlap(p, q):
    """Teste de eixos separadores entre dois polígonos convexos (listas de XY).
    Devolve True se se sobrepõem; polígonos que só se tocam na borda (dentro de
    uma tolerância de 1e-9) contam como separados."""
    for poly in (p, q):
        n = len(poly)
        for i in range(n):
            a, b = np.asarray(poly[i], float), np.asarray(poly[(i + 1) % n], float)
            # eixo = normal da aresta; se as projeções dos dois polígonos nele
            # não se cruzam, existe um eixo separador e eles não se sobrepõem
            axis = np.array([-(b - a)[1], (b - a)[0]])
            norm = np.linalg.norm(axis)
            if norm < 1e-9:
                continue
            axis /= norm
            pa = [float(np.dot(axis, np.asarray(v, float))) for v in p]
            pb = [float(np.dot(axis, np.asarray(v, float))) for v in q]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return False
    return True


def _inside(point, poly):
    """Ponto dentro de polígono (raio horizontal)."""
    x, y = point
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            inside = not inside
    return inside


class _Builder:
    """Acumula a geometria da estufa em grupos de material (`GROUPS`).

    `parts[grupo]` é a lista de partes (vértices, faces) já em coordenadas
    mundiais Z-up. `pane_loss` e `rib_loss` são as probabilidades (0 a 1) de
    cada painel de vidro / cada viga "descartável" ser omitido (estufa em
    ruínas). `bay` é a largura-alvo de um vão de parede; `door_h` a altura
    da porta (no mínimo `DOOR_HEIGHT`, e proporcional ao vão). `hang_points`
    junta pontos de onde as trepadeiras mortas podem pender."""

    def __init__(self, rng, pane_loss=0.0, rib_loss=0.0, bay=BAY):
        self.rng = rng
        self.bay = bay
        self.door_h = max(DOOR_HEIGHT, 1.2 * bay)
        self.pane_loss = pane_loss
        self.rib_loss = rib_loss
        self.parts = {g: [] for g in GROUPS}
        self.hang_points = []

    def beam(self, a, b, radius=0.04, group="moldura", droppable=True, sides=4):
        """Viga (tubo reto de `a` a `b`, seção de `sides` lados) no `group`.
        Se `droppable`, pode ser omitida com probabilidade `rib_loss`; vigas
        estruturais passam `droppable=False`. Vigas de comprimento ~0 são ignoradas."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        if np.linalg.norm(b - a) < 1e-6:
            return
        if droppable and self.rib_loss and self.rng.random() < self.rib_loss:
            return
        segment = dict(start=a, end=b, r0=radius, r1=radius, depth=0)
        self.parts[group].append(tube_mesh(segment, n_sides=sides, cross_section_n=2.0))

    def panel(self, v0, v1, v2, v3, group="vidro", droppable=True):
        """Painel quadrilátero (v0..v3 em ordem em volta do contorno) no `group`.
        Se v2 e v3 (ou v0 e v1) coincidem (o painel vira triângulo, como no
        ápice da cúpula), emite só um triângulo.
        Só o vidro "descartável" pode ser omitido, com probabilidade `pane_loss`."""
        if group == "vidro" and droppable and self.pane_loss and self.rng.random() < self.pane_loss:
            return
        verts = np.array([v0, v1, v2, v3], float)
        if np.allclose(v2, v3):
            faces = np.array([[0, 1, 2]])
        elif np.allclose(v0, v1):
            faces = np.array([[0, 2, 3]])
        else:
            faces = np.array([[0, 1, 2], [0, 2, 3]])
        self.parts[group].append((verts, faces))

    def triangle(self, a, b, c, group="vidro"):
        """Painel triangular (empena, leque do arco etc.); no vidro, sujeito a `pane_loss`."""
        if group == "vidro" and self.pane_loss and self.rng.random() < self.pane_loss:
            return
        self.parts[group].append((np.array([a, b, c], float), np.array([[0, 1, 2]])))

    # --- entrada em arco --------------------------------------------------
    def arch(self, left, right, steps=8):
        """Arco de meia-circunferência (viga + vidro) entre os pontos `left` e
        `right` (3D, à mesma altura), subindo em Z a partir da linha que os une;
        o vão sob a linha fica livre para a passagem. `steps` é o número de trechos."""
        center = (left + right) / 2.0
        half = (left - right) / 2.0
        w = float(np.linalg.norm(left - right)) / 2.0
        # t vai de 0 (em `left`) a pi (em `right`); sen(t) dá a altura do arco
        pts = [center + half * math.cos(t) + UP * w * math.sin(t) for t in np.linspace(0, math.pi, steps + 1)]
        for p, q in zip(pts, pts[1:]):
            self.beam(p, q, 0.035, droppable=False)
            self.triangle(center, p, q)
        self.beam(center, center + UP * w, 0.02)

    # --- parede reta ------------------------------------------------------
    def wall(self, a, b, floors, openings=(), door_t=None):
        """Parede de `a` a `b` (XY). `openings`: faixas (t0, t1) sem painéis
        (onde uma ala se liga). `door_t`: posição (0 a 1) de uma porta em arco."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        length = float(np.linalg.norm(b - a))
        nb = max(1, int(round(length / self.bay)))
        z_top = floors * STORY

        def pt(t, z):
            """Ponto da parede na posição t (0 em `a`, 1 em `b`) e altura z."""
            return _v(a + (b - a) * t, z)

        def opened(t_mid):
            """True se a posição t cai numa abertura (onde não há painéis)."""
            return any(lo <= t_mid <= hi for lo, hi in openings)

        # A parede é dividida em `nb` vãos de ~`bay`; cada vão tem soco embaixo
        # (exceto na porta) e, por pavimento, um painel de vidro com travessa.
        door_bay = None if door_t is None else min(nb - 1, int(door_t * nb))
        for i in range(nb):
            t0, t1 = i / nb, (i + 1) / nb
            if opened((t0 + t1) / 2):
                continue
            is_door = door_bay == i
            if not is_door:
                self.panel(pt(t0, 0), pt(t1, 0), pt(t1, PLINTH), pt(t0, PLINTH), "soco", droppable=False)
            for f in range(floors):
                z0 = PLINTH if f == 0 else f * STORY
                z1 = (f + 1) * STORY
                if is_door and f == 0:
                    # acima da porta: vidro de `top` até o fim do pavimento, com o arco
                    # por baixo (`top` fica meio vão acima de `door_h`, a altura do arco)
                    top = self.door_h + length / nb / 2
                    self.panel(pt(t0, top), pt(t1, top), pt(t1, z1), pt(t0, z1))
                    self.arch(pt(t0, self.door_h), pt(t1, self.door_h))
                else:
                    self.panel(pt(t0, z0), pt(t1, z0), pt(t1, z1), pt(t0, z1))
                    zm = (z0 + z1) / 2
                    self.beam(pt(t0, zm), pt(t1, zm), 0.02)

        # montantes verticais em cada divisa de vão (os dos cantos, mais grossos,
        # nunca caem na ruína), vigas de pavimento e a viga do soco
        for i in range(nb + 1):
            t = i / nb
            corner = i in (0, nb)
            if not corner and opened(t):
                continue
            self.beam(pt(t, 0), pt(t, z_top), 0.06 if corner else 0.04, droppable=not corner)
        for f in range(1, floors + 1):
            self.beam(pt(0, f * STORY), pt(1, f * STORY), 0.06, droppable=False)
            self.hang_points.append(pt(0.5, f * STORY))
        self.beam(pt(0, PLINTH), pt(1, PLINTH), 0.05)

    # --- galeria (balcão externo) ----------------------------------------
    def gallery(self, corners, floors):
        """Balcão externo em cada pavimento acima do térreo, com guarda-corpo.
        `corners` é o polígono da base do núcleo; o balcão avança 0,55 m para
        fora de cada canto, radialmente a partir do centroide."""
        n = len(corners)
        centroid = np.mean(corners, axis=0)
        for f in range(1, floors):
            z = f * STORY
            outer = []
            for c in corners:
                d = np.asarray(c, float) - centroid
                outer.append(np.asarray(c, float) + d / (np.linalg.norm(d) + 1e-9) * 0.55)
            for i in range(n):
                a0, a1 = np.asarray(corners[i], float), np.asarray(corners[(i + 1) % n], float)
                b0, b1 = outer[i], outer[(i + 1) % n]
                self.panel(_v(a0, z), _v(a1, z), _v(b1, z), _v(b0, z), "soco", droppable=False)
                self.beam(_v(b0, z + 1.0), _v(b1, z + 1.0), 0.03, droppable=False)
                self.beam(_v(b0, z), _v(b0, z + 1.0), 0.03, droppable=False)

    # --- telhados -----------------------------------------------------------
    def gable_roof(self, o, d, n, w, length, wall_h, rise, close_start, close_end):
        """Telhado de duas águas sobre um salão. Parâmetros de salão (como em
        `_hall_geometry`): `o` = centro da parede inicial (XY), `d` = direção do
        comprimento, `n` = normal à esquerda, `w` = largura, `length` = comprimento.
        `wall_h` é a altura do beiral e `rise` quanto a cumeeira sobe acima dele.
        `close_start`/`close_end` fecham a empena (triângulo de vidro) de cada ponta."""
        nb = max(1, int(round(length / self.bay)))
        up_h = wall_h + rise
        # três fileiras de pontos ao longo do comprimento: beiral esquerdo,
        # beiral direito e cumeeira (a meia largura, mais alta)
        left = [_v(o + n * w / 2 + d * length * i / nb, wall_h) for i in range(nb + 1)]
        right = [_v(o - n * w / 2 + d * length * i / nb, wall_h) for i in range(nb + 1)]
        ridge = [_v(o + d * length * i / nb, up_h) for i in range(nb + 1)]
        for i in range(nb + 1):
            self.beam(left[i], ridge[i], 0.04)
            self.beam(right[i], ridge[i], 0.04)
        self.beam(ridge[0], ridge[-1], 0.05, droppable=False)
        for i in range(nb):
            self.panel(left[i], left[i + 1], ridge[i + 1], ridge[i])
            self.panel(right[i], right[i + 1], ridge[i + 1], ridge[i])
        if close_end:
            self.triangle(left[-1], right[-1], ridge[-1])
        if close_start:
            self.triangle(left[0], right[0], ridge[0])
        self.hang_points.extend(ridge)

    def vault_roof(self, o, d, n, w, length, wall_h, close_start, close_end):
        """Abóbada de berço (meio cilindro achatado) sobre um salão: mesmos
        parâmetros de salão que `gable_roof`, com altura de arco igual a 38% da
        largura. A seção é um semicírculo de `k` = 8 trechos, repetido a cada vão;
        `close_start`/`close_end` fecham as pontas com um leque de vidro."""
        nb = max(1, int(round(length / self.bay)))
        k = 8
        arch_h = w * 0.38
        thetas = np.linspace(0, math.pi, k + 1)

        def ring(i):
            """Arco (k+1 pontos) da seção transversal na posição `i` ao longo do comprimento."""
            base = o + d * length * i / nb
            return [_v(base + n * (math.cos(t) * w / 2), wall_h + math.sin(t) * arch_h) for t in thetas]

        rings = [ring(i) for i in range(nb + 1)]
        for i, r in enumerate(rings):
            for a, b in zip(r, r[1:]):
                self.beam(a, b, 0.035)
        for i in range(nb):
            for j in range(k):
                self.beam(rings[i][j], rings[i + 1][j], 0.03)
                self.panel(rings[i][j], rings[i + 1][j], rings[i + 1][j + 1], rings[i][j + 1])
            self.beam(rings[i][k], rings[i + 1][k], 0.03)
        for flag, idx in ((close_end, -1), (close_start, 0)):
            if flag:
                r = rings[idx]
                center = _v(o + d * (length if idx == -1 else 0.0), wall_h)
                for a, b in zip(r, r[1:]):
                    self.triangle(center, a, b)
        self.hang_points.extend(rings[nb // 2])

    def dome(self, corners, z_eave, radius, tiered, ndiv):
        """Cúpula poligonal sobre o núcleo, com a base em `z_eave`. `corners` é o
        polígono do núcleo (centrado na origem) e `ndiv` quantas divisões cada
        lado recebe. Se `tiered`, ganha tambor e cúpula superior (em camadas);
        senão, uma calota simples. Sempre termina num pináculo vertical."""
        n = len(corners)
        rise = max(0.9, 0.55 * radius)
        # Cada anel = (escala do polígono em relação à base, altura acima do beiral):
        # o polígono encolhe rumo ao centro conforme sobe. Escala 0 é o ápice.
        rings = [(1.0, 0.0), (0.93, 0.38 * rise), (0.78, 0.72 * rise), (0.58, rise)]
        if tiered:
            drum = 0.22 * rise + 0.2
            rings.append((0.58, rise + drum))
            rings += [(0.44, rise + drum + 0.30 * rise), (0.22, rise + drum + 0.52 * rise), (0.0, rise + drum + 0.62 * rise)]
        else:
            rings += [(0.30, rise * 1.12), (0.0, rise * 1.2)]

        def ring_points(s, z):
            """Pontos do anel de escala `s` e altura `z` (acima do beiral): os lados
            do polígono subdivididos em `ndiv` pontos e reduzidos por `s`."""
            pts = []
            for i in range(n):
                c0, c1 = np.asarray(corners[i], float), np.asarray(corners[(i + 1) % n], float)
                for k in range(ndiv):
                    pts.append(_v((c0 + (c1 - c0) * k / ndiv) * s, z_eave + z))
            return pts

        rp = [ring_points(s, z) for s, z in rings]
        total = len(rp[0])
        # nervuras horizontais em cada anel (menos no ápice, que é um ponto),
        # depois nervuras e painéis entre anéis consecutivos
        for r in rp[:-1]:
            for m in range(total):
                self.beam(r[m], r[(m + 1) % total], 0.04)
        for j in range(len(rp) - 1):
            for m in range(total):
                m2 = (m + 1) % total
                self.beam(rp[j][m], rp[j + 1][m], 0.035)
                self.panel(rp[j][m], rp[j][m2], rp[j + 1][m2], rp[j + 1][m])
        apex = rp[-1][0]
        self.beam(apex, apex + UP * (0.8 + 0.1 * radius), 0.03, droppable=False)
        self.hang_points.extend(rp[2])

    # --- trepadeiras mortas (estufa em ruínas) -------------------------------
    def dead_vines(self, count):
        """Pendura `count` trepadeiras mortas (grupo `morto`): cada uma parte de
        um ponto de `hang_points` e desce em passos irregulares, com galhinhos
        ocasionais, até o comprimento sorteado ou até quase tocar o chão."""
        rng = self.rng
        if not self.hang_points:
            return
        for _ in range(count):
            p = np.asarray(rng.choice(self.hang_points), float).copy()
            length = rng.uniform(1.5, 4.5)
            hung = 0.0
            while hung < length and p[2] > 0.3:
                step = np.array([rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), -rng.uniform(0.3, 0.55)])
                q = p + step
                q[2] = max(q[2], 0.2)
                self.beam(p, q, 0.022, "morto", droppable=False, sides=3)
                if rng.random() < 0.25:
                    twig = q + np.array([rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), -rng.uniform(0.0, 0.3)])
                    self.beam(q, twig, 0.012, "morto", droppable=False, sides=3)
                p = q
                hung += abs(step[2])

    # --- piso em xadrez -------------------------------------------------------
    def checker_floor(self, footprints):
        """Piso em xadrez (grupos `piso_preto` e `piso_branco`) em z = 0,04.
        `footprints` é a lista de polígonos XY dos blocos; uma grade de ladrilhos
        quadrados cobre a caixa que os contém, e só ficam os ladrilhos cujo centro
        está dentro de algum polígono. O lado do ladrilho cresce com o tamanho do
        conjunto (de 0,8 a 3 m), para o número de ladrilhos não explodir."""
        xs = [p[0] for poly in footprints for p in poly]
        ys = [p[1] for poly in footprints for p in poly]
        extent = max(max(xs) - min(xs), max(ys) - min(ys))
        tile = min(3.0, max(0.8, extent / 45.0))
        x0 = math.floor(min(xs) / tile) * tile
        y0 = math.floor(min(ys) / tile) * tile
        nx = int(math.ceil((max(xs) - x0) / tile))
        ny = int(math.ceil((max(ys) - y0) / tile))
        for i in range(nx):
            for j in range(ny):
                cx, cy = x0 + (i + 0.5) * tile, y0 + (j + 0.5) * tile
                if not any(_inside((cx, cy), poly) for poly in footprints):
                    continue
                group = "piso_preto" if (i + j) % 2 == 0 else "piso_branco"
                h = tile / 2
                self.panel(
                    _v((cx - h, cy - h), 0.04), _v((cx + h, cy - h), 0.04), _v((cx + h, cy + h), 0.04), _v((cx - h, cy + h), 0.04), group, droppable=False
                )


# --- planejamento dos blocos ---------------------------------------------------


def _hall_geometry(o, d, w, length):
    """Geometria de um salão retangular no plano XY. `o` é o centro da parede
    inicial, `d` a direção unitária do comprimento, `w` a largura e `length`
    o comprimento. Devolve um dict com `n` (normal à esquerda de `d`) e os
    quatro cantos: `s_l`/`s_r` (início, esquerda/direita) e `e_l`/`e_r` (fim)."""
    n = np.array([-d[1], d[0]])
    s_l, s_r = o + n * w / 2, o - n * w / 2
    return dict(o=o, d=d, n=n, w=w, length=length, s_l=s_l, s_r=s_r, e_l=s_l + d * length, e_r=s_r + d * length)


def _hall_polygon(g):
    """Contorno do salão `g` (de `_hall_geometry`) como lista de 4 tuplas XY, em ordem."""
    return [tuple(g["s_l"]), tuple(g["s_r"]), tuple(g["e_r"]), tuple(g["e_l"])]


def _wall_ends(g, name):
    """Pontos inicial e final de cada parede de um salão, na orientação em
    que o parâmetro t cresce (ver `_attach_point`)."""
    return {
        "esq": (g["s_l"], g["e_l"]),
        "dir": (g["s_r"], g["e_r"]),
        "fim": (g["e_r"], g["e_l"]),
        "ini": (g["s_r"], g["s_l"]),
    }[name]


def _attach_point(g, wall, t):
    """Ponto na parede `wall` ("esq", "dir", "fim" ou "ini") do salão `g`, na
    posição `t` (0 a 1, no sentido de `_wall_ends`), e a normal horizontal que
    aponta para fora do salão nessa parede. Serve para ancorar uma ala."""
    a, b = _wall_ends(g, wall)
    point = a + (b - a) * t
    outward = {"esq": g["n"], "dir": -g["n"], "fim": g["d"], "ini": -g["d"]}[wall]
    return point, outward


def _spread(count, k):
    """`k` índices bem espaçados entre `count` possíveis (ex.: 4 de 8: 0,2,4,6)."""
    return sorted({int(round(i * count / k)) % count for i in range(k)})


PADROES = ("livre", "palacio", "cruz")


def plan_blocks(rng, sides, radius, n_floors, n_wings, padrao="livre", fase=None, portas_angulos=None):
    """Decide a geometria da estufa: o núcleo (polígono com cúpula, ou salão
    retangular) e as alas (salões de um pavimento, ligados ao núcleo ou a
    outras alas, sem se sobreporem). `padrao`: "palacio" (duas alas em
    paredes opostas), "cruz" (quatro alas, uma por lado) ou "livre" (faces
    sorteadas). Alas além das do padrão saem das pontas e dos lados de
    outras alas. Devolve a lista de blocos; `blocks[0]["porta"]` diz onde fica
    a porta: `(bloco, parede)`."""
    if sides == 4:
        width = radius * 1.4
        length = width * rng.uniform(1.0, 1.8)
        g = _hall_geometry(np.array([0.0, -length / 2]), np.array([0.0, 1.0]), width, length)
        core = dict(kind="salao", g=g, floors=n_floors, children=[], poly=_hall_polygon(g), style=rng.choice(["aguas", "abobada"]))
        faces = ["esq", "dir", "fim", "ini"]
        opposite = {"esq": "dir", "dir": "esq", "fim": "ini", "ini": "fim"}
    else:
        phase = rng.uniform(0.0, 2 * math.pi) if fase is None else fase
        corners = [np.array([radius * math.cos(phase + 2 * math.pi * i / sides), radius * math.sin(phase + 2 * math.pi * i / sides)]) for i in range(sides)]
        core = dict(kind="cupula", corners=corners, floors=n_floors, children=[], poly=[tuple(c) for c in corners], radius=radius, tiered=radius >= 3.0)
        faces = list(range(sides))
        opposite = None
    blocks = [core]

    def core_slot(face):
        """Ponto médio, normal para fora e comprimento do lado `face` do núcleo
        (onde uma ala pode se prender)."""
        if core["kind"] == "cupula":
            a, b = core["corners"][face], core["corners"][(face + 1) % sides]
            mid = (a + b) / 2
            outward = mid / (np.linalg.norm(mid) + 1e-9)
            return mid, outward, float(np.linalg.norm(b - a))
        point, outward = _attach_point(core["g"], face, 0.5)
        a, b = _wall_ends(core["g"], face)
        return point, outward, float(np.linalg.norm(b - a))

    if padrao == "palacio":
        if opposite is not None:
            first = rng.choice(["esq", "dir"] if rng.random() < 0.7 else ["fim", "ini"])
            primary = [first, opposite[first]]
        else:
            primary = _spread(sides, min(2, sides))
        n_wings = max(n_wings, 2)
    elif padrao == "cruz":
        primary = list(faces) if opposite is not None else _spread(sides, min(4, sides))
        n_wings = max(n_wings, len(primary))
    else:
        primary = list(faces)
        rng.shuffle(primary)
        primary.pop()  # uma face fica livre pra porta
        primary = primary[: max(0, n_wings)]

    def try_add(origin, direction, parent, wall, t, wing_w, wing_l):
        """Tenta criar uma ala saindo de `origin` na `direction`, presa à parede
        `wall` (posição `t`) do bloco `parent`. Se o contorno se sobrepõe a algum
        outro bloco (exceto o pai), desiste e devolve None; senão registra a ala
        em `blocks` e em `parent["children"]` e a devolve."""
        d = np.asarray(direction, float)
        d = d / np.linalg.norm(d)
        g = _hall_geometry(np.asarray(origin, float), d, wing_w, wing_l)
        probe = _hall_geometry(np.asarray(origin, float), d, wing_w, wing_l)
        for other in blocks:
            if other is parent:
                continue
            if _convex_overlap(_hall_polygon(probe), other["poly"]):
                return None
        child = dict(kind="ala", g=g, floors=1, children=[], poly=_hall_polygon(g), style=rng.choice(["aguas", "abobada"]), parent=parent, wall=wall, t=t)
        parent["children"].append(child)
        blocks.append(child)
        return child

    # Primeiro as alas "do padrão", saindo do meio das faces escolhidas do núcleo.
    placed = 0
    for face in primary:
        if placed >= n_wings:
            break
        mid, outward, edge = core_slot(face)
        wing_w = max(2.4, min(edge * rng.uniform(0.5, 0.85), 6.5))
        wing_l = max(3.0, min(radius * rng.uniform(0.9, 1.9), 15.0))
        if try_add(mid, outward, core, face, 0.5, wing_w, wing_l) is not None:
            placed += 1

    # Alas extras: sorteia uma ala existente e tenta prender outra na ponta ou num
    # dos lados dela; as colisões fazem `try_add` falhar, por isso o limite de tentativas.
    attempts = 0
    while placed < n_wings and attempts < 60:
        attempts += 1
        wings = [b for b in blocks if b["kind"] == "ala"]
        if not wings:
            break
        parent = rng.choice(wings)
        g = parent["g"]
        wall = rng.choice(["fim", "esq", "dir"])
        t = 0.5 if wall == "fim" else rng.uniform(0.3, 0.7)
        point, outward = _attach_point(g, wall, t)
        wing_w = max(2.2, min(g["w"] * rng.uniform(0.6, 1.0), 6.0))
        wing_l = max(3.0, min(g["length"] * rng.uniform(0.5, 1.1), 14.0))
        if try_add(point, outward, parent, wall, t, wing_w, wing_l) is not None:
            placed += 1

    if portas_angulos and core["kind"] == "cupula":
        # Portais em direções dadas (ex.: entrada de um lado, saída do oposto):
        # a face cujo centro aponta mais perto de cada ângulo.
        centros = []
        for i in range(sides):
            mid = (core["corners"][i] + core["corners"][(i + 1) % sides]) / 2
            centros.append(math.atan2(mid[1], mid[0]))
        core["portas"] = []
        for ang in portas_angulos:
            face = min(range(sides), key=lambda i: abs(math.atan2(math.sin(centros[i] - ang), math.cos(centros[i] - ang))))
            core["portas"].append((core, face))
        core["porta"] = core["portas"][0]
        return blocks

    used_core_walls = {c["wall"] for c in core["children"]}
    free = [f for f in faces if f not in used_core_walls]
    if free:
        core["porta"] = (core, rng.choice(free))
    else:
        core["porta"] = (core["children"][0], "fim")
    core["portas"] = [core["porta"]]
    return blocks


def _opening_ranges(block, wall, wall_len):
    """Faixas (t0, t1) da parede `wall` do `block` ocupadas por alas filhas
    (onde não se põem painéis). `wall_len` é o comprimento da parede, usado
    para converter a largura da ala em fração de t."""
    ranges = []
    for child in block["children"]:
        if child["wall"] == wall:
            half = child["g"]["w"] / 2 / wall_len
            ranges.append((child["t"] - half, child["t"] + half))
    return ranges


def build_greenhouse(rng, sides, n_floors, radius, n_wings=0, ruined=False, checker=False, padrao="livre", bay=None, fase=None, portas_angulos=None):
    """Monta a estufa e devolve `(grupos, info)`: `grupos` é um dict
    {nome: lista de partes (vértices, faces)} (só os grupos não vazios) e
    `info` traz as pegadas (polígonos XY), o raio ocupado, o ângulo da
    porta e a lista de blocos."""
    pane_loss = rng.uniform(0.35, 0.75) if ruined else 0.0
    rib_loss = rng.uniform(0.04, 0.12) if ruined else 0.0
    bay = bay or BAY
    b = _Builder(rng, pane_loss, rib_loss, bay)
    blocks = plan_blocks(rng, sides, radius, n_floors, n_wings, padrao, fase, portas_angulos)
    core = blocks[0]
    enterable = radius >= 2.2
    portas = core["portas"]

    # Cada bloco vira paredes (com aberturas onde há alas e a porta, se for o caso)
    # e cobertura: cúpula no núcleo poligonal, duas águas ou abóbada nos salões.
    door_angles = []
    for block in blocks:
        if block["kind"] == "cupula":
            corners = block["corners"]
            n = len(corners)
            edge = float(np.linalg.norm(corners[1] - corners[0]))
            ndiv = max(1, int(round(edge / bay)))
            for i in range(n):
                a, c = corners[i], corners[(i + 1) % n]
                openings = []
                for child in block["children"]:
                    if child["wall"] == i:
                        half = child["g"]["w"] / 2 / edge
                        openings.append((0.5 - half, 0.5 + half))
                door = 0.5 if (enterable and any(block is pb and i == pw for pb, pw in portas)) else None
                if door is not None:
                    mid = (a + c) / 2
                    door_angles.append(math.atan2(mid[1], mid[0]))
                b.wall(a, c, block["floors"], openings, door)
            b.gallery(corners, block["floors"])
            b.dome(corners, block["floors"] * STORY, radius, block["tiered"], ndiv)
        else:
            g = block["g"]
            for name in ("esq", "dir", "fim", "ini"):
                a, c = _wall_ends(g, name)
                wall_len = float(np.linalg.norm(c - a))
                openings = _opening_ranges(block, name, wall_len)
                if block["kind"] == "ala" and name == "ini":
                    openings = [(0.0, 1.0)]  # a parede inicial da ala é toda aberta, ligada ao pai
                door = None
                if enterable and any(block is pb and name == pw for pb, pw in portas):
                    door = 0.5
                    mid = (a + c) / 2
                    door_angles.append(math.atan2(mid[1], mid[0]))
                b.wall(a, c, block["floors"], openings, door)
            wall_h = block["floors"] * STORY
            closed_start = block["kind"] != "ala" and not _opening_ranges(block, "ini", g["w"])
            closed_end = True
            if block["style"] == "abobada":
                b.vault_roof(g["o"], g["d"], g["n"], g["w"], g["length"], wall_h, closed_start, closed_end)
            else:
                b.gable_roof(g["o"], g["d"], g["n"], g["w"], g["length"], wall_h, max(1.0, g["w"] * 0.32), closed_start, closed_end)

    footprints = [block["poly"] for block in blocks]
    if checker:
        b.checker_floor(footprints)
    if ruined:
        b.dead_vines(b.rng.randint(6, 14))

    occupied = max(math.hypot(x, y) for poly in footprints for x, y in poly)
    groups = {name: parts for name, parts in b.parts.items() if parts}
    info = dict(
        pegadas=[[(float(x), float(y)) for x, y in poly] for poly in footprints],
        raio_ocupado=float(occupied),
        porta_angulo=float(door_angles[0]) if door_angles else 0.0,
        portas_angulos=[float(a) for a in door_angles],
        n_blocos=len(blocks),
        n_alas=len(blocks) - 1,
        pane_loss=pane_loss,
    )
    return groups, info


def generate_greenhouse(rng, sides=4, n_floors=1, radius=3.6, n_wings=0, ruined=False, checker=False, padrao="livre", bay=None, fase=None, portas_angulos=None, out_path=None):
    """Gera a estufa e grava um .obj por material: a moldura em `out_path`
    (padrão `examples/output/estufa.obj`) e os demais ao lado
    (`group_path`). Retorna `(out_path, info)`; `info["malhas"]` mapeia cada
    grupo gravado ao seu caminho."""
    groups, info = build_greenhouse(rng, sides, n_floors, radius, n_wings, ruined, checker, padrao, bay, fase, portas_angulos)
    if out_path is None:
        from .structures import OUTPUT_DIR

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, "estufa.obj")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    info["malhas"] = {}
    for name, parts in groups.items():
        path = group_path(out_path, name)
        write_obj(path, parts)
        info["malhas"][name] = path
    return out_path, info
