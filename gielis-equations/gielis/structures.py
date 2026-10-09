"""Estruturas arquitetônicas simples (torre enterável, gazebo) para o
layout do jardim — não são plantas, mas reaproveitam os mesmos utilitários de
`gielis.plants`: o tubo com seção de Lamé (`mesh_utils.tube_mesh`) para
postes/vigas/torre, e o domo da Superfórmula (`foliage.cap_mesh`,
originalmente o chapéu de cogumelo) para os telhados.
"""

import os

import numpy as np

from . import ferragens
from .plants.foliage import cap_mesh, leaf_mesh, place_leaf
from .plants.mesh_utils import tube_mesh, write_obj

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "output")


def _resolve_out_path(out_path, default_name):
    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        return os.path.join(OUTPUT_DIR, default_name)
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    return out_path


def _add_beam(parts, skeleton, start, end, radius, depth, n_sides=6):
    segment = dict(start=start, end=end, r0=radius, r1=radius, depth=depth)
    parts.append(tube_mesh(segment, n_sides=n_sides, cross_section_n=2.0))
    skeleton.append(segment)


def _polygon_corners(radius, sides, phase):
    angles = phase + 2 * np.pi * np.arange(sides) / sides
    return [np.array([radius * np.cos(a), radius * np.sin(a), 0.0]) for a in angles]


def _polygon_fan(radius, sides, z):
    """Piso poligonal plano em `z` (dupla face, igual às folhas)."""
    angles = 2 * np.pi * np.arange(sides) / sides
    ring = np.column_stack([radius * np.cos(angles), radius * np.sin(angles), np.full(sides, z)])
    vertices = np.vstack([ring, [[0.0, 0.0, z]]])
    center = sides
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([center, i, j])
        faces.append([center, j, i])
    return vertices, np.array(faces, dtype=int)


TOWER_SIDES = 16
TOWER_FLOOR_HEIGHT = 3.4
TOWER_DOOR_HEIGHT = 2.4
TOWER_WINDOW_SILL = 1.0
TOWER_WINDOW_TOP = 2.3
TOWER_STAIR_STEPS_PER_TURN = 14
TOWER_STAIRWELL_RADIUS = 1.3


def _annulus(radius_out, radius_in, sides, z):
    """Piso em anel (dupla face) com um vão central — o poço da escada."""
    angles = 2 * np.pi * np.arange(sides) / sides
    outer = np.column_stack([radius_out * np.cos(angles), radius_out * np.sin(angles), np.full(sides, z)])
    inner = np.column_stack([radius_in * np.cos(angles), radius_in * np.sin(angles), np.full(sides, z)])
    vertices = np.vstack([outer, inner])
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        for tri in ([i, j, sides + j], [i, sides + j, sides + i]):
            faces.append(tri)
            faces.append(tri[::-1])
    return vertices, np.array(faces, dtype=int)


TOWER_GROUPS = ("tijolo", "madeira", "telhado", "terra", "tapete", "agua", "papel", "ferro", "pedra", "jarro", "musgo")
TOWER_SHUTTER_AJAR_CHANCE = 0.5  # metade das venezianas está entreaberta; as outras, fechadas
TOWER_DOOR_AJAR_DEG = (35.0, 65.0)
TOWER_PEELING_PER_FLOOR = (2, 4)


def tower_group_path(base_path, group):
    """Caminho do .obj de um grupo da torre: o `tijolo` (as paredes) é o
    próprio `base_path`; os outros ficam ao lado (`<nome>_<grupo>.obj`)."""
    if group == "tijolo":
        return base_path
    root, ext = os.path.splitext(base_path)
    return f"{root}_{group}{ext}"


def _grade_para(rng, estilo, origem, direcao, largura, altura, ruina):
    """Grade de uma abertura no estilo da estrutura: art nouveau (filigrana de
    ferro), clássico (barras de ferro) ou rústico (ripas de madeira)."""
    up = np.array([0.0, 0.0, 1.0])
    if estilo == "art_nouveau":
        return ferragens.painel_art_nouveau(rng, origem, direcao, up, largura, altura, ruina=ruina)
    return ferragens.grade_simples(rng, origem, direcao, up, largura, altura, ruina=ruina, madeira=estilo == "rustico")


def _quad(v0, v1, v2, v3):
    return np.array([v0, v1, v2, v3], float), np.array([[0, 1, 2], [0, 2, 3]])


def _leaf_panel(hinge, along, outward, width, z0, z1, angle):
    """Folha de porta ou de veneziana: presa em `hinge` (XY), cobrindo `width`
    na direção `along` quando fechada, girada `angle` (rad) pra fora."""
    direction = along * np.cos(angle) + outward * np.sin(angle)
    far = hinge + direction * width
    return _quad(
        [hinge[0], hinge[1], z0], [far[0], far[1], z0], [far[0], far[1], z1], [hinge[0], hinge[1], z1]
    )


def _disc(center, radius, z, sides=12):
    ring = [[center[0] + radius * np.cos(t), center[1] + radius * np.sin(t), z] for t in np.linspace(0, 2 * np.pi, sides, endpoint=False)]
    vertices = np.vstack([ring, [[center[0], center[1], z]]])
    faces = [[sides, i, (i + 1) % sides] for i in range(sides)]
    return vertices, np.array(faces)


def _generate_tower(rng, n_floors, roof=True, estilo=None, ruina=False):
    """Torre oca, para os aventureiros entrarem, como a do livro: um
    "folly" de tijolo e madeira de ~6 m de largura (polígono de 16 lados), com
    a porta do térreo entreaberta, janelas de venezianas nos andares de cima
    (metade entreabertas, metade fechadas — dá pra entrar por qualquer andar,
    escalando até uma janela), piso de madeira em cada andar (os de cima em anel,
    com um vão central), uma escada em espiral em volta de um mastro central,
    tapete mofado, poças d'água junto às venezianas e papel de parede
    descascando. As paredes têm espessura zero — o material deve ser de dupla
    face. Devolve `(grupos, esqueleto)`: `grupos` mapeia material -> lista de
    partes; o primeiro segmento do esqueleto traz a geometria (porta,
    janelas...).

    `estilo` (`ferragens.ESTILOS`) escolhe as grades das janelas e da porta e o
    parapeito do topo destelhado; com `ruina`, a porta e as venezianas estão
    caídas ou faltando, trechos de parede desabaram e o parapeito se desfez."""
    estilo = estilo or ferragens.sortear_estilo(rng)
    sides = TOWER_SIDES
    floor_h = TOWER_FLOOR_HEIGHT
    radius0 = rng.uniform(2.8, 3.4)
    taper = rng.uniform(0.01, 0.02)  # pouco: o piso em anel do topo tem que sobrar espaço
    total_h = n_floors * floor_h
    door = rng.randrange(sides)
    stair_phase = rng.uniform(0.0, 2 * np.pi)

    def radius_at(z):
        return radius0 * (1.0 - taper * z / floor_h)

    def ring_point(i, z):
        angle = 2 * np.pi * (i % sides) / sides
        return [radius_at(z) * np.cos(angle), radius_at(z) * np.sin(angle), z]

    grupos = {g: [] for g in TOWER_GROUPS}
    skeleton = []
    janelas = []

    def wall_panel(i, z_lo, z_hi):
        vertices = np.array([ring_point(i, z_lo), ring_point(i + 1, z_lo), ring_point(i + 1, z_hi), ring_point(i, z_hi)])
        grupos["tijolo"].append((vertices, np.array([[0, 1, 2], [0, 2, 3]])))

    def sector_frame(i, z):
        """Cantos A e B do setor `i` (XY), vetor ao longo da parede e normal pra fora."""
        a = np.array(ring_point(i, z)[:2])
        b = np.array(ring_point(i + 1, z)[:2])
        along = (b - a) / np.linalg.norm(b - a)
        mid = (a + b) / 2.0
        outward = mid / np.linalg.norm(mid)
        return a, b, along, outward

    for floor in range(n_floors):
        z0 = floor * floor_h
        z1 = z0 + floor_h
        for i in range(sides):
            if floor == 0 and i == door:
                wall_panel(i, TOWER_DOOR_HEIGHT, z1)
                # folha da porta, entreaberta pra fora, presa no canto esquerdo
                a, b, along, outward = sector_frame(i, 0.0)
                largura = float(np.linalg.norm(b - a)) * 0.96
                angulo = np.radians(rng.uniform(*TOWER_DOOR_AJAR_DEG))
                if ruina:
                    angulo = np.radians(rng.uniform(75.0, 110.0))  # a porta caiu da dobradiça, quase deitada
                grupos["madeira"].append(_leaf_panel(a, along, outward, largura, 0.0, TOWER_DOOR_HEIGHT - 0.05, angulo))
                # grade de ferro (ou de ripas) na parte de cima da folha, como nas portas de vidro
                direcao = np.array([*(along * np.cos(angulo) + outward * np.sin(angulo)), 0.0])
                origem = np.array([a[0], a[1], TOWER_DOOR_HEIGHT * 0.36]) + direcao * largura * 0.12
                ferragens.somar(grupos, _grade_para(rng, estilo, origem, direcao, largura * 0.76, TOWER_DOOR_HEIGHT * 0.52, ruina))
            elif floor >= 1 and (i - floor) % 4 == 0:
                z_lo, z_hi = z0 + TOWER_WINDOW_SILL, z0 + TOWER_WINDOW_TOP
                wall_panel(i, z0, z_lo)
                wall_panel(i, z_hi, z1)
                # janela com duas folhas de veneziana
                a, b, along, outward = sector_frame(i, (z_lo + z_hi) / 2.0)
                meia = float(np.linalg.norm(b - a)) / 2.0
                entreaberta = rng.random() < TOWER_SHUTTER_AJAR_CHANCE
                for hinge, direcao in ((a, along), (b, -along)):
                    angulo = np.radians(rng.uniform(55.0, 100.0)) if entreaberta else 0.0
                    if ruina:
                        if rng.random() < 0.3:
                            continue  # a folha da veneziana sumiu
                        angulo = np.radians(rng.uniform(80.0, 150.0))  # pendurada de lado
                    grupos["madeira"].append(_leaf_panel(hinge, direcao, outward, meia * 0.98, z_lo, z_hi, angulo))
                if rng.random() < (0.3 if ruina else 0.45):
                    dentro = -outward * 0.06
                    origem = np.array([a[0] + dentro[0], a[1] + dentro[1], z_lo]) + np.array([*along, 0.0]) * meia * 0.1
                    ferragens.somar(grupos, _grade_para(rng, estilo, origem, np.array([*along, 0.0]), meia * 1.8, z_hi - z_lo, ruina))
                meio = ((a + b) / 2.0)
                angulo_janela = float(np.arctan2(meio[1], meio[0]))
                janelas.append({"andar": floor + 1, "angulo": angulo_janela, "estado": "entreaberta" if entreaberta else "fechada"})
                # poça d'água no chão, junto da veneziana (por dentro)
                centro = meio * 0.78
                grupos["agua"].append(_disc(centro, rng.uniform(0.35, 0.6), z0 + 0.045))
            elif ruina and floor >= n_floors - 2 and rng.random() < 0.12:
                wall_panel(i, z0, z0 + rng.uniform(0.3, 1.2))  # trecho desabado: só o pé da parede ficou
            else:
                wall_panel(i, z0, z1)

        grupos["madeira"].append(
            _polygon_fan(radius_at(z0), sides, 0.02)
            if floor == 0
            else _annulus(radius_at(z0), TOWER_STAIRWELL_RADIUS, sides, z0)
        )
        # tapete mofado: um anel de pano sobre o piso, mais curto que as paredes
        grupos["tapete"].append(_annulus(radius_at(z0) * 0.86, TOWER_STAIRWELL_RADIUS + 0.12, sides, z0 + 0.03))
        # papel de parede descascando: tiras que se soltam do alto e pendem pro meio
        n_tiras = rng.randint(*TOWER_PEELING_PER_FLOOR)
        for _ in range(n_tiras):
            i = rng.randrange(sides)
            if (floor == 0 and i == door) or (floor >= 1 and (i - floor) % 4 == 0):
                continue
            a, b, along, outward = sector_frame(i, z1 - 0.25)  # no raio do alto, onde a tira se prende
            centro = (a + b) / 2.0
            largura = rng.uniform(0.35, 0.6)
            p0 = centro - along * largura / 2.0
            p1 = centro + along * largura / 2.0
            dentro = -outward
            topo = z1 - 0.25
            fim = topo - rng.uniform(0.9, 1.6)
            solta = p0 + dentro * 0.32, p1 + dentro * 0.32
            grupos["papel"].append(
                (
                    np.array([[p0[0], p0[1], topo], [p1[0], p1[1], topo], [solta[1][0], solta[1][1], fim], [solta[0][0], solta[0][1], fim]], float),
                    np.array([[0, 1, 2], [0, 2, 3]]),
                )
            )
        skeleton.append(
            dict(start=np.array([0.0, 0.0, z0]), end=np.array([0.0, 0.0, z1]), r0=radius_at(z0), r1=radius_at(z1), depth=0)
        )

    pole_top = (n_floors - 1) * floor_h + 1.0
    pole = dict(start=np.array([0.0, 0.0, 0.0]), end=np.array([0.0, 0.0, pole_top]), r0=0.12, r1=0.12, depth=1)
    grupos["madeira"].append(tube_mesh(pole, n_sides=8, cross_section_n=2.0))

    steps = (n_floors - 1) * TOWER_STAIR_STEPS_PER_TURN
    for k in range(1, steps + 1):
        angle = stair_phase + 2 * np.pi * k / TOWER_STAIR_STEPS_PER_TURN
        z = k * floor_h / TOWER_STAIR_STEPS_PER_TURN
        direction = np.array([np.cos(angle), np.sin(angle), 0.0])
        step = dict(
            start=direction * 0.12 + np.array([0.0, 0.0, z]),
            end=direction * (TOWER_STAIRWELL_RADIUS - 0.15) + np.array([0.0, 0.0, z]),
            r0=0.1,
            r1=0.1,
            depth=2,
        )
        grupos["madeira"].append(tube_mesh(step, n_sides=4, cross_section_n=4.0))

    if roof:
        roof_v, roof_f = cap_mesh(
            radius=radius_at(total_h) * 1.25, height=rng.uniform(2.8, 4.0), n_sides=sides, cross_section_n=2.0
        )
        grupos["telhado"].append((roof_v + np.array([0.0, 0.0, total_h]), roof_f))
    else:
        # Torre destelhada: um piso de terra tapando o topo (onde algo pode
        # brotar) e uma cornija de tijolo em volta da borda.
        grupos["terra"].append(_polygon_fan(radius_at(total_h) * 0.97, sides, total_h - 0.08))
        for i in range(sides):
            a = np.array(ring_point(i, total_h))
            b = np.array(ring_point(i + 1, total_h))
            cornice = dict(start=a, end=b, r0=0.14, r1=0.14, depth=3)
            grupos["tijolo"].append(tube_mesh(cornice, n_sides=5, cross_section_n=2.0))
        # parapeito sobre a cornija, em cordas de dois setores, no estilo da torre
        for i in range(0, sides, 2):
            a = np.array(ring_point(i, total_h))[:2] * 0.97
            b = np.array(ring_point(i + 2, total_h))[:2] * 0.97
            ferragens.somar(grupos, ferragens.parapeito(rng, a, b, total_h, altura=0.9, estilo=estilo, ruina=ruina))

    # Ângulo (rad, plano XY de construção) do centro do setor da porta, pra
    # quem posicionar objetos dentro da torre não bloquear a entrada.
    skeleton[0]["porta_angulo"] = 2 * np.pi * (door + 0.5) / sides
    skeleton[0]["altura_total"] = total_h
    skeleton[0]["raio_topo"] = radius_at(total_h)
    skeleton[0]["janelas"] = janelas
    skeleton[0]["estilo"] = estilo
    skeleton[0]["ruina"] = ruina
    return grupos, skeleton


def generate_tower(rng, n_floors, out_path=None, roof=True, estilo=None, ruina=False):
    """Gera uma torre oca e enterável com `n_floors` andares (ver
    `_generate_tower`) e salva como .obj em `out_path` (padrão:
    `examples/output/torre.obj`) — as paredes de tijolo no próprio arquivo e
    cada outro material ao lado (`tower_group_path`). Retorna `(out_path,
    skeleton)` — um segmento (o eixo) por andar, mesma convenção de
    `generate_plant`; `r0` é o raio do piso daquele andar e o primeiro
    segmento traz `porta_angulo`, `altura_total`, `raio_topo`, `janelas` (andar,
    ângulo e estado da veneziana de cada uma) e `malhas` (material -> .obj).
    `roof=False` gera a torre destelhada (piso de terra e cornija no topo, sem
    o telhado cônico).
    `n_floors` deve vir de `ynn.generator.generate_torre_conteudo`, pra a
    malha bater com o número de andares do conteúdo gerado."""
    grupos, skeleton = _generate_tower(rng, n_floors, roof, estilo, ruina)
    out_path = _resolve_out_path(out_path, "torre.obj")
    malhas = {}
    for grupo, partes in grupos.items():
        if not partes:
            continue
        path = tower_group_path(out_path, grupo)
        write_obj(path, partes)
        malhas[grupo] = path
    skeleton[0]["malhas"] = malhas
    return out_path, skeleton


def _generate_gazebo(rng, estilo=None, ruina=False):
    """Gazebo: plataforma, 6 ou 8 postes, parapeito baixo (com um vão de
    entrada) no `estilo` dado, telhado em cúpula e pináculo. Em `ruina`, parte do
    telhado, dos postes e do parapeito se foi, o musgo cobre a base. Devolve
    `(grupos, esqueleto)`: `madeira` (o corpo), `telhado` e os grupos das
    ferragens (`ferro`, `pedra`, `jarro`, `musgo`)."""
    estilo = estilo or ferragens.sortear_estilo(rng)
    n_posts = rng.choice([6, 8])
    radius = rng.uniform(1.8, 2.6)
    post_height = rng.uniform(2.4, 2.8)
    post_radius = 0.07
    up = np.array([0.0, 0.0, 1.0])
    platform_height = 0.3

    grupos = {g: [] for g in ("madeira", "telhado", "ferro", "pedra", "jarro", "musgo")}
    grupos["madeira"].append(_polygon_fan(radius * 1.1, n_posts, platform_height))
    skeleton = []
    corners = _polygon_corners(radius, n_posts, phase=rng.uniform(0.0, 2 * np.pi))
    postes_altos = []

    for corner in corners:
        base = corner + up * platform_height
        altura = post_height * (rng.uniform(0.45, 0.8) if ruina and rng.random() < 0.25 else 1.0)
        postes_altos.append(altura >= post_height)
        parts = []
        _add_beam(parts, skeleton, base, base + up * altura, post_radius, depth=0)
        grupos["madeira"] += parts

    entrance = rng.randrange(n_posts)
    for i, corner in enumerate(corners):
        nxt = corners[(i + 1) % n_posts]
        top = up * (platform_height + post_height)
        if postes_altos[i] and postes_altos[(i + 1) % n_posts]:
            parts = []
            _add_beam(parts, skeleton, corner + top, nxt + top, post_radius, depth=1)
            grupos["madeira"] += parts
        if i != entrance:
            ferragens.somar(
                grupos,
                ferragens.parapeito(
                    rng, corner[:2] * 0.97, nxt[:2] * 0.97, platform_height, altura=0.9, estilo=estilo, ruina=ruina, com_jarros=False
                ),
            )

    roof_z = platform_height + post_height
    if not ruina or rng.random() < 0.5:  # na ruína, metade dos coretos perdeu o telhado
        roof_height = rng.uniform(1.2, 2.0)
        roof_v, roof_f = cap_mesh(radius=radius * 1.25, height=roof_height, n_sides=n_posts, cross_section_n=2.0)
        grupos["telhado"].append((roof_v + np.array([0.0, 0.0, roof_z]), roof_f))
        parts = []
        finial_base = np.array([0.0, 0.0, roof_z + roof_height])
        _add_beam(parts, skeleton, finial_base, finial_base + up * 0.4, 0.04, depth=2)
        grupos["madeira"] += parts
    if skeleton:
        skeleton[0]["estilo"] = estilo
        skeleton[0]["ruina"] = ruina
    return grupos, skeleton


def gazebo_group_path(base_path, group):
    """Caminho do .obj de um grupo do gazebo: `madeira` (o corpo) é o próprio
    `base_path`; os outros ficam ao lado."""
    if group == "madeira":
        return base_path
    root, ext = os.path.splitext(base_path)
    return f"{root}_{group}{ext}"


def generate_gazebo(rng, out_path=None, estilo=None, ruina=False):
    """Gera um gazebo (pavilhão aberto: plataforma, 6 ou 8 postes, parapeito
    baixo com uma abertura de entrada, telhado em cúpula e um pináculo) e
    salva como .obj em `out_path` (padrão: `examples/output/gazebo.obj`) — o
    corpo de madeira no próprio arquivo e cada outro material ao lado
    (`gazebo_group_path`). Retorna `(out_path, skeleton)`; o primeiro segmento
    traz `malhas` (material -> .obj), `estilo` e `ruina`."""
    grupos, skeleton = _generate_gazebo(rng, estilo, ruina)
    out_path = _resolve_out_path(out_path, "gazebo.obj")
    malhas = {}
    for grupo, partes in grupos.items():
        if not partes:
            continue
        path = gazebo_group_path(out_path, grupo)
        write_obj(path, partes)
        malhas[grupo] = path
    skeleton[0]["malhas"] = malhas
    return out_path, skeleton


def generate_tower_vines(rng, skeleton, out_path=None):
    """Trepadeiras subindo rente à parede externa da torre (`skeleton` é o
    devolvido por `generate_tower`): de 3 a 6 hastes que sobem do pé até uma
    altura sorteada, ondulando de lado a lado, com ramos laterais e folhas
    deitadas sobre a parede — formam manchas, não uma cobertura uniforme.
    Salva um .obj (padrão: `examples/output/trepadeiras.obj`). Retorna
    `(out_path, hastes)`, com os pontos (ângulo, altura) de cada haste."""
    zs = [float(seg["start"][2]) for seg in skeleton] + [float(skeleton[-1]["end"][2])]
    rs = [float(seg["r0"]) for seg in skeleton] + [float(skeleton[-1]["r1"])]
    total_h = zs[-1]

    def point(angle, z):
        r = float(np.interp(z, zs, rs)) + 0.1
        return np.array([r * np.cos(angle), r * np.sin(angle), z])

    parts = []
    hastes = []

    def grow(angle, z, steps, wobble, climb):
        """Anda `steps` passos a partir de (angle, z), emitindo caule e folhas."""
        trail = [(angle, z)]
        for _ in range(steps):
            angle += rng.uniform(-wobble, wobble)
            z += climb()
            trail.append((angle, min(z, total_h)))
        for (a0, z0), (a1, z1) in zip(trail, trail[1:]):
            stem = dict(start=point(a0, z0), end=point(a1, z1), r0=0.035, r1=0.03, depth=0)
            parts.append(tube_mesh(stem, n_sides=5, cross_section_n=2.0))
        for a, zz in trail:
            outward = np.array([np.cos(a), np.sin(a), 0.0])
            for _ in range(rng.randint(2, 4)):
                local_v, local_f = leaf_mesh(
                    shape_power=rng.uniform(1.8, 3.0), length=rng.uniform(0.25, 0.42), width_ratio=0.45, n_points=9
                )
                world_v = place_leaf(
                    local_v, point(a, zz), outward, twist=rng.uniform(0.0, 2 * np.pi), droop_deg=rng.uniform(3.0, 15.0)
                )
                parts.append((world_v, local_f))
        return trail

    for _ in range(rng.randint(3, 6)):
        target = rng.uniform(0.35, 1.0) * total_h
        steps = max(2, int(target / 0.4))
        trail = grow(rng.uniform(0.0, 2 * np.pi), 0.1, steps, 0.18, lambda: rng.uniform(0.3, 0.5))
        hastes.append(trail)
        for index in range(3, len(trail)):
            if rng.random() < 0.3:
                a, z = trail[index]
                grow(a, z, rng.randint(3, 6), 0.35, lambda: rng.uniform(0.0, 0.25))

    out_path = _resolve_out_path(out_path, "trepadeiras.obj")
    write_obj(out_path, parts)
    return out_path, hastes
