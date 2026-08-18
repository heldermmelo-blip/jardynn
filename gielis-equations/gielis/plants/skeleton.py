"""Ramificação procedural genérica (esqueleto de galhos).

Algoritmo comum (quantos galhos, ângulos, afinamento), sem relação com
nenhuma equação específica do livro — os parâmetros é que mudam de espécie
para espécie (ver `gielis.plants.generator.BRANCHING_SPECIES`).
"""

import numpy as np

from .mesh_utils import orthonormal_basis, rotate_around_axis


def generate_skeleton(
    rng,
    start=(0.0, 0.0, 0.0),
    direction=(0.0, 0.0, 1.0),
    length=1.0,
    radius=0.06,
    depth=0,
    max_depth=4,
    length_falloff=0.72,
    radius_falloff=0.68,
    branch_angle_deg=28.0,
    branches_per_node=2,
    root_branches=(2, 3),
    phototropism=0.15,
):
    """Gera recursivamente uma lista de segmentos (galhos), cada um um dict
    com start, end, r0, r1, depth. `rng` é um `random.Random` (para
    reprodutibilidade via seed)."""
    start = np.asarray(start, dtype=float)
    direction = np.asarray(direction, dtype=float)
    direction = direction / np.linalg.norm(direction)
    end = start + direction * length
    r1 = radius * radius_falloff

    segments = [dict(start=start, end=end, r0=radius, r1=r1, depth=depth)]

    if depth >= max_depth or r1 < 0.004:
        return segments

    n_branches = branches_per_node if depth > 0 else rng.choice(list(root_branches))
    branch_angle = np.radians(branch_angle_deg)
    for i in range(n_branches):
        twist = 2 * np.pi * i / n_branches + rng.uniform(-0.3, 0.3)
        u, v = orthonormal_basis(direction)
        tilt_axis = np.cos(twist) * u + np.sin(twist) * v
        new_dir = rotate_around_axis(direction, tilt_axis, branch_angle * rng.uniform(0.7, 1.3))
        new_dir = new_dir + np.array([0.0, 0.0, phototropism])  # fototropismo simplificado
        new_dir = new_dir / np.linalg.norm(new_dir)
        segments += generate_skeleton(
            rng,
            end,
            new_dir,
            length * length_falloff * rng.uniform(0.85, 1.05),
            r1,
            depth + 1,
            max_depth,
            length_falloff,
            radius_falloff,
            branch_angle_deg,
            branches_per_node,
            root_branches,
            phototropism,
        )
    return segments
