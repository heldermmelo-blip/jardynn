"""Utilitários geométricos genéricos: base ortonormal, rotação de Rodrigues,
tubo com seção transversal de Lamé (Eq. 4.1/5.1), e exportação .obj.

Extraído de `examples/rpg_plant.py` para ser reaproveitado por várias
espécies de planta.
"""

import numpy as np

from .. import lame


def orthonormal_basis(tangent):
    """Dois vetores unitários perpendiculares a `tangent`, formando uma base
    local (tangent, u, v)."""
    tangent = tangent / np.linalg.norm(tangent)
    # Escolhe um "cima" de referência que não seja quase paralelo à tangente,
    # senão o produto vetorial degenera (Z, salvo quando a tangente é quase vertical).
    up = np.array([0.0, 0.0, 1.0]) if abs(tangent[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(up, tangent)
    u = u / np.linalg.norm(u)
    v = np.cross(tangent, u)
    return u, v


def rotate_around_axis(vector, axis, angle):
    """Rotaciona `vector` em torno de `axis` por `angle` radianos (fórmula
    de Rodrigues)."""
    axis = axis / np.linalg.norm(axis)
    return (
        vector * np.cos(angle)
        + np.cross(axis, vector) * np.sin(angle)
        + axis * np.dot(axis, vector) * (1 - np.cos(angle))
    )


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
    u, v = orthonormal_basis(tangent_vec)

    phi = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
    shape = lame.lame_polar_radius(phi, A=1.0, B=1.0, n=cross_section_n)
    cx, cy = shape * np.cos(phi), shape * np.sin(phi)

    # Dois anéis de n_sides vértices no plano (u, v) perpendicular ao eixo do
    # segmento: o primeiro em `start` (raio r0), o segundo em `end` (raio r1).
    ring_start = start + r0 * (np.outer(cx, u) + np.outer(cy, v))
    ring_end = end + r1 * (np.outer(cx, u) + np.outer(cy, v))
    vertices = np.vstack([ring_start, ring_end])

    faces = []
    for i in range(n_sides):
        j = (i + 1) % n_sides  # fecha o anel: o último lado volta ao vértice 0
        # Cada lado do tubo é um quadrilátero (a, b, c, d) dividido em 2 triângulos.
        a, b, c, d = i, j, n_sides + j, n_sides + i
        faces.append([a, b, c])
        faces.append([a, c, d])
    return vertices, np.array(faces, dtype=int)


def write_obj(path, parts):
    """`parts` é uma lista de (vertices Nx3, faces Mx3) já em coordenadas
    mundiais, no eixo de crescimento Z (convenção do esqueleto em
    `skeleton.py`, `direction=(0, 0, 1)`). Escreve um único .obj combinando
    todas as partes, remapeando Z-up (interno) para Y-up (convenção de
    motores de jogo como o Godot) via rotação de -90° em X: (x, y, z) ->
    (x, z, -y) — uma rotação própria, preserva o sentido das faces.

    Uma parte pode ser (vertices, faces, (r, g, b)): a cor (0..1) vai como
    cor de vértice (`v x y z r g b`), que o Godot importa e usa com
    `vertex_color_use_as_albedo`. Se alguma parte tem cor, as sem cor saem
    cinza-claro, pra todos os vértices terem cor. Sem nenhuma cor, o arquivo
    é o de sempre (`v x y z`).

    Tudo vai num único objeto (`o`): o importador de .obj do Godot cria uma
    superfície por objeto, e o limite é 256 — uma árvore com folhas passa
    disso e perdia partes na importação."""
    coloridas = any(len(parte) > 2 and parte[2] is not None for parte in parts)
    with open(path, "w") as f:
        f.write("o mesh\n")
        offset = 0
        for parte in parts:
            vertices, faces = parte[0], parte[1]
            if len(vertices) == 0:
                continue
            cor = None
            if coloridas:
                cor = parte[2] if len(parte) > 2 and parte[2] is not None else (0.8, 0.8, 0.8)
            for vx, vy, vz in vertices:
                sufixo = f" {cor[0]:.3f} {cor[1]:.3f} {cor[2]:.3f}" if cor is not None else ""
                f.write(f"v {vx:.6f} {vz:.6f} {-vy:.6f}{sufixo}\n")
            for face in faces:
                a, b, c = face + offset + 1  # .obj é indexado a partir de 1
                f.write(f"f {a} {b} {c}\n")
            offset += len(vertices)
