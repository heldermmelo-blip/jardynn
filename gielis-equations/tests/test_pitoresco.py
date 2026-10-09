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
        assert todos[:, 1].min() >= -0.55  # no máximo as pedras da margem e o canto afundado da casa torta


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


# --- ruína, estilo e as estruturas da foto do jardim abandonado ------------------------------


@pytest.mark.parametrize("tipo", sorted(pitoresco.GERADORES))
def test_every_structure_accepts_ruin_and_style_and_still_fits_its_radius(tmp_path, tipo):
    for ruina in (False, True):
        for estilo in ("art_nouveau", "rustico", "classico"):
            path, info = pitoresco.GERADORES[tipo](
                random.Random(6), out_path=os.path.join(tmp_path, f"{tipo}.obj"), ruina=ruina, estilo=estilo
            )
            todos = np.vstack([_verts(m) for m in info["malhas"].values()])
            assert np.hypot(todos[:, 0], todos[:, 2]).max() <= info["raio_ocupado"] + 0.01


def test_ruin_adds_moss_and_never_adds_it_to_intact_ones(tmp_path):
    for tipo in ("fonte", "estatuas", "xadrez", "escadaria"):
        _, intacta = pitoresco.GERADORES[tipo](random.Random(2), out_path=os.path.join(tmp_path, "i.obj"), ruina=False, estilo="classico")
        _, ruina = pitoresco.GERADORES[tipo](random.Random(2), out_path=os.path.join(tmp_path, "r.obj"), ruina=True, estilo="classico")
        assert "musgo" not in intacta["malhas"] and "musgo" in ruina["malhas"]


def test_ruined_fountain_is_dry_and_sometimes_loses_its_top_basin(tmp_path):
    cheias = [pitoresco.generate_fountain(random.Random(s), os.path.join(tmp_path, "f.obj"), seca=False)[1] for s in range(10)]
    ruinas = [pitoresco.generate_fountain(random.Random(s), os.path.join(tmp_path, "g.obj"), seca=False, ruina=True)[1] for s in range(40)]
    assert all("agua" in i["malhas"] for i in cheias)
    assert all(r["seca"] and "agua" not in r["malhas"] for r in ruinas)  # a ruína seca a fonte
    assert 8 <= sum(r["quebrada"] for r in ruinas) <= 32  # ~metade perde a bacia de cima


def test_ruined_statuary_topples_and_beheads_statues(tmp_path):
    from gielis.pitoresco import _Peças, _estatua

    def altura(**kw):
        p = _Peças("pedra")
        _estatua(p, 0.0, 0.0, 0.0, random.Random(1), 0.8, **kw)
        return np.vstack([v for v, _ in p.grupos["marmore"]])

    de_pe, sem_cabeca, caida = altura(), altura(sem_cabeca=True), altura(derrubada=True)
    assert de_pe[:, 2].max() > 1.9  # pedestal + corpo + cabeça
    assert sem_cabeca[:, 2].max() < de_pe[:, 2].max() - 0.1 and len(sem_cabeca) < len(de_pe)  # sem cabeça
    assert caida[:, 2].max() < 1.0  # a estátua caída jaz no chão (só o pedestal sobra de pé)
    _, info = pitoresco.generate_statuary(random.Random(1), os.path.join(tmp_path, "e.obj"), estilo="rustico")
    assert "madeira" in info["malhas"] and info["estilo"] == "rustico"  # o parapeito em volta do terraço


def test_stair_terrace_is_curved_steps_around_a_round_lawn_with_a_parapet(tmp_path):
    _, info = pitoresco.generate_stair_terrace(random.Random(3), os.path.join(tmp_path, "s.obj"), estilo="classico")
    assert 5 <= info["degraus"] <= 8 and {"gramado", "pedra", "jarro"} <= set(info["malhas"])
    v = _verts(info["malhas"]["pedra"])
    assert v[:, 1].max() >= info["degraus"] * 0.2 and v[:, 1].max() <= info["degraus"] * 0.26 + 1.4  # sobe um degrau por vez
    _, ruina = pitoresco.generate_stair_terrace(random.Random(3), os.path.join(tmp_path, "r.obj"), ruina=True, estilo="classico")
    assert len(_verts(ruina["malhas"]["pedra"])) < len(v) * 1.1  # perdeu degraus e muro


def test_leaning_house_is_tilted_with_windows_roof_and_a_sunken_corner(tmp_path):
    _, info = pitoresco.generate_leaning_house(random.Random(4), os.path.join(tmp_path, "c.obj"))
    assert 5.0 <= info["inclinacao_graus"] <= 12.0 and {"reboco", "pedra"} <= set(info["malhas"])
    v = _verts(info["malhas"]["reboco"])
    assert v[:, 1].max() > 5.0  # dois andares
    # o telhado de telhas existe na maioria; uma água pode ter caído
    teve_telhado = sum("telha" in pitoresco.generate_leaning_house(random.Random(s), os.path.join(tmp_path, "x.obj"))[1]["malhas"] for s in range(20))
    assert teve_telhado >= 15
    # inclinada: o topo não está acima do centro da base
    base = v[v[:, 1] < 0.8]
    topo = v[v[:, 1] > v[:, 1].max() - 0.8]
    deslocamento = np.hypot(*(topo[:, [0, 2]].mean(axis=0) - base[:, [0, 2]].mean(axis=0)))
    assert deslocamento > 0.4
