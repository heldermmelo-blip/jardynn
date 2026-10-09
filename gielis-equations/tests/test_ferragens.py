import math
import os
import random

import numpy as np
import pytest

from gielis import ferragens
from gielis.structures import generate_gazebo, generate_tower


def _n(grupos, grupo):
    return len(grupos[grupo])


def _verts(partes):
    return np.vstack([v for v, _ in partes]) if partes else np.zeros((0, 3))


def test_three_styles_with_their_own_materials():
    assert set(ferragens.ESTILOS) == {"art_nouveau", "rustico", "classico"}
    a = ferragens.parapeito(random.Random(1), (0, 0), (6, 0), 0.0, estilo="art_nouveau")
    r = ferragens.parapeito(random.Random(1), (0, 0), (6, 0), 0.0, estilo="rustico")
    c = ferragens.parapeito(random.Random(1), (0, 0), (6, 0), 0.0, estilo="classico")
    assert _n(a, "ferro") > 100 and not r["ferro"] and not c["ferro"]  # ferro só no art nouveau
    assert _n(r, "madeira") > 5 and not r["pedra"] and not r["jarro"]  # rústico: madeira, sem jarros
    assert _n(c, "pedra") > 30 and _n(c, "jarro") > 0  # clássico: balaústres de pedra com jarros


def test_art_nouveau_panel_is_symmetric_about_its_axis():
    painel = ferragens.painel_art_nouveau(random.Random(2), (0, 0, 0), (1, 0, 0), (0, 0, 1), 1.2, 2.0)
    v = _verts(painel["ferro"])
    assert len(v) > 300 and v[:, 0].min() >= -0.2 and v[:, 0].max() <= 1.4
    esq = (v[:, 0] < 0.6 - 0.05).sum()
    dir = (v[:, 0] > 0.6 + 0.05).sum()
    assert abs(esq - dir) <= 0.2 * (esq + dir)  # espelhado em torno do centro
    assert v[:, 2].max() <= 2.0 + 0.2 and v[:, 2].min() >= -0.05


def test_panel_is_deterministic_and_varies_with_the_seed():
    a = ferragens.painel_art_nouveau(random.Random(3), (0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 1.8)
    b = ferragens.painel_art_nouveau(random.Random(3), (0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 1.8)
    c = ferragens.painel_art_nouveau(random.Random(4), (0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 1.8)
    assert np.array_equal(_verts(a["ferro"]), _verts(b["ferro"]))
    assert len(_verts(a["ferro"])) != len(_verts(c["ferro"])) or not np.array_equal(_verts(a["ferro"]), _verts(c["ferro"]))


@pytest.mark.parametrize("estilo", ferragens.ESTILOS)
def test_ruin_drops_pieces_and_grows_moss(estilo):
    inteiros = ruinas = 0
    for seed in range(12):
        i = ferragens.parapeito(random.Random(seed), (0, 0), (8, 0), 0.0, estilo=estilo, ruina=False)
        r = ferragens.parapeito(random.Random(seed), (0, 0), (8, 0), 0.0, estilo=estilo, ruina=True)
        assert not i["musgo"] and r["musgo"]
        inteiros += sum(len(v) for g, v in i.items() if g != "musgo")
        ruinas += sum(len(v) for g, v in r.items() if g != "musgo")
    # o corrimão rústico se parte em pedaços (mais peças, menores); nos outros estilos, sobra menos
    assert ruinas != inteiros if estilo == "rustico" else ruinas < inteiros * 0.95


def test_urns_can_be_toppled_or_gone_in_ruins():
    inteiros = [len(ferragens.parapeito(random.Random(s), (0, 0), (10, 0), 0.0, estilo="classico")["jarro"]) for s in range(20)]
    ruinas = [len(ferragens.parapeito(random.Random(s), (0, 0), (10, 0), 0.0, estilo="classico", ruina=True)["jarro"]) for s in range(20)]
    assert sum(ruinas) < sum(inteiros)
    # um jarro tombado fica rente ao chão; um de pé passa de meio metro de altura
    de_pe = _verts(ferragens.jarro(random.Random(1), (0, 0, 0.0)))
    deitado = _verts(ferragens.jarro(random.Random(1), (0, 0, 0.0), tombado=True))
    assert de_pe[:, 2].max() > 0.5 and deitado[:, 2].max() < de_pe[:, 2].max() * 0.8


def test_parapet_stays_along_its_segment_and_rises_to_the_requested_height():
    g = ferragens.parapeito(random.Random(5), (0, 0), (6, 0), 2.0, altura=0.95, estilo="classico", com_jarros=False)
    v = _verts([p for partes in g.values() for p in partes])
    assert v[:, 2].min() >= 2.0 - 0.01 and v[:, 2].max() <= 2.0 + 1.05 + 0.2
    assert v[:, 0].min() >= -0.2 and v[:, 0].max() <= 6.2 and abs(v[:, 1]).max() < 0.3


# --- aplicação na torre e no gazebo ------------------------------------------------------


@pytest.mark.parametrize("estilo", ferragens.ESTILOS)
def test_tower_door_and_windows_get_grilles_in_the_towers_style(tmp_path, estilo):
    _, sk = generate_tower(random.Random(2), 5, out_path=os.path.join(tmp_path, "t.obj"), estilo=estilo, roof=False)
    malhas = sk[0]["malhas"]
    assert sk[0]["estilo"] == estilo
    if estilo == "rustico":
        assert "ferro" not in malhas
    else:
        assert os.path.getsize(malhas["ferro"]) > 0
    assert os.path.getsize(malhas.get("pedra", malhas["tijolo"])) > 0  # o parapeito do topo destelhado


def test_roofless_tower_gets_a_parapet_and_roofed_one_does_not(tmp_path):
    _, a = generate_tower(random.Random(3), 4, out_path=os.path.join(tmp_path, "a.obj"), estilo="classico", roof=False)
    _, b = generate_tower(random.Random(3), 4, out_path=os.path.join(tmp_path, "b.obj"), estilo="classico", roof=True)
    assert "jarro" in a[0]["malhas"] and "jarro" not in b[0]["malhas"]


def test_tower_in_ruins_loses_wall_pieces_and_shutters(tmp_path):
    def area_parede(ruina):
        total = 0.0
        for seed in range(6):
            _, sk = generate_tower(random.Random(seed), 6, out_path=os.path.join(tmp_path, "t.obj"), estilo="classico", ruina=ruina)
            linhas = open(sk[0]["malhas"]["tijolo"]).read().splitlines()
            v = np.array([[float(c) for c in l.split()[1:4]] for l in linhas if l.startswith("v ")])
            for l in linhas:
                if l.startswith("f "):
                    a, b, c = (v[int(t) - 1] for t in l.split()[1:4])
                    total += 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
        return total

    assert area_parede(True) < area_parede(False)


def test_gazebo_has_materials_style_and_a_ruined_roof_in_some_cases(tmp_path):
    _, sk = generate_gazebo(random.Random(1), out_path=os.path.join(tmp_path, "g.obj"), estilo="classico")
    assert {"madeira", "telhado", "pedra"} <= set(sk[0]["malhas"]) and sk[0]["estilo"] == "classico"
    sem_telhado = sum(
        "telhado" not in generate_gazebo(random.Random(s), out_path=os.path.join(tmp_path, "r.obj"), ruina=True)[1][0]["malhas"] for s in range(40)
    )
    com_telhado = sum("telhado" in generate_gazebo(random.Random(s), out_path=os.path.join(tmp_path, "i.obj"), ruina=False)[1][0]["malhas"] for s in range(10))
    assert 10 <= sem_telhado <= 30 and com_telhado == 10  # ~metade dos coretos em ruína perde o telhado
