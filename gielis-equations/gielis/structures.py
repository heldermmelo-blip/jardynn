"""Estruturas arquitetônicas simples (torre enterável, gazebo) para o
layout do jardim — não são plantas, mas reaproveitam os mesmos utilitários de
`gielis.plants`: o tubo com seção de Lamé (`mesh_utils.tube_mesh`) para
postes/vigas/torre, e o domo da Superfórmula (`foliage.cap_mesh`,
originalmente o chapéu de cogumelo) para os telhados.
"""

import os

import numpy as np

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


def _generate_tower(rng, n_floors, roof=True):
    """Torre oca, para os aventureiros entrarem: paredes de um polígono de
    16 lados (~6 m de largura, como os andares do livro), porta no térreo,
    janelas nos andares de cima, piso em cada andar (os de cima em anel,
    com um vão central) e uma escada em espiral em torno de um mastro
    central, que atravessa os vãos. As paredes têm espessura zero — o
    material deve ser de dupla face."""
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

    parts = []
    skeleton = []

    def wall_panel(i, z_lo, z_hi):
        vertices = np.array([ring_point(i, z_lo), ring_point(i + 1, z_lo), ring_point(i + 1, z_hi), ring_point(i, z_hi)])
        parts.append((vertices, np.array([[0, 1, 2], [0, 2, 3]])))

    for floor in range(n_floors):
        z0 = floor * floor_h
        z1 = z0 + floor_h
        for i in range(sides):
            if floor == 0 and i == door:
                wall_panel(i, TOWER_DOOR_HEIGHT, z1)
            elif floor >= 1 and (i - floor) % 4 == 0:
                wall_panel(i, z0, z0 + TOWER_WINDOW_SILL)
                wall_panel(i, z0 + TOWER_WINDOW_TOP, z1)
            else:
                wall_panel(i, z0, z1)

        parts.append(
            _polygon_fan(radius_at(z0), sides, 0.02)
            if floor == 0
            else _annulus(radius_at(z0), TOWER_STAIRWELL_RADIUS, sides, z0)
        )
        skeleton.append(
            dict(start=np.array([0.0, 0.0, z0]), end=np.array([0.0, 0.0, z1]), r0=radius_at(z0), r1=radius_at(z1), depth=0)
        )

    pole_top = (n_floors - 1) * floor_h + 1.0
    pole = dict(start=np.array([0.0, 0.0, 0.0]), end=np.array([0.0, 0.0, pole_top]), r0=0.12, r1=0.12, depth=1)
    parts.append(tube_mesh(pole, n_sides=8, cross_section_n=2.0))

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
        parts.append(tube_mesh(step, n_sides=4, cross_section_n=4.0))

    if roof:
        roof_v, roof_f = cap_mesh(
            radius=radius_at(total_h) * 1.25, height=rng.uniform(2.8, 4.0), n_sides=sides, cross_section_n=2.0
        )
        parts.append((roof_v + np.array([0.0, 0.0, total_h]), roof_f))
    else:
        # Torre destelhada: um piso de terra tapando o topo (onde algo pode
        # brotar) e uma cornija de tijolo em volta da borda.
        parts.append(_polygon_fan(radius_at(total_h) * 0.97, sides, total_h - 0.08))
        for i in range(sides):
            a = np.array(ring_point(i, total_h))
            b = np.array(ring_point(i + 1, total_h))
            cornice = dict(start=a, end=b, r0=0.14, r1=0.14, depth=3)
            parts.append(tube_mesh(cornice, n_sides=5, cross_section_n=2.0))

    # Ângulo (rad, plano XY de construção) do centro do setor da porta, pra
    # quem posicionar objetos dentro da torre não bloquear a entrada.
    skeleton[0]["porta_angulo"] = 2 * np.pi * (door + 0.5) / sides
    skeleton[0]["altura_total"] = total_h
    skeleton[0]["raio_topo"] = radius_at(total_h)

    return parts, skeleton


def generate_tower(rng, n_floors, out_path=None, roof=True):
    """Gera uma torre oca e enterável com `n_floors` andares (ver
    `_generate_tower`) e salva como .obj em `out_path` (padrão:
    `examples/output/torre.obj`). Retorna `(out_path, skeleton)` — um
    segmento (o eixo) por andar, mesma convenção de `generate_plant`; `r0`
    é o raio do piso daquele andar e o primeiro segmento traz `porta_angulo`,
    `altura_total` e `raio_topo`. `roof=False` gera a torre destelhada (piso de
    terra e cornija no topo, sem o telhado cônico).
    `n_floors` deve vir de `ynn.generator.generate_torre_conteudo`, pra a
    malha bater com o número de andares do conteúdo gerado."""
    parts, skeleton = _generate_tower(rng, n_floors, roof)
    out_path = _resolve_out_path(out_path, "torre.obj")
    write_obj(out_path, parts)
    return out_path, skeleton


def _generate_gazebo(rng):
    n_posts = rng.choice([6, 8])
    radius = rng.uniform(1.8, 2.6)
    post_height = rng.uniform(2.4, 2.8)
    post_radius = 0.07
    up = np.array([0.0, 0.0, 1.0])
    platform_height = 0.3

    parts = [_polygon_fan(radius * 1.1, n_posts, platform_height)]
    skeleton = []
    corners = _polygon_corners(radius, n_posts, phase=rng.uniform(0.0, 2 * np.pi))

    for corner in corners:
        base = corner + up * platform_height
        _add_beam(parts, skeleton, base, base + up * post_height, post_radius, depth=0)

    entrance = rng.randrange(n_posts)
    for i, corner in enumerate(corners):
        nxt = corners[(i + 1) % n_posts]
        top = up * (platform_height + post_height)
        _add_beam(parts, skeleton, corner + top, nxt + top, post_radius, depth=1)
        if i != entrance:
            rail = up * (platform_height + 0.9)
            _add_beam(parts, skeleton, corner + rail, nxt + rail, post_radius * 0.8, depth=1)

    roof_z = platform_height + post_height
    roof_height = rng.uniform(1.2, 2.0)
    roof_v, roof_f = cap_mesh(radius=radius * 1.25, height=roof_height, n_sides=n_posts, cross_section_n=2.0)
    parts.append((roof_v + np.array([0.0, 0.0, roof_z]), roof_f))
    finial_base = np.array([0.0, 0.0, roof_z + roof_height])
    _add_beam(parts, skeleton, finial_base, finial_base + up * 0.4, 0.04, depth=2)

    return parts, skeleton


def generate_gazebo(rng, out_path=None):
    """Gera um gazebo (pavilhão aberto: plataforma, 6 ou 8 postes, grade
    baixa com uma abertura de entrada, telhado em cúpula e um pináculo) e
    salva como .obj em `out_path` (padrão: `examples/output/gazebo.obj`).
    Retorna `(out_path, skeleton)`."""
    parts, skeleton = _generate_gazebo(rng)
    out_path = _resolve_out_path(out_path, "gazebo.obj")
    write_obj(out_path, parts)
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
