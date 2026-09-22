"""Espécies de planta e a função de montagem principal (`generate_plant`).

Cada espécie "ramificada" (BRANCHING_SPECIES) reaproveita o mesmo motor —
esqueleto de galhos (`skeleton.generate_skeleton`) + tubo com seção de
Lamé (`mesh_utils.tube_mesh`) + folhas (`foliage.leaf_mesh`) — variando só
os parâmetros. `flor`, `cogumelo` e `samambaia` têm geometria própria
demais para caber nesse molde e usam funções dedicadas.
"""

import os

import numpy as np

from . import foliage
from .mesh_utils import orthonormal_basis, rotate_around_axis, tube_mesh, write_obj
from .skeleton import generate_skeleton

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "examples", "output"
)

BRANCHING_SPECIES = {
    "arvore": dict(
        skeleton=dict(max_depth=4, length=1.0, radius=0.06, branch_angle_deg=28.0, branches_per_node=2),
        trunk_cross_n=1.4,
        branch_cross_n=2.0,
        leaf_length=(0.18, 0.32),
        leaves_per_tip=(2, 4),
    ),
    "arbusto": dict(
        skeleton=dict(
            max_depth=3,
            length=0.30,
            radius=0.03,
            branch_angle_deg=42.0,
            branches_per_node=3,
            root_branches=(3, 4),
            length_falloff=0.62,
        ),
        trunk_cross_n=2.0,
        branch_cross_n=2.0,
        leaf_length=(0.07, 0.13),
        leaves_per_tip=(2, 3),
    ),
    "espinheiro": dict(
        skeleton=dict(
            max_depth=4,
            length=0.22,
            radius=0.02,
            branch_angle_deg=50.0,
            branches_per_node=3,
            root_branches=(3, 5),
            length_falloff=0.6,
        ),
        trunk_cross_n=2.5,
        branch_cross_n=2.5,
        leaf_length=(0.04, 0.07),
        leaves_per_tip=(1, 2),
    ),
    "bambu": dict(
        skeleton=dict(
            max_depth=2,
            length=0.6,
            radius=0.035,
            branch_angle_deg=6.0,
            branches_per_node=1,
            root_branches=(1, 1),
            length_falloff=0.85,
            radius_falloff=0.9,
            phototropism=0.05,
        ),
        trunk_cross_n=1.2,
        branch_cross_n=1.2,
        leaf_length=(0.1, 0.16),
        leaves_per_tip=(3, 5),
    ),
    "videira": dict(
        skeleton=dict(
            max_depth=4,
            length=0.4,
            radius=0.015,
            branch_angle_deg=55.0,
            branches_per_node=1,
            root_branches=(1, 2),
            length_falloff=0.85,
            phototropism=0.02,
        ),
        trunk_cross_n=2.0,
        branch_cross_n=2.0,
        leaf_length=(0.05, 0.09),
        leaves_per_tip=(2, 3),
    ),
}


def _generate_branching_plant(rng, params):
    skeleton = generate_skeleton(rng, **params["skeleton"])
    max_depth = params["skeleton"].get("max_depth", 4)

    parts = []
    for seg in skeleton:
        cross_n = params["trunk_cross_n"] if seg["depth"] == 0 else params["branch_cross_n"]
        parts.append(tube_mesh(seg, n_sides=10, cross_section_n=cross_n))

        if seg["depth"] >= max_depth - 1:
            tangent_vec = seg["end"] - seg["start"]
            n_leaves = rng.randint(*params["leaves_per_tip"])
            for k in range(n_leaves):
                twist = 2 * np.pi * k / n_leaves + rng.uniform(-0.4, 0.4)
                shape_power = rng.uniform(1.8, 3.5)
                leaf_len = rng.uniform(*params["leaf_length"])
                local_v, local_f = foliage.leaf_mesh(shape_power=shape_power, length=leaf_len)
                world_v = foliage.place_leaf(
                    local_v, seg["end"], tangent_vec, twist=twist, droop_deg=rng.uniform(10, 35)
                )
                parts.append((world_v, local_f))
    return parts, skeleton


def _generate_flower(rng):
    stem_length = rng.uniform(0.35, 0.55)
    stem = dict(
        start=np.array([0.0, 0.0, 0.0]), end=np.array([0.0, 0.0, stem_length]), r0=0.012, r1=0.008, depth=0
    )
    parts = [tube_mesh(stem, n_sides=8, cross_section_n=2.0)]

    n_petals = rng.choice([5, 6, 8, 13])
    bloom_v, bloom_f = foliage.flower_bloom_mesh(
        n_petals=n_petals,
        radius=rng.uniform(0.08, 0.16),
        n1=rng.uniform(0.2, 0.5),
        n2=rng.uniform(1.2, 2.2),
        n3=rng.uniform(1.2, 2.2),
    )
    bloom_v = bloom_v + np.array([0.0, 0.0, stem_length])
    parts.append((bloom_v, bloom_f))
    return parts, [stem]


def _generate_mushroom(rng):
    stem_length = rng.uniform(0.08, 0.16)
    stem_radius = rng.uniform(0.012, 0.022)
    stem = dict(
        start=np.array([0.0, 0.0, 0.0]),
        end=np.array([0.0, 0.0, stem_length]),
        r0=stem_radius,
        r1=stem_radius * 0.9,
        depth=0,
    )
    parts = [tube_mesh(stem, n_sides=8, cross_section_n=2.0)]

    cap_v, cap_f = foliage.cap_mesh(
        radius=rng.uniform(0.04, 0.09),
        height=rng.uniform(0.02, 0.05),
        cross_section_n=rng.uniform(1.8, 3.0),
    )
    cap_v = cap_v + np.array([0.0, 0.0, stem_length])
    parts.append((cap_v, cap_f))
    return parts, [stem]


def _generate_fern(rng):
    stub = dict(start=np.array([0.0, 0.0, 0.0]), end=np.array([0.0, 0.0, 0.04]), r0=0.015, r1=0.012, depth=0)
    parts = [tube_mesh(stub, n_sides=8, cross_section_n=2.0)]

    base = stub["end"]
    tangent = np.array([0.0, 0.0, 1.0])
    n_fronds = rng.randint(5, 8)
    for k in range(n_fronds):
        twist = 2 * np.pi * k / n_fronds + rng.uniform(-0.2, 0.2)
        frond_len = rng.uniform(0.25, 0.4)
        local_v, local_f = foliage.leaf_mesh(shape_power=rng.uniform(1.2, 1.8), length=frond_len, width_ratio=0.22)
        world_v = foliage.place_leaf(local_v, base, tangent, twist=twist, droop_deg=rng.uniform(35, 60))
        parts.append((world_v, local_f))
    return parts, [stub]


SPECIAL_SPECIES = {
    "flor": _generate_flower,
    "cogumelo": _generate_mushroom,
    "samambaia": _generate_fern,
}

SPECIES = sorted(set(BRANCHING_SPECIES) | set(SPECIAL_SPECIES))


def _generate_fallen_branch(rng):
    """Um galho ou tronco caído/quebrado — não é espécie viva, é detrito de
    jardim sem cuidado. Cresce quase na horizontal (leve inclinação
    aleatória) em vez de para cima, às vezes com 1-2 cotos quebrados saindo
    pro lado em ângulo."""
    length = rng.uniform(0.5, 1.1)
    radius = rng.uniform(0.02, 0.05)
    heading = rng.uniform(0.0, 2 * np.pi)
    tilt = rng.uniform(-0.15, 0.15)
    direction = np.array([np.cos(heading), np.sin(heading), tilt])
    direction = direction / np.linalg.norm(direction)

    start = np.array([0.0, 0.0, 0.0])
    end = start + direction * length
    trunk = dict(start=start, end=end, r0=radius, r1=radius * rng.uniform(0.5, 0.75), depth=0)
    parts = [tube_mesh(trunk, n_sides=8, cross_section_n=rng.uniform(1.6, 2.2))]

    for _ in range(rng.randint(0, 2)):
        t = rng.uniform(0.2, 0.8)
        stub_start = start + direction * length * t
        stub_length = length * rng.uniform(0.15, 0.35)
        u, v = orthonormal_basis(direction)
        twist = rng.uniform(0.0, 2 * np.pi)
        tilt_axis = np.cos(twist) * u + np.sin(twist) * v
        stub_dir = rotate_around_axis(direction, tilt_axis, rng.uniform(0.6, 1.4))
        stub_end = stub_start + stub_dir * stub_length
        stub_radius = radius * rng.uniform(0.3, 0.5)
        stub = dict(start=stub_start, end=stub_end, r0=stub_radius, r1=stub_radius * 0.6, depth=1)
        parts.append(tube_mesh(stub, n_sides=6, cross_section_n=2.0))

    return parts, [trunk]


def generate_fallen_branch(rng, out_path=None):
    """Gera um galho/tronco caído (ver `_generate_fallen_branch`) e salva
    como .obj em `out_path` (padrão: `examples/output/galho_caido.obj`).
    Retorna `(out_path, skeleton)`, mesma convenção de `generate_plant`."""
    parts, skeleton = _generate_fallen_branch(rng)

    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, "galho_caido.obj")
    else:
        out_dir = os.path.dirname(os.path.abspath(out_path))
        os.makedirs(out_dir, exist_ok=True)

    write_obj(out_path, parts)
    return out_path, skeleton


def generate_plant(rng, species, out_path=None, **skeleton_overrides):
    """Gera uma planta da espécie `species` e salva como .obj em `out_path`
    (padrão: `examples/output/<species>.obj`). Retorna `(out_path,
    skeleton)` — `skeleton` é a lista de segmentos (para espécies sem
    ramificação, uma lista com um único segmento "caule").

    `skeleton_overrides` (só vale para espécies em `BRANCHING_SPECIES`)
    sobrescreve parâmetros do esqueleto, ex. `max_depth=6`.
    """
    if species in BRANCHING_SPECIES:
        params = BRANCHING_SPECIES[species]
        if skeleton_overrides:
            params = dict(params)
            params["skeleton"] = {**params["skeleton"], **skeleton_overrides}
        parts, skeleton = _generate_branching_plant(rng, params)
    elif species in SPECIAL_SPECIES:
        parts, skeleton = SPECIAL_SPECIES[species](rng)
    else:
        raise ValueError(f"espécie desconhecida: {species!r} (opções: {SPECIES})")

    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"{species}.obj")
    else:
        out_dir = os.path.dirname(os.path.abspath(out_path))
        os.makedirs(out_dir, exist_ok=True)

    write_obj(out_path, parts)
    return out_path, skeleton
