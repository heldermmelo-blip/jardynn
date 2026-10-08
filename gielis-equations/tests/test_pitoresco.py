import math
import os
import random

import numpy as np
import pytest

from gielis import pitoresco


def _verts(path):
    with open(path) as f:
        return np.array([[float(c) for c in line.split()[1:4]] for line in f if line.startswith("v ")])


def _gerar(tmp_path, tipo, seed=1, **kw):
    gerador = pitoresco.GERADORES[tipo]
    return gerador(random.Random(seed), out_path=os.path.join(tmp_path, f"{tipo}.obj"), **kw)


@pytest.mark.parametrize("tipo", sorted(pitoresco.GERADORES))
def test_every_structure_builds_and_fits_in_its_radius(tmp_path, tipo):
    for seed in range(5):
        path, info = _gerar(tmp_path, tipo, seed)
        assert path in info["malhas"].values() and os.path.getsize(path) > 0
        assert all(os.path.getsize(m) > 0 for m in info["malhas"].values())
        todos = np.vstack([_verts(m) for m in info["malhas"].values()])
        # o .obj sai em Y pra cima: o chão é X/Z
        assert np.hypot(todos[:, 0], todos[:, 2]).max() <= info["raio_ocupado"] + 0.01
        assert todos[:, 1].min() >= -0.25  # no máximo as pedras da margem, meio enterradas


@pytest.mark.parametrize("tipo", sorted(pitoresco.GERADORES))
def test_is_deterministic(tmp_path, tipo):
    a, ia = _gerar(tmp_path, tipo, 7)
    primeiro = {g: open(p).read() for g, p in ia["malhas"].items()}
    b, ib = _gerar(tmp_path, tipo, 7)
    assert primeiro == {g: open(p).read() for g, p in ib["malhas"].items()}


def test_maze_is_a_perfect_maze_with_an_entrance(tmp_path):
    for seed in range(12):
        n = random.Random(seed).randint(6, 9)
        abertas = pitoresco.sortear_labirinto(random.Random(seed), n)
        assert len(abertas) == n * n - 1  # perfeito: uma árvore geradora
        vizinhos = {}
        for a, b in abertas:
            vizinhos.setdefault(a, []).append(b)
            vizinhos.setdefault(b, []).append(a)
        visto, pilha = {(0, 0)}, [(0, 0)]
        while pilha:
            for v in vizinhos.get(pilha.pop(), []):
                if v not in visto:
                    visto.add(v)
                    pilha.append(v)
        assert len(visto) == n * n  # todas as células alcançáveis: o centro tem caminho
    _, info = _gerar(tmp_path, "labirinto", 3)
    assert 0 <= info["entrada"] < info["n"] and info["passagens"] == info["n"] ** 2 - 1


def test_fountain_can_be_dry_or_full(tmp_path):
    _, seca = _gerar(tmp_path, "fonte", 1, seca=True)
    _, cheia = _gerar(tmp_path, "fonte", 1, seca=False)
    assert "agua" not in seca["malhas"] and "agua" in cheia["malhas"]
    secas = sum(pitoresco.generate_fountain(random.Random(s), out_path=os.path.join(tmp_path, "f.obj"))[1]["seca"] for s in range(200))
    assert 30 <= secas <= 90  # ~30%


def test_pond_has_water_or_ice_never_both(tmp_path):
    _, agua = _gerar(tmp_path, "lago")
    _, gelo = _gerar(tmp_path, "lago_gelado")
    assert "agua" in agua["malhas"] and "folha" in agua["malhas"] and "gelo" not in agua["malhas"]
    assert "gelo" in gelo["malhas"] and "agua" not in gelo["malhas"]


def test_chess_lawn_alternates_squares_and_has_giant_pieces(tmp_path):
    _, info = _gerar(tmp_path, "xadrez", 2)
    pretas = len(_verts(info["malhas"]["pedra_preta"])) // 8
    verdes = len(_verts(info["malhas"]["gramado"])) // 8
    assert pretas == verdes == 32
    assert 6 <= len(info["pecas"]) <= 12
    assert {p["tipo"] for p in info["pecas"]} <= {"peao", "torre", "bispo", "cavalo", "rainha", "rei"}
    altos = _verts(info["malhas"].get("marmore", info["malhas"]["gramado"]))
    assert altos[:, 1].max() > 1.5  # as peças têm mais do dobro da altura de uma pessoa agachada


def test_mausoleum_has_a_dark_door_and_ivy(tmp_path):
    _, info = _gerar(tmp_path, "mausoleu")
    assert {"marmore", "porta", "hera"} <= set(info["malhas"])
    assert info["porta_angulo"] == pytest.approx(-math.pi / 2)


def test_statuary_ring_has_between_five_and_nine_statues(tmp_path):
    contagens = {pitoresco.generate_statuary(random.Random(s), out_path=os.path.join(tmp_path, "e.obj"))[1]["estatuas"] for s in range(40)}
    assert contagens <= set(range(5, 10)) and len(contagens) >= 3
