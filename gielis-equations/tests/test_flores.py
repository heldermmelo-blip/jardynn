import math
import os
import random

import numpy as np
import pytest

from gielis.plants import ESPECIES_FLORES, PALETAS, SPECIES, flowers, generate_plant
from gielis.plants.mesh_utils import write_obj


def _linhas_v(path):
    with open(path) as f:
        return [line.split()[1:] for line in f if line.startswith("v ")]


def _gerar(tmp_path, especie, seed):
    path, _ = generate_plant(random.Random(seed), especie, out_path=os.path.join(tmp_path, f"{especie}_{seed}.obj"))
    return path


def test_there_are_nine_flower_species_all_registered():
    assert len(ESPECIES_FLORES) == 9 and set(ESPECIES_FLORES) <= set(SPECIES)
    assert len(SPECIES) == len(set(SPECIES)) >= 23
    assert set(PALETAS) == set(ESPECIES_FLORES)


@pytest.mark.parametrize("especie", ESPECIES_FLORES)
def test_flowers_carry_vertex_colors_with_green_and_bloom(tmp_path, especie):
    cores = {tuple(round(float(c), 2) for c in v[3:6]) for v in _linhas_v(_gerar(tmp_path, especie, 1))}
    assert all(len(v) == 6 for v in _linhas_v(_gerar(tmp_path, especie, 1)))
    assert len(cores) >= (1 if especie == "nenufar" else 2)  # haste/folha e corola (o nenúfar às vezes é só a folha)
    verdes = [c for c in cores if c[1] > c[0] and c[1] > c[2]]
    assert verdes, "toda flor tem haste ou folha verde"


def test_non_flowers_keep_plain_obj_vertices(tmp_path):
    for especie in ("arvore", "cacto_coluna", "palmeira"):
        assert all(len(v) == 3 for v in _linhas_v(_gerar(tmp_path, especie, 1)))


def test_each_flower_gets_its_own_color_within_the_species_palette():
    for especie in ESPECIES_FLORES:
        cores = [flowers.sortear_cor(random.Random(s), especie) for s in range(60)]
        assert len({tuple(round(c, 2) for c in cor) for cor in cores}) > 20  # nenhuma igual à outra
        for cor in cores:
            assert any(all(abs(a - b) <= 0.0501 for a, b in zip(cor, base)) for base in PALETAS[especie])


def test_same_seed_same_flower_different_seed_different_color(tmp_path):
    a = open(_gerar(tmp_path, "rosa", 5)).read()
    assert a == open(_gerar(tmp_path, "rosa", 5)).read()
    cores = set()
    for seed in range(12):
        cores |= {tuple(v[3:6]) for v in _linhas_v(_gerar(tmp_path, "tulipa", seed))}
    assert len(cores) > 15


def test_petal_ring_has_requested_tip_radius_and_petal_count():
    for petalas in (3, 5, 8, 13, 21):
        v, _ = flowers.anel_de_petalas(0.2, petalas, 1.0, 4.0, 4.0, 0.0)
        r = np.hypot(v[:-1, 0], v[:-1, 1])  # sem o vértice central
        assert r.max() == pytest.approx(0.2, abs=1e-6)
        picos = sum(1 for i in range(len(r)) if r[i] > r[i - 1] and r[i] >= r[(i + 1) % len(r)] and r[i] > 0.9 * r.max())
        assert picos == petalas


def test_layered_blooms_have_more_layers_for_roses_and_dahlias_than_for_daisies(tmp_path):
    def n_vertices(especie):
        return len(_linhas_v(_gerar(tmp_path, especie, 2)))

    assert n_vertices("dalia") > n_vertices("margarida") * 1.5
    assert n_vertices("rosa") > n_vertices("tulipa")


def test_obj_without_colors_is_unchanged_and_mixed_parts_get_a_gray(tmp_path):
    tri = (np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]), np.array([[0, 1, 2]]))
    sem = os.path.join(tmp_path, "sem.obj")
    write_obj(sem, [tri])
    assert all(len(v) == 3 for v in _linhas_v(sem))
    mista = os.path.join(tmp_path, "mista.obj")
    write_obj(mista, [tri, (*tri, (1.0, 0.0, 0.0))])
    linhas = _linhas_v(mista)
    assert all(len(v) == 6 for v in linhas)
    assert [float(c) for c in linhas[0][3:]] == [0.8, 0.8, 0.8] and [float(c) for c in linhas[3][3:]] == [1.0, 0.0, 0.0]


def test_sunflower_is_taller_than_daisy_and_lavender_has_many_spikes(tmp_path):
    def altura(especie):
        ys = [float(v[1]) for v in _linhas_v(_gerar(tmp_path, especie, 3))]
        return max(ys) - min(ys)

    assert altura("girassol") > 0.8 > altura("margarida")
    assert len(_linhas_v(_gerar(tmp_path, "lavanda", 3))) > 500
