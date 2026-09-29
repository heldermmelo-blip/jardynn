"""Estruturas arquitetônicas simples (torre, estufa) para o layout do
jardim — não são plantas, mas reaproveitam os mesmos utilitários de
`gielis.plants`: o tubo com seção de Lamé (`mesh_utils.tube_mesh`) para
postes/vigas/torre, e o domo da Superfórmula (`foliage.cap_mesh`,
originalmente o chapéu de cogumelo) para o telhado da torre.
"""

import os

import numpy as np

from .plants.foliage import cap_mesh
from .plants.mesh_utils import tube_mesh, write_obj

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "output")


def _resolve_out_path(out_path, default_name):
    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        return os.path.join(OUTPUT_DIR, default_name)
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    return out_path


def _generate_tower(rng):
    height = rng.uniform(8.0, 14.0)
    base_radius = rng.uniform(0.9, 1.5)
    top_radius = base_radius * rng.uniform(0.55, 0.75)

    shaft = dict(
        start=np.array([0.0, 0.0, 0.0]), end=np.array([0.0, 0.0, height]), r0=base_radius, r1=top_radius, depth=0
    )
    parts = [tube_mesh(shaft, n_sides=12, cross_section_n=2.0)]

    roof_v, roof_f = cap_mesh(
        radius=top_radius * 1.15, height=rng.uniform(2.5, 4.0), n_sides=12, cross_section_n=rng.uniform(1.6, 2.2)
    )
    roof_v = roof_v + np.array([0.0, 0.0, height])
    parts.append((roof_v, roof_f))

    return parts, [shaft]


def generate_tower(rng, out_path=None):
    """Gera uma torre (fuste afunilado + telhado cônico) e salva como .obj
    em `out_path` (padrão: `examples/output/torre.obj`). Retorna
    `(out_path, skeleton)`, mesma convenção de `gielis.plants.generate_plant`."""
    parts, skeleton = _generate_tower(rng)
    out_path = _resolve_out_path(out_path, "torre.obj")
    write_obj(out_path, parts)
    return out_path, skeleton


def _generate_greenhouse(rng):
    width = rng.uniform(4.0, 6.5)
    depth = rng.uniform(6.0, 10.0)
    wall_height = rng.uniform(2.2, 3.0)
    ridge_height = wall_height + rng.uniform(1.5, 2.5)
    post_radius = 0.06

    corners = [
        np.array([-width / 2, -depth / 2, 0.0]),
        np.array([width / 2, -depth / 2, 0.0]),
        np.array([width / 2, depth / 2, 0.0]),
        np.array([-width / 2, depth / 2, 0.0]),
    ]

    parts = []
    skeleton = []
    for corner in corners:
        post = dict(start=corner, end=corner + np.array([0.0, 0.0, wall_height]), r0=post_radius, r1=post_radius, depth=0)
        parts.append(tube_mesh(post, n_sides=6, cross_section_n=2.0))
        skeleton.append(post)

    ridge_a = np.array([0.0, -depth / 2, ridge_height])
    ridge_b = np.array([0.0, depth / 2, ridge_height])
    ridge = dict(start=ridge_a, end=ridge_b, r0=post_radius, r1=post_radius, depth=1)
    parts.append(tube_mesh(ridge, n_sides=6, cross_section_n=2.0))
    skeleton.append(ridge)

    top_corners = [corner + np.array([0.0, 0.0, wall_height]) for corner in corners]
    ridge_ends = [ridge_a, ridge_a, ridge_b, ridge_b]
    for top_corner, ridge_end in zip(top_corners, ridge_ends):
        beam = dict(start=top_corner, end=ridge_end, r0=post_radius, r1=post_radius, depth=1)
        parts.append(tube_mesh(beam, n_sides=6, cross_section_n=2.0))
        skeleton.append(beam)

    return parts, skeleton


def generate_greenhouse(rng, out_path=None):
    """Gera o esqueleto de uma estufa (quatro postes + cumeeira + águas do
    telhado, sem vidro/painéis) e salva como .obj em `out_path` (padrão:
    `examples/output/estufa.obj`). Retorna `(out_path, skeleton)`."""
    parts, skeleton = _generate_greenhouse(rng)
    out_path = _resolve_out_path(out_path, "estufa.obj")
    write_obj(out_path, parts)
    return out_path, skeleton
