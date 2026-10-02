import os
import random

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
