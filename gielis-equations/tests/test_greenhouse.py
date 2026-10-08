import math
import os
import random

import numpy as np
import pytest

from gielis.greenhouse import _convex_overlap, generate_greenhouse, group_path


def _verts(path):
    with open(path) as f:
        return np.array([[float(c) for c in line.split()[1:4]] for line in f if line.startswith("v ")])


def _gerar(tmp_path, nome="e", seed=1, **kw):
    path, info = generate_greenhouse(random.Random(seed), out_path=os.path.join(tmp_path, f"{nome}.obj"), **kw)
    return path, info


@pytest.mark.parametrize("sides", [3, 4, 5, 6, 8])
def test_builds_frame_glass_and_plinth_for_each_floorplan(tmp_path, sides):
    _, info = _gerar(tmp_path, sides=sides, radius=4.5)
    for grupo in ("moldura", "vidro", "soco"):
        assert os.path.getsize(info["malhas"][grupo]) > 0
    assert info["raio_ocupado"] >= 4.4


def test_group_paths_sit_next_to_the_frame(tmp_path):
    path, info = _gerar(tmp_path, nome="x", sides=5, radius=4.0)
    assert info["malhas"]["moldura"] == path
    assert info["malhas"]["vidro"] == group_path(path, "vidro") == os.path.join(tmp_path, "x_vidro.obj")


def test_more_floors_make_it_taller(tmp_path):
    alturas = []
    for andares in (1, 2, 3):
        path, _ = _gerar(tmp_path, nome=f"a{andares}", sides=5, radius=5.0, n_floors=andares)
        alturas.append(_verts(path)[:, 1].max())
    assert alturas == sorted(alturas) and alturas[2] > alturas[0] + 4.0


def test_tiny_one_is_not_enterable_and_a_normal_one_has_one_door(tmp_path):
    _, tiny = _gerar(tmp_path, nome="t", sides=4, radius=1.5)
    _, normal = _gerar(tmp_path, nome="n", sides=5, radius=4.0)
    assert tiny["portas_angulos"] == []
    assert len(normal["portas_angulos"]) == 1


def test_palace_has_two_wings_and_cross_has_four(tmp_path):
    for seed in range(8):
        _, palacio = _gerar(tmp_path, nome="p", seed=seed, sides=4, radius=4.5, n_wings=2, padrao="palacio")
        _, cruz = _gerar(tmp_path, nome="c", seed=seed, sides=4, radius=4.0, n_wings=4, padrao="cruz")
        assert palacio["n_alas"] == 2
        assert cruz["n_alas"] == 4


def test_many_wings_can_chain_off_other_wings(tmp_path):
    alas = [_gerar(tmp_path, nome="m", seed=s, sides=8, radius=5.5, n_floors=3, n_wings=9)[1]["n_alas"] for s in range(6)]
    assert max(alas) >= 6  # mais que as faces do núcleo menos a da porta: tem ala saindo de ala


def test_footprints_never_overlap(tmp_path):
    for seed in range(10):
        _, info = _gerar(tmp_path, nome="o", seed=seed, sides=rng_sides(seed), radius=5.0, n_floors=2, n_wings=7)
        polys = info["pegadas"]
        for i in range(len(polys)):
            for j in range(i + 1, len(polys)):
                assert not _convex_overlap(polys[i], polys[j])


def rng_sides(seed):
    return (4, 5, 6, 8)[seed % 4]


def test_ruined_loses_glass_panes_and_grows_dead_vines(tmp_path):
    inteiro = ruina = 0
    for seed in range(8):
        _, a = _gerar(tmp_path, nome="i", seed=seed, sides=5, radius=5.0, n_floors=2)
        _, b = _gerar(tmp_path, nome="r", seed=seed, sides=5, radius=5.0, n_floors=2, ruined=True)
        inteiro += len(_verts(a["malhas"]["vidro"]))
        ruina += len(_verts(b["malhas"]["vidro"]))
        assert "morto" not in a["malhas"] and "morto" in b["malhas"]
        assert 0.35 <= b["pane_loss"] <= 0.75 and a["pane_loss"] == 0.0
    assert ruina < inteiro * 0.8


def test_checker_floor_alternates_black_and_white_tiles(tmp_path):
    _, info = _gerar(tmp_path, sides=6, radius=5.0, checker=True)
    pretas = len(_verts(info["malhas"]["piso_preto"])) // 4
    brancas = len(_verts(info["malhas"]["piso_branco"])) // 4
    assert pretas > 10 and abs(pretas - brancas) <= max(3, pretas * 0.15)
    _, sem = _gerar(tmp_path, nome="s", sides=6, radius=5.0, checker=False)
    assert "piso_preto" not in sem["malhas"]


def test_level_sized_greenhouse_has_entry_and_exit_on_opposite_sides(tmp_path):
    n, raio = 32, 60.0
    path, info = _gerar(
        tmp_path,
        nome="col",
        sides=n,
        radius=raio,
        n_floors=3,
        bay=raio / 18.0,
        fase=math.pi / 2 - math.pi / n,
        portas_angulos=[math.pi / 2, -math.pi / 2],
    )
    assert info["raio_ocupado"] == pytest.approx(raio, abs=0.5)
    a, b = info["portas_angulos"]
    assert abs(abs(a - b) - math.pi) < 1e-6  # lados opostos
    peso = sum(os.path.getsize(p) for p in info["malhas"].values())
    assert peso < 5_000_000  # enorme, mas ainda um arquivo razoável


def test_is_deterministic(tmp_path):
    a, ia = _gerar(tmp_path, nome="a", seed=5, sides=5, radius=5.0, n_wings=3, ruined=True, checker=True)
    b, ib = _gerar(tmp_path, nome="b", seed=5, sides=5, radius=5.0, n_wings=3, ruined=True, checker=True)
    for grupo in ia["malhas"]:
        with open(ia["malhas"][grupo]) as fa, open(ib["malhas"][grupo]) as fb:
            assert fa.read() == fb.read()
