import os
import random

from gielis.plants import SPECIES, generate_plant


def test_all_species_generate_nonempty_mesh(tmp_path):
    for species in SPECIES:
        rng = random.Random(0)
        out_path = os.path.join(tmp_path, f"{species}.obj")
        path, skeleton = generate_plant(rng, species, out_path=out_path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
        assert len(skeleton) >= 1


def test_same_seed_is_deterministic(tmp_path):
    for species in SPECIES:
        path_a = os.path.join(tmp_path, f"{species}_a.obj")
        path_b = os.path.join(tmp_path, f"{species}_b.obj")
        generate_plant(random.Random(7), species, out_path=path_a)
        generate_plant(random.Random(7), species, out_path=path_b)
        with open(path_a) as f:
            content_a = f.read()
        with open(path_b) as f:
            content_b = f.read()
        assert content_a == content_b


def test_unknown_species_raises():
    try:
        generate_plant(random.Random(0), "planta_inexistente")
    except ValueError:
        pass
    else:
        raise AssertionError("esperava ValueError para espécie desconhecida")


def test_greenhouse_species_exist_and_have_plausible_sizes(tmp_path):
    novas = ("cacto_coluna", "cacto_barril", "agave", "palmeira", "folha_larga", "cipreste", "topiaria")
    assert all(n in SPECIES for n in novas)
    for species in novas:
        for seed in range(5):
            path, _ = generate_plant(random.Random(seed), species, out_path=os.path.join(tmp_path, f"{species}.obj"))
            with open(path) as f:
                pts = [[float(c) for c in line.split()[1:4]] for line in f if line.startswith("v ")]
            assert len(pts) > 20
            xs, ys, zs = zip(*pts)  # o .obj sai em Y para cima (Godot)
            assert 0.15 <= max(ys) - min(ys) <= 3.2  # nem pó, nem gigante
            assert max(max(map(abs, xs)), max(map(abs, zs))) < 1.5
