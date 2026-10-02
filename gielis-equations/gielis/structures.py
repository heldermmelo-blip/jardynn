"""Estruturas arquitetônicas simples (torre, estufa, gazebo) para o layout
do jardim — não são plantas, mas reaproveitam os mesmos utilitários de
`gielis.plants`: o tubo com seção de Lamé (`mesh_utils.tube_mesh`) para
postes/vigas/torre, e o domo da Superfórmula (`foliage.cap_mesh`,
originalmente o chapéu de cogumelo) para os telhados.
"""

import os

import numpy as np

from .plants.foliage import cap_mesh
from .plants.mesh_utils import tube_mesh, write_obj

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "output")

STORY_HEIGHT = 2.6


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


def _generate_tower(rng, n_floors):
    floor_height = rng.uniform(3.2, 4.0)
    base_radius = rng.uniform(1.0, 1.6)
    taper_per_floor = rng.uniform(0.04, 0.08)

    parts = []
    skeleton = []
    radius = base_radius
    z = 0.0
    for _ in range(n_floors):
        next_radius = max(radius * (1.0 - taper_per_floor), base_radius * 0.35)
        segment = dict(
            start=np.array([0.0, 0.0, z]), end=np.array([0.0, 0.0, z + floor_height]), r0=radius, r1=next_radius, depth=0
        )
        parts.append(tube_mesh(segment, n_sides=12, cross_section_n=2.0))
        skeleton.append(segment)
        radius = next_radius
        z += floor_height

    roof_v, roof_f = cap_mesh(
        radius=radius * 1.2, height=rng.uniform(2.5, 4.0), n_sides=12, cross_section_n=rng.uniform(1.6, 2.2)
    )
    roof_v = roof_v + np.array([0.0, 0.0, z])
    parts.append((roof_v, roof_f))

    return parts, skeleton


def generate_tower(rng, n_floors, out_path=None):
    """Gera uma torre com `n_floors` andares (um segmento afunilado por
    andar, mais o telhado cônico) e salva como .obj em `out_path` (padrão:
    `examples/output/torre.obj`). Retorna `(out_path, skeleton)` — um
    segmento por andar, mesma convenção de `gielis.plants.generate_plant`.
    `n_floors` deve vir de `ynn.generator.generate_torre_conteudo`, pra a
    malha bater com o número de andares do conteúdo gerado."""
    parts, skeleton = _generate_tower(rng, n_floors)
    out_path = _resolve_out_path(out_path, "torre.obj")
    write_obj(out_path, parts)
    return out_path, skeleton


def _generate_greenhouse(rng, sides, n_floors, radius):
    wall_height = STORY_HEIGHT * n_floors
    post_radius = 0.06 + 0.02 * (n_floors - 1)

    if sides == 4:
        width = radius * 1.4
        depth = width * rng.uniform(1.0, 1.5)
        corners = [
            np.array([-width / 2, -depth / 2, 0.0]),
            np.array([width / 2, -depth / 2, 0.0]),
            np.array([width / 2, depth / 2, 0.0]),
            np.array([-width / 2, depth / 2, 0.0]),
        ]
    else:
        corners = _polygon_corners(radius, sides, phase=rng.uniform(0.0, 2 * np.pi))

    parts = []
    skeleton = []
    up = np.array([0.0, 0.0, 1.0])

    for corner in corners:
        _add_beam(parts, skeleton, corner, corner + up * wall_height, post_radius, depth=0)

    for level in range(1, n_floors + 1):
        for i, corner in enumerate(corners):
            nxt = corners[(i + 1) % len(corners)]
            _add_beam(parts, skeleton, corner + up * STORY_HEIGHT * level, nxt + up * STORY_HEIGHT * level, post_radius, depth=1)

    top_corners = [corner + up * wall_height for corner in corners]
    if sides == 4:
        ridge_height = wall_height + rng.uniform(1.5, 2.5)
        ridge_a = np.array([0.0, -depth / 2, ridge_height])
        ridge_b = np.array([0.0, depth / 2, ridge_height])
        _add_beam(parts, skeleton, ridge_a, ridge_b, post_radius, depth=1)
        for top_corner, ridge_end in zip(top_corners, [ridge_a, ridge_a, ridge_b, ridge_b]):
            _add_beam(parts, skeleton, top_corner, ridge_end, post_radius, depth=1)
    else:
        apex = np.array([0.0, 0.0, wall_height + radius * rng.uniform(0.5, 0.8)])
        for top_corner in top_corners:
            _add_beam(parts, skeleton, top_corner, apex, post_radius, depth=1)

    return parts, skeleton


def generate_greenhouse(rng, sides=4, n_floors=1, radius=3.6, out_path=None):
    """Gera o esqueleto de uma estufa (postes nos cantos, vigas por andar e
    águas do telhado, sem vidro/painéis) e salva como .obj em `out_path`
    (padrão: `examples/output/estufa.obj`). `sides` é o número de cantos da
    planta baixa (4 = retangular com cumeeira; os demais, polígono regular
    com telhado em pirâmide), `n_floors` o número de andares e `radius` o
    raio circunscrito da planta (m). Retorna `(out_path, skeleton)`."""
    parts, skeleton = _generate_greenhouse(rng, sides, n_floors, radius)
    out_path = _resolve_out_path(out_path, "estufa.obj")
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
