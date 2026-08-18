"""Folhas, flor e chapéu de cogumelo — as partes "não-tubulares" de uma
planta.
"""

import numpy as np

from .. import lame, superformula


def leaf_mesh(shape_power=2.5, length=0.3, width_ratio=0.35, n_points=24):
    """Malha plana (dupla face) de uma folha, no plano XY local, com a base
    (ponto de fixação no galho) na origem e a ponta no eixo +y.

    NÃO usa a Eq. 10.1 do livro diretamente: a extração do PDF deixou
    ambíguo se o expoente interno daquela equação é fixo (4) ou é o próprio
    parâmetro de forma n — e para os valores de n citados no livro (0.02 a
    0.1), as duas leituras possíveis geram curvas degeneradas, não uma
    silhueta de folha utilizável (ver `gielis/models.py`).

    Em vez disso, usa um perfil direto e sempre bem-comportado: a
    meia-largura em função da altura y (de 0 até `length`) é
    `width_ratio*length*sin(pi*y/length)^shape_power` — zero na base e na
    ponta, máxima no meio. `shape_power` maior dá uma folha mais fina e
    pontiaguda (lanceolada); menor dá uma folha mais arredondada.
    """
    y = np.linspace(0.0, length, n_points)
    # np.maximum(..., 0.0): ruído de ponto flutuante pode deixar sin(...) levemente
    # negativo bem na ponta (y perto de `length`), o que gera NaN numa potência fracionária.
    half_width = width_ratio * length * np.maximum(np.sin(np.pi * y / length), 0.0) ** shape_power
    left = np.column_stack([-half_width, y, np.zeros_like(y)])  # base -> ponta, lado esquerdo
    right = np.column_stack([half_width[::-1], y[::-1], np.zeros_like(y)])  # ponta -> base, lado direito
    # left[0] e right[-1] sao ambos a base; left[-1] e right[0] sao ambos a ponta.
    outline = np.vstack([left, right[1:-1]])

    n = len(outline)
    faces = []
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])  # frente (leque a partir da base, vértice 0)
        faces.append([0, i + 1, i])  # verso, pra ficar visível dos dois lados
    return outline, np.array(faces, dtype=int)


def place_leaf(local_vertices, attach_point, branch_tangent, twist=0.0, droop_deg=20.0):
    """Leva os vértices locais de uma folha (planas, base na origem, ponta
    em +y) para o espaço 3D, presos em `attach_point`, apontando para fora
    do galho `branch_tangent`, com giro `twist` ao redor do galho e uma
    leve queda `droop_deg` (efeito da gravidade).
    """
    tangent_vec = branch_tangent / np.linalg.norm(branch_tangent)
    up = np.array([0.0, 0.0, 1.0]) if abs(tangent_vec[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(up, tangent_vec)
    u = u / np.linalg.norm(u)
    v = np.cross(tangent_vec, u)

    out_dir = np.cos(twist) * u + np.sin(twist) * v
    droop = np.radians(droop_deg)
    leaf_y = out_dir * np.cos(droop) - tangent_vec * np.sin(droop)
    leaf_y = leaf_y / np.linalg.norm(leaf_y)
    leaf_x = np.cross(leaf_y, tangent_vec)
    leaf_x = leaf_x / np.linalg.norm(leaf_x)

    world = attach_point + local_vertices[:, 0:1] * leaf_x + local_vertices[:, 1:2] * leaf_y
    return world


def flower_bloom_mesh(n_petals=6, radius=0.12, n1=0.3, n2=1.7, n3=1.7, n_points=120):
    """Malha plana de uma flor vista de cima, no plano XY local, centrada na
    origem: a silhueta vem da Superfórmula de Gielis (Eq. 5.8) com
    `m=2*n_petals`, que dá `n_petals` lóbulos/pétalas em volta do centro.
    """
    theta = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    rho = radius * superformula.superformula(theta, m=2 * n_petals, n1=n1, n2=n2, n3=n3)
    x, y = superformula.to_cartesian(theta, rho)
    outline = np.column_stack([x, y, np.zeros_like(x)])

    center_idx = n_points
    vertices = np.vstack([outline, [[0.0, 0.0, 0.0]]])
    faces = []
    for i in range(n_points):
        j = (i + 1) % n_points
        faces.append([center_idx, i, j])
        faces.append([center_idx, j, i])
    return vertices, np.array(faces, dtype=int)


def cap_mesh(radius=0.06, height=0.03, n_sides=16, cross_section_n=2.5):
    """Malha do chapéu de um cogumelo: uma cúpula rasa cuja borda segue uma
    curva de Lamé (Eq. 4.1/5.1) — `cross_section_n` maior dá uma borda mais
    "angular", menor dá uma borda mais estrelada.
    """
    phi = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
    rim_shape = lame.lame_polar_radius(phi, A=1.0, B=1.0, n=cross_section_n)
    rim = np.column_stack(
        [radius * rim_shape * np.cos(phi), radius * rim_shape * np.sin(phi), np.zeros(n_sides)]
    )
    top_idx = n_sides
    vertices = np.vstack([rim, [[0.0, 0.0, height]]])
    faces = []
    for i in range(n_sides):
        j = (i + 1) % n_sides
        faces.append([i, j, top_idx])
    return vertices, np.array(faces, dtype=int)
