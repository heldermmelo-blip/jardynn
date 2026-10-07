import os
import random

import numpy as np
import pytest

from gielis.structures import generate_greenhouse, generate_gazebo, generate_tower


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


@pytest.mark.parametrize("sides", [3, 4, 5])
def test_greenhouse_builds_for_each_floorplan(tmp_path, sides):
    path, skeleton = generate_greenhouse(
        random.Random(2), sides=sides, n_floors=1, radius=4.0, out_path=os.path.join(tmp_path, f"g{sides}.obj")
    )
    assert os.path.getsize(path) > 0
    assert len(skeleton) > sides  # postes + vigas + telhado


def test_more_floors_means_more_beams_and_taller_posts(tmp_path):
    _, one = generate_greenhouse(random.Random(3), sides=5, n_floors=1, out_path=os.path.join(tmp_path, "a.obj"))
    _, three = generate_greenhouse(random.Random(3), sides=5, n_floors=3, out_path=os.path.join(tmp_path, "b.obj"))
    assert len(three) > len(one)
    tallest_one = max(seg["end"][2] for seg in one)
    tallest_three = max(seg["end"][2] for seg in three)
    assert tallest_three > tallest_one


def test_bigger_radius_means_wider_greenhouse(tmp_path):
    _, small = generate_greenhouse(random.Random(4), sides=3, radius=3.0, out_path=os.path.join(tmp_path, "s.obj"))
    _, big = generate_greenhouse(random.Random(4), sides=3, radius=6.0, out_path=os.path.join(tmp_path, "b.obj"))
    assert max(abs(seg["start"][0]) for seg in big) > max(abs(seg["start"][0]) for seg in small)


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
