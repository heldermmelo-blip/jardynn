import math
import random

import pytest

from ynn import cli, generator, tables
from ynn.generator import PITORESCOS

LOTES_CONHECIDOS = {"area", "canteiro", "estufa", "gazebo", "torre", *PITORESCOS}


def test_every_location_maps_to_a_known_lot_type():
    tipos = {tipo for _, tipo in tables.LOCAIS}
    assert tipos <= LOTES_CONHECIDOS
    assert set(PITORESCOS) <= tipos  # todo tipo pitoresco pode sair no sorteio


def _niveis(sementes, **kw):
    for seed in sementes:
        yield generator.generate_nivel(random.Random(seed), profundidade_max=5, max_nos=14, estufa_colossal="nunca", **kw)


def test_picturesque_lots_carry_meshes_radius_and_rotation(tmp_path):
    vistos = set()
    for nivel in _niveis(range(12), plant_output_dir=str(tmp_path)):
        for plot in nivel["layout"]["plots"]:
            if plot["tipo"] not in PITORESCOS:
                continue
            vistos.add(plot["tipo"])
            assert plot["malhas"] and plot["obj"] in plot["malhas"].values()
            assert plot["raio_ocupado"] > 1.0 and "rotacao_y" in plot
            assert "pitoresco" in plot
    assert len(vistos) >= 5


def test_terrain_is_flat_under_picturesque_structures(tmp_path):
    achados = 0
    for nivel in _niveis(range(10), plant_output_dir=str(tmp_path)):
        terreno = nivel["terreno"]
        meia, cel = (terreno["resolucao"] - 1) / 2, terreno["tamanho_celula"]
        for plot in nivel["layout"]["plots"]:
            if plot["tipo"] not in PITORESCOS:
                continue
            achados += 1
            for j, linha in enumerate(terreno["alturas"]):
                for i, h in enumerate(linha):
                    if math.hypot((i - meia) * cel - plot["x"], (j - meia) * cel - plot["z"]) <= plot["raio_ocupado"]:
                        assert h == 0.0
    assert achados >= 5


def test_picturesque_lots_do_not_overlap_other_lots(tmp_path):
    for nivel in _niveis(range(6), plant_output_dir=str(tmp_path)):
        plots = nivel["layout"]["plots"]
        for i, a in enumerate(plots):
            for b in plots[i + 1 :]:
                if a["tipo"] in PITORESCOS or b["tipo"] in PITORESCOS:
                    ra, rb = a.get("raio_ocupado", 6.0), b.get("raio_ocupado", 6.0)
                    assert math.hypot(a["x"] - b["x"], a["z"] - b["z"]) >= (ra + rb) * 0.8


def test_doorways_face_the_trail_that_leads_to_them(tmp_path):
    achados = 0
    for nivel in _niveis(range(25), plant_output_dir=str(tmp_path)):
        for plot in nivel["layout"]["plots"]:
            if plot["tipo"] in ("labirinto", "mausoleu"):
                achados += 1
                assert plot["porta_angulo_godot"] == pytest.approx(math.pi / 2)
                assert math.isfinite(plot["rotacao_y"])
    assert achados >= 3


def test_markdown_lists_the_picturesque_lots(tmp_path):
    for nivel in _niveis([42], plant_output_dir=str(tmp_path)):
        texto = cli.render_nivel_markdown(nivel)
        for plot in nivel["layout"]["plots"]:
            if plot["tipo"] in PITORESCOS:
                assert f"- {plot['tipo']} em (" in texto


def test_the_colossal_level_has_no_picturesque_structures(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(8), profundidade_max=5, max_nos=14, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
    )
    assert not any(p["tipo"] in PITORESCOS for p in nivel["layout"]["plots"])
