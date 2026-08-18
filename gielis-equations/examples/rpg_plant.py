"""Gerador procedural de plantas para uso em jogos (ex. RPG): ramificação +
folhas, exportado como malha 3D em .obj.

Isto NÃO é uma equação do livro — é uma aplicação construída EM CIMA da
biblioteca `gielis`: a seção transversal do tronco/galhos usa curvas de
Lamé (Eq. 4.1/5.1, o "bambu quadrado" citado no livro). O contorno das
folhas usa um perfil próprio (ver `leaf_mesh`), não a Eq. 10.1 do livro —
a extração do PDF deixou ambíguo o expoente interno daquela equação, e as
leituras possíveis geram curvas degeneradas para os valores de n citados no
livro; ver o comentário em `leaf_mesh` e a nota em EQUATIONS.md. A
ramificação em si (quantos galhos, ângulos, afinamento) é um algoritmo
procedural comum, sem relação com uma equação específica do livro.

Uso:
    python examples/rpg_plant.py
"""

import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gielis import lame

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


# ---------------------------------------------------------------------------
# Geometria auxiliar (não são equações do livro, só matemática de suporte)
# ---------------------------------------------------------------------------


def _orthonormal_basis(tangent):
    """Dois vetores unitários perpendiculares a `tangent`, formando uma base
    local (tangent, u, v)."""
    tangent = tangent / np.linalg.norm(tangent)
    up = np.array([0.0, 0.0, 1.0]) if abs(tangent[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(up, tangent)
    u = u / np.linalg.norm(u)
    v = np.cross(tangent, u)
    return u, v


def _rotate_around_axis(vector, axis, angle):
    """Rotaciona `vector` em torno de `axis` por `angle` radianos (fórmula
    de Rodrigues)."""
    axis = axis / np.linalg.norm(axis)
    return (
        vector * np.cos(angle)
        + np.cross(axis, vector) * np.sin(angle)
        + axis * np.dot(axis, vector) * (1 - np.cos(angle))
    )


# ---------------------------------------------------------------------------
# Esqueleto de galhos (ramificação procedural)
# ---------------------------------------------------------------------------


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

    n_branches = branches_per_node if depth > 0 else rng.choice([2, 3])
    branch_angle = np.radians(branch_angle_deg)
    for i in range(n_branches):
        twist = 2 * np.pi * i / n_branches + rng.uniform(-0.3, 0.3)
        u, v = _orthonormal_basis(direction)
        tilt_axis = np.cos(twist) * u + np.sin(twist) * v
        new_dir = _rotate_around_axis(direction, tilt_axis, branch_angle * rng.uniform(0.7, 1.3))
        new_dir = new_dir + np.array([0.0, 0.0, 0.15])  # fototropismo simplificado
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
        )
    return segments


# ---------------------------------------------------------------------------
# Malha do tronco/galhos (tubo com seção transversal de Lamé, Eq. 4.1/5.1)
# ---------------------------------------------------------------------------


def tube_mesh(segment, n_sides=10, cross_section_n=2.0):
    """Vértices e faces (triângulos) de um tubo entre segment['start'] e
    segment['end'], com raio r0 no início e r1 no fim. A seção transversal é
    uma curva de Lamé (Eq. 4.1/5.1): n=2 dá um tubo circular, n<2 dá uma
    seção mais "quadrada" (o efeito de bambu quadrado do Cap. 4).
    """
    start, end = segment["start"], segment["end"]
    r0, r1 = segment["r0"], segment["r1"]
    tangent_vec = end - start
    length = np.linalg.norm(tangent_vec)
    if length < 1e-9:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=int)
    tangent_vec = tangent_vec / length
    u, v = _orthonormal_basis(tangent_vec)

    phi = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
    shape = lame.lame_polar_radius(phi, A=1.0, B=1.0, n=cross_section_n)
    cx, cy = shape * np.cos(phi), shape * np.sin(phi)

    ring_start = start + r0 * (np.outer(cx, u) + np.outer(cy, v))
    ring_end = end + r1 * (np.outer(cx, u) + np.outer(cy, v))
    vertices = np.vstack([ring_start, ring_end])

    faces = []
    for i in range(n_sides):
        j = (i + 1) % n_sides
        a, b, c, d = i, j, n_sides + j, n_sides + i
        faces.append([a, b, c])
        faces.append([a, c, d])
    return vertices, np.array(faces, dtype=int)


# ---------------------------------------------------------------------------
# Folha (perfil próprio — ver aviso em leaf_mesh sobre a Eq. 10.1)
# ---------------------------------------------------------------------------


def leaf_mesh(shape_power=2.5, length=0.3, width_ratio=0.35, n_points=24):
    """Malha plana (dupla face) de uma folha, no plano XY local, com a base
    (ponto de fixação no galho) na origem e a ponta no eixo +y.

    NÃO usa a Eq. 10.1 do livro diretamente: ao revisar este código,
    percebi que a extração do PDF deixou ambíguo se o expoente interno
    daquela equação é fixo (4) ou é o próprio parâmetro de forma n — e para
    os valores de n citados no livro (0.02 a 0.1), as duas leituras
    possíveis geram curvas degeneradas (uma explode perto do infinito, a
    outra colapsa perto de zero), não uma silhueta de folha utilizável.

    Em vez disso, usa um perfil direto e sempre bem-comportado: a
    meia-largura em função da altura y (de 0 até `length`) é
    `width_ratio*length*sin(pi*y/length)^shape_power` — zero na base e na
    ponta, máxima no meio. `shape_power` maior dá uma folha mais fina e
    pontiaguda (lanceolada); menor dá uma folha mais arredondada.
    """
    y = np.linspace(0.0, length, n_points)
    half_width = width_ratio * length * np.sin(np.pi * y / length) ** shape_power
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
    u, v = _orthonormal_basis(tangent_vec)
    out_dir = np.cos(twist) * u + np.sin(twist) * v
    droop = np.radians(droop_deg)
    leaf_y = out_dir * np.cos(droop) - tangent_vec * np.sin(droop)
    leaf_y = leaf_y / np.linalg.norm(leaf_y)
    leaf_x = np.cross(leaf_y, tangent_vec)
    leaf_x = leaf_x / np.linalg.norm(leaf_x)

    world = attach_point + local_vertices[:, 0:1] * leaf_x + local_vertices[:, 1:2] * leaf_y
    return world


# ---------------------------------------------------------------------------
# Exportação .obj
# ---------------------------------------------------------------------------


def write_obj(path, parts):
    """`parts` é uma lista de (vertices Nx3, faces Mx3) já em coordenadas
    mundiais. Escreve um único arquivo .obj combinando todas as partes."""
    with open(path, "w") as f:
        offset = 0
        for idx, (vertices, faces) in enumerate(parts):
            if len(vertices) == 0:
                continue
            f.write(f"o part_{idx}\n")
            for vx, vy, vz in vertices:
                f.write(f"v {vx:.6f} {vy:.6f} {vz:.6f}\n")
            for face in faces:
                a, b, c = face + offset + 1  # .obj é indexado a partir de 1
                f.write(f"f {a} {b} {c}\n")
            offset += len(vertices)


# ---------------------------------------------------------------------------
# Montagem da planta completa
# ---------------------------------------------------------------------------


def generate_plant(seed=0, max_depth=4, out_path=None):
    """Gera uma planta completa (tronco + galhos + folhas nas pontas) e
    salva em `out_path` (padrão: examples/output/plant.obj)."""
    rng = random.Random(seed)
    skeleton = generate_skeleton(rng, max_depth=max_depth)

    parts = []
    for seg in skeleton:
        cross_n = 1.4 if seg["depth"] == 0 else 2.0
        parts.append(tube_mesh(seg, n_sides=10, cross_section_n=cross_n))

        if seg["depth"] >= max_depth - 1:
            tangent_vec = seg["end"] - seg["start"]
            n_leaves = rng.randint(2, 4)
            for k in range(n_leaves):
                twist = 2 * np.pi * k / n_leaves + rng.uniform(-0.4, 0.4)
                shape_power = rng.uniform(1.8, 3.5)
                leaf_len = rng.uniform(0.18, 0.32)
                local_v, local_f = leaf_mesh(shape_power=shape_power, length=leaf_len)
                world_v = place_leaf(local_v, seg["end"], tangent_vec, twist=twist, droop_deg=rng.uniform(10, 35))
                parts.append((world_v, local_f))

    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, "plant.obj")
    write_obj(out_path, parts)
    return out_path, skeleton


def plot_skeleton_preview(skeleton, out_name="plant_skeleton_preview.png"):
    """Pré-visualização rápida (wireframe) do esqueleto de galhos, útil pra
    conferir a estrutura antes de abrir o .obj num programa 3D."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    for seg in skeleton:
        s, e = seg["start"], seg["end"]
        ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color="tab:green", linewidth=max(0.5, 4 * seg["r0"]))
    ax.set_title("Pré-visualização do esqueleto da planta")
    ax.set_box_aspect([1, 1, 1.4])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUTPUT_DIR, out_name), dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    path, skeleton = generate_plant(seed=42, max_depth=4)
    print(f"planta gerada: {path} ({len(skeleton)} segmentos)")
    plot_skeleton_preview(skeleton)
    print(f"pré-visualização salva em: {os.path.join(OUTPUT_DIR, 'plant_skeleton_preview.png')}")
