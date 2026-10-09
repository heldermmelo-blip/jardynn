import math
import os
import random

import numpy as np
import pytest

from gielis.plants import ESPECIES_L, GRAMATICAS, SPECIES, generate_plant
from gielis.plants import lsystem


def _altura_e_raio(path):
    pts = np.array([[float(c) for c in line.split()[1:4]] for line in open(path) if line.startswith("v ")])
    return pts[:, 1].max() - pts[:, 1].min(), np.hypot(pts[:, 0], pts[:, 2]).max()


def test_five_grammars_registered_as_species():
    assert set(ESPECIES_L) == {"carvalho", "salgueiro", "pinheiro", "araucaria", "dracena_dragao"}
    assert set(ESPECIES_L) <= set(SPECIES) and len(SPECIES) == len(set(SPECIES))


def test_rewriting_is_stochastic_but_deterministic_per_seed():
    g = GRAMATICAS["carvalho"]
    a = lsystem.reescrever(random.Random(1), g, 4)
    assert a == lsystem.reescrever(random.Random(1), g, 4)
    assert len({lsystem.reescrever(random.Random(s), g, 4) for s in range(12)}) > 6
    assert "A" not in a and "B" not in a  # brotos viram folhagem no fim


def test_string_grows_with_iterations():
    g = GRAMATICAS["pinheiro"]
    tamanhos = [len(lsystem.reescrever(random.Random(2), g, n)) for n in (1, 3, 5, 7)]
    assert tamanhos == sorted(tamanhos) and tamanhos[-1] > tamanhos[0] * 4


def test_turtle_draws_branches_that_taper_and_start_at_the_ground():
    g = GRAMATICAS["carvalho"]
    cadeia = lsystem.reescrever(random.Random(3), g, 5)
    segmentos, pontas = lsystem.interpretar(random.Random(3), cadeia, g)
    assert len(segmentos) > 30 and pontas
    assert all(s["r1"] <= s["r0"] for s in segmentos)
    assert segmentos[0]["start"].tolist() == [0.0, 0.0, 0.0]
    assert max(s["end"][2] for s in segmentos) > 3.0  # sobe


def test_turtle_brackets_restore_state():
    g = dict(GRAMATICAS["carvalho"], tropismo=((0, 0, 1), 0.0))
    seg, _ = lsystem.interpretar(random.Random(0), "F[&F]F", g)
    # o segundo F do tronco continua de onde o primeiro parou, não do ramo
    assert np.allclose(seg[2]["start"], seg[0]["end"])
    assert seg[1]["end"][2] < seg[2]["end"][2]


def test_dragon_tree_forks_in_two_every_node():
    g = GRAMATICAS["dracena_dragao"]
    for n in (3, 4, 5):
        cadeia = lsystem.reescrever(random.Random(0), g, n)
        seg, pontas = lsystem.interpretar(random.Random(0), cadeia, g)
        assert len(pontas) == 2**n and all(t == "R" for _, _, t in pontas)  # bifurcação dicotômica, roseta em cada ponta


def test_willow_droops_and_oak_does_not(tmp_path):
    def inclinacao_media(nome):
        g = GRAMATICAS[nome]
        seg, _ = lsystem.interpretar(random.Random(4), lsystem.reescrever(random.Random(4), g, 5), g)
        folhas = [s for s in seg if s["depth"] >= 3]
        return np.mean([(s["end"][2] - s["start"][2]) / np.linalg.norm(s["end"] - s["start"]) for s in folhas])

    assert inclinacao_media("salgueiro") < inclinacao_media("carvalho") - 0.2


def test_monkey_puzzle_is_taller_than_wide_with_bare_lower_trunk(tmp_path):
    path, seg = generate_plant(random.Random(1), "araucaria", out_path=os.path.join(tmp_path, "a.obj"))
    h, r = _altura_e_raio(path)
    assert h > 6.0 and r < h * 0.4
    ramos = [s for s in seg if s["depth"] >= 1]
    assert min(s["start"][2] for s in ramos) > h * 0.2  # nada de galho nos primeiros metros


@pytest.mark.parametrize("nome", ESPECIES_L)
def test_meshes_are_reasonable_in_size_and_deterministic(tmp_path, nome):
    a, _ = generate_plant(random.Random(7), nome, out_path=os.path.join(tmp_path, "a.obj"))
    b, _ = generate_plant(random.Random(7), nome, out_path=os.path.join(tmp_path, "b.obj"))
    assert open(a).read() == open(b).read()
    h, r = _altura_e_raio(a)
    lo, hi = GRAMATICAS[nome]["altura"]
    assert lo * 0.85 < h < hi * 1.2 and r < hi
    assert os.path.getsize(a) < 4_000_000


def test_height_varies_from_sapling_to_veteran_and_follows_the_request(tmp_path):
    for nome in ESPECIES_L:
        lo, hi = GRAMATICAS[nome]["altura"]
        alturas = [lsystem.sortear_altura(random.Random(s), nome) for s in range(300)]
        assert min(alturas) >= lo and max(alturas) <= hi
        assert max(alturas) - min(alturas) > (hi - lo) * 0.7  # de muda a veterana
        assert sum(alturas) / len(alturas) < (lo + hi) / 2 + 0.1 * (hi - lo)  # mais adultas que veteranas
    for pedida in (5.0, 12.0, 20.0):
        path, _ = generate_plant(random.Random(2), "carvalho", out_path=os.path.join(tmp_path, "c.obj"))
        partes, seg = lsystem.gerar_arvore_l(random.Random(2), "carvalho", altura=pedida)
        assert max(s["end"][2] for s in seg) == pytest.approx(pedida, rel=0.02)
    assert os.path.getsize(path) > 0


def test_mesh_weight_does_not_grow_with_tree_height(tmp_path):
    def peso(altura):
        partes, _ = lsystem.gerar_arvore_l(random.Random(5), "pinheiro", altura=altura)
        return sum(len(v) for v, *_ in partes)

    # a geometria é a mesma; só o galho que engrossa ganha mais lados
    assert peso(9.0) <= peso(26.0) <= peso(9.0) * 1.6
