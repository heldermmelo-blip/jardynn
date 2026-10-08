import os
import random

import numpy as np
import pytest

from gielis.structures import generate_gazebo, generate_tower, generate_tower_vines


def _vertex_count(path):
    with open(path) as f:
        return sum(1 for line in f if line.startswith("v "))


def test_tower_has_one_segment_per_floor(tmp_path):
    for n_floors in (3, 5, 8):
        path, skeleton = generate_tower(random.Random(1), n_floors, out_path=os.path.join(tmp_path, f"t{n_floors}.obj"))
        assert len(skeleton) == n_floors
        assert os.path.getsize(path) > 0


def _vertices(path):
    with open(path) as f:
        return np.array([[float(c) for c in line.split()[1:4]] for line in f if line.startswith("v ")])


def test_tower_is_hollow_and_wide_enough_to_enter(tmp_path):
    path, _ = generate_tower(random.Random(2), 5, out_path=os.path.join(tmp_path, "t.obj"))
    v = _vertices(path)  # .obj é Y-up: o plano horizontal é (x, z)
    radii = np.hypot(v[:, 0], v[:, 2])
    assert radii.max() >= 2.5  # ~6 m de largura: cabe um aventureiro com folga
    assert (radii < 1.3).any()  # escada e mastro no vão central
    # Paredes só na borda: não há vértices de parede entre o poço e a parede.
    assert not ((radii > 1.9) & (radii < 2.5) & (v[:, 1] > 0.5) & (v[:, 1] < 2.0)).any()


def _faces_centroids(path):
    with open(path) as f:
        lines = f.read().splitlines()
    verts = np.array([[float(c) for c in line.split()[1:4]] for line in lines if line.startswith("v ")])
    faces = [[int(t) - 1 for t in line.split()[1:4]] for line in lines if line.startswith("f ")]
    return np.array([verts[face].mean(axis=0) for face in faces])


def test_tower_ground_floor_has_exactly_one_door_opening(tmp_path):
    path, _ = generate_tower(random.Random(3), 3, out_path=os.path.join(tmp_path, "t.obj"))
    c = _faces_centroids(path)  # .obj é Y-up: horizontal = (x, z), altura = y
    radii = np.hypot(c[:, 0], c[:, 2])
    angles = np.arctan2(c[:, 2], c[:, 0]) % (2 * np.pi)
    setor = np.floor(angles / (2 * np.pi) * 16).astype(int) % 16
    parede_baixa = (radii > 2.5) & (c[:, 1] < 1.2)  # faces de parede junto ao chão do térreo
    assert len(set(setor[parede_baixa])) == 15  # 16 setores menos o da porta


def test_tower_upper_floors_have_window_openings(tmp_path):
    path, _ = generate_tower(random.Random(4), 4, out_path=os.path.join(tmp_path, "t.obj"))
    c = _faces_centroids(path)
    radii = np.hypot(c[:, 0], c[:, 2])
    angles = np.arctan2(c[:, 2], c[:, 0]) % (2 * np.pi)
    setor = np.floor(angles / (2 * np.pi) * 16).astype(int) % 16
    # No meio do 2º andar (y ~ 3.4 + 1.65), as janelas deixam setores sem parede.
    meio = (radii > 2.5) & (c[:, 1] > 3.4 + 1.2) & (c[:, 1] < 3.4 + 2.2)
    assert len(set(setor[meio])) < 16


def test_taller_tower_has_more_vertices(tmp_path):
    short, _ = generate_tower(random.Random(1), 3, out_path=os.path.join(tmp_path, "short.obj"))
    tall, _ = generate_tower(random.Random(1), 8, out_path=os.path.join(tmp_path, "tall.obj"))
    assert _vertex_count(tall) > _vertex_count(short)


def test_gazebo_builds_and_is_deterministic(tmp_path):
    path_a, skel_a = generate_gazebo(random.Random(5), out_path=os.path.join(tmp_path, "a.obj"))
    path_b, skel_b = generate_gazebo(random.Random(5), out_path=os.path.join(tmp_path, "b.obj"))
    assert os.path.getsize(path_a) > 0
    assert len(skel_a) == len(skel_b)
    with open(path_a) as fa, open(path_b) as fb:
        assert fa.read() == fb.read()


def test_tower_skeleton_exposes_floor_radii_and_door_angle(tmp_path):
    _, skeleton = generate_tower(random.Random(5), 8, out_path=os.path.join(tmp_path, "t.obj"))
    radii = [seg["r0"] for seg in skeleton]
    assert radii == sorted(radii, reverse=True)  # afunila pra cima
    assert all(r - 1.3 >= 1.0 for r in radii)  # sobra >= 1 m de piso em anel até no último andar
    assert 0.0 <= skeleton[0]["porta_angulo"] < 2 * np.pi


def test_tower_without_roof_is_open_on_top_with_a_soil_floor(tmp_path):
    with_roof, _ = generate_tower(random.Random(6), 4, out_path=os.path.join(tmp_path, "a.obj"), roof=True)
    open_top, skeleton = generate_tower(random.Random(6), 4, out_path=os.path.join(tmp_path, "b.obj"), roof=False)
    total = skeleton[0]["altura_total"]
    assert _vertices(with_roof)[:, 1].max() > total + 2.0  # telhado cônico
    assert total <= _vertices(open_top)[:, 1].max() <= total + 0.3  # só a cornija passa do topo
    assert skeleton[0]["raio_topo"] > 2.0
    piso_de_terra = np.isclose(_vertices(open_top)[:, 1], total - 0.08)
    assert piso_de_terra.sum() > 10


def test_tower_vines_hug_the_outer_wall_and_climb(tmp_path):
    _, skeleton = generate_tower(random.Random(7), 5, out_path=os.path.join(tmp_path, "t.obj"))
    path, hastes = generate_tower_vines(random.Random(8), skeleton, out_path=os.path.join(tmp_path, "v.obj"))
    v = _vertices(path)  # .obj é Y-up
    zs = [float(seg["start"][2]) for seg in skeleton] + [float(skeleton[-1]["end"][2])]
    rs = [float(seg["r0"]) for seg in skeleton] + [float(skeleton[-1]["r1"])]
    raio_parede = np.interp(v[:, 1], zs, rs)
    raio = np.hypot(v[:, 0], v[:, 2])
    assert (raio >= raio_parede - 0.05).all()  # nunca atravessa a parede pra dentro
    assert (raio <= raio_parede + 1.0).all()  # rente à parede
    assert v[:, 1].max() > 0.3 * zs[-1]  # sobe de verdade
    assert 3 <= len(hastes) <= 6


def test_tower_vines_are_deterministic(tmp_path):
    _, skeleton = generate_tower(random.Random(7), 4, out_path=os.path.join(tmp_path, "t.obj"))
    a, _ = generate_tower_vines(random.Random(9), skeleton, out_path=os.path.join(tmp_path, "a.obj"))
    b, _ = generate_tower_vines(random.Random(9), skeleton, out_path=os.path.join(tmp_path, "b.obj"))
    with open(a) as fa, open(b) as fb:
        assert fa.read() == fb.read()
