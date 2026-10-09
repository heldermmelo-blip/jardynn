import os
import random

import numpy as np
import pytest

from gielis.plants import ARVORES_EXOTICAS, ESPECIES_EXOTICAS, SPECIES, generate_plant
from gielis.plants import exoticas


def _linhas(path):
    return [line.split()[1:] for line in open(path) if line.startswith("v ")]


def _pts(path):
    return np.array([[float(c) for c in v[:3]] for v in _linhas(path)])


def _gerar(tmp_path, especie, seed=1, **kw):
    path, seg = generate_plant(random.Random(seed), especie, out_path=os.path.join(tmp_path, f"{especie}_{seed}.obj"), **kw)
    return path, seg


def test_six_exotic_species_are_registered():
    assert set(ESPECIES_EXOTICAS) == {"baoba", "samambaia_arborea", "cica", "nepentes", "vitoria_regia", "flor_cadaver"}
    assert set(ESPECIES_EXOTICAS) <= set(SPECIES)
    assert set(ARVORES_EXOTICAS) == {"baoba", "samambaia_arborea", "cica"}


@pytest.mark.parametrize("especie", ESPECIES_EXOTICAS)
def test_every_species_builds_a_deterministic_nonempty_mesh(tmp_path, especie):
    a, seg = _gerar(tmp_path, especie, 3)
    b, _ = _gerar(tmp_path, especie, 3)
    assert open(a).read() == open(b).read() and len(seg) >= 1
    assert len(_pts(a)) > 50 and os.path.getsize(a) < 1_500_000


@pytest.mark.parametrize("especie", ("samambaia_arborea", "cica", "nepentes", "vitoria_regia", "flor_cadaver"))
def test_colored_species_carry_vertex_colors_with_green_in_them(tmp_path, especie):
    path, _ = _gerar(tmp_path, especie, 2)
    linhas = _linhas(path)
    assert all(len(v) == 6 for v in linhas)
    cores = {tuple(round(float(c), 2) for c in v[3:6]) for v in linhas}
    assert len(cores) >= 2 and any(c[1] > c[0] and c[1] > c[2] for c in cores)


def test_baobab_keeps_a_plain_obj_and_is_a_bottle_with_a_narrow_top(tmp_path):
    path, seg = _gerar(tmp_path, "baoba", 4)
    assert all(len(v) == 3 for v in _linhas(path))
    v = _pts(path)  # Y pra cima
    raio = lambda y0, y1: np.hypot(v[(v[:, 1] > y0) & (v[:, 1] < y1), 0], v[(v[:, 1] > y0) & (v[:, 1] < y1), 2]).max()
    altura = seg[9]["end"][2]  # os 10 primeiros segmentos são o tronco
    assert raio(altura * 0.2, altura * 0.35) > raio(altura * 0.85, altura * 0.97) * 1.5  # bojo largo, topo fino
    assert len([s for s in seg if s["start"][2] >= altura * 0.99]) >= 6  # galhos finos saindo do topo


def test_trees_follow_the_requested_height_and_otherwise_grow_from_sapling_to_veteran(tmp_path):
    for especie in ARVORES_EXOTICAS:
        for pedida in (2.5, 4.5):
            partes, seg = exoticas.EXOTICAS[especie](random.Random(5), pedida)
            n_tronco = 10 if especie == "baoba" else 5 if especie == "samambaia_arborea" else 9
            assert seg[n_tronco - 1]["end"][2] == pytest.approx(pedida, rel=0.02)  # `altura` é a do tronco
        alturas = {round(float(exoticas.EXOTICAS[especie](random.Random(s), None)[1][0]["end"][2]), 2) for s in range(12)}
        assert len(alturas) > 6
    path, _ = _gerar(tmp_path, "cica", 1, altura=1.5)
    assert os.path.getsize(path) > 0


def test_nepentes_hangs_three_to_six_pitchers_on_tendrils(tmp_path):
    contagens = set()
    for seed in range(12):
        partes, _ = exoticas.gerar_nepentes(random.Random(seed))
        contagens.add(sum(1 for p in partes if len(p[0]) == 5 * 9 + 9 * 0 or len(p[0]) == 6 * 9))  # esferas de jarro (n_lat=5, n_lon=9)
    assert contagens <= set(range(3, 7)) and len(contagens) >= 2


def test_giant_water_lily_pad_has_a_raised_rim_and_a_notch(tmp_path):
    partes = exoticas.almofada_vitoria(random.Random(1), (3.0, -2.0), 1.2)
    v = np.vstack([p[0] for p in partes])
    assert v[:, 2].max() == pytest.approx(0.04 + 0.14) and v[:, 2].min() >= 0.04
    d = np.hypot(v[:, 0] - 3.0, v[:, 1] + 2.0)
    assert d.max() == pytest.approx(1.2, abs=1e-6)
    path, _ = _gerar(tmp_path, "vitoria_regia", 2)
    p = _pts(path)
    assert 0.9 <= np.hypot(p[:, 0], p[:, 2]).max() <= 1.6 and p[:, 1].max() < 0.5  # folha rente à água


def test_corpse_flower_is_either_the_inflorescence_or_the_single_leaf(tmp_path):
    flor = folha = 0
    for seed in range(30):
        partes, seg = exoticas.gerar_flor_cadaver(random.Random(seed))
        cores = {tuple(round(c, 2) for c in p[2]) for p in partes}
        if exoticas.ESPATA_DENTRO in cores:
            flor += 1
            assert exoticas.ESPADICE in cores  # o espádice alto, junto da espata vinho
        else:
            folha += 1
    assert flor > 5 and folha > 5
