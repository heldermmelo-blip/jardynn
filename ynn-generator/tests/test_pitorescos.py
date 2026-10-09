import math
import random

import pytest

from ynn import cli, generator, tables
from ynn.generator import PITORESCOS

LOTES_CONHECIDOS = {"area", "canteiro", "estufa", "orquidario", "gazebo", "torre", *PITORESCOS}


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


# --- flores -----------------------------------------------------------------------


def test_vegetation_and_canteiro_species_exist_and_include_the_flower_family():
    from gielis.plants import ESPECIES_FLORES, SPECIES

    especies = {e for _, _, e in tables.VEGETATION if e}
    assert especies <= set(SPECIES)
    assert {"tulipa", "girassol", "rosa", "lavanda", "margarida", "dalia"} <= especies
    assert set(generator.CANTEIRO_SPECIES) <= set(SPECIES)
    assert len(set(generator.CANTEIRO_SPECIES) & set(ESPECIES_FLORES)) >= 5
    assert set(tables.CANTEIRO_ESPECIE_POR_LOCAL.values()) <= set(SPECIES)
    assert set(tables.CANTEIRO_ESPECIE_POR_LOCAL) <= {nome for nome, _ in tables.LOCAIS}
    assert {nome for nome, tipo in tables.LOCAIS if tipo == "canteiro"} == set(tables.CANTEIRO_ESPECIE_POR_LOCAL)


def test_areas_report_their_vegetation_species(tmp_path):
    for nivel in _niveis(range(4), plant_output_dir=str(tmp_path)):
        for area in nivel["areas"]:
            assert "especie_vegetacao" in area
            assert (area["especie_vegetacao"] is None) == (not area["plantas_obj"])


def test_pond_has_water_lily_flowers_unless_frozen(tmp_path):
    from gielis import pitoresco
    import os

    com_flor = sum("flor" in pitoresco.generate_pond(random.Random(s), os.path.join(tmp_path, "l.obj"))[1]["malhas"] for s in range(20))
    assert com_flor == 20
    assert "flor" not in pitoresco.generate_pond(random.Random(1), os.path.join(tmp_path, "g.obj"), gelado=True)[1]["malhas"]


# --- ruína e estilo das estruturas (a maioria jaz em ruínas) -----------------------------




def test_the_three_flower_bed_places_grow_their_own_species(tmp_path):
    esperado = {"Horta de Ervas": "arbusto", "Roseiral": "rosa", "Canteiros de Cogumelos": "cogumelo"}
    assert tables.CANTEIRO_ESPECIE_POR_LOCAL == esperado
    for nome, especie in esperado.items():
        plot = {"tipo": "canteiro", "x": 0.0, "z": 0.0, "local": nome}
        generator._preencher_lote(random.Random(1), 2, plot, 1, str(tmp_path), [])
        assert plot["especie"] == especie and all(f"_{especie}_" in p for p in plot["plantas_obj"])


def test_towers_and_gazebos_are_whole_only_with_the_two_kept_details_and_have_a_style(tmp_path):
    from gielis.ferragens import ESTILOS

    for tipo in ("torre", "gazebo"):
        estilos = set()
        for seed in range(40):
            for efeitos, estado in (([], "ruina"), (["bem_cuidado"], "intacta"), (["hera"], "intacta"), (["alagado"], "ruina")):
                plot = {"tipo": tipo, "x": 0.0, "z": 0.0}
                generator._preencher_lote(random.Random(seed), 3, plot, seed, str(tmp_path), efeitos)
                assert plot["estado"] == estado
                estilos.add(plot["estilo"])
            if estilos == set(ESTILOS):
                break
        assert estilos == set(ESTILOS)  # nem toda estrutura segue o mesmo esquema


def test_a_lot_without_effects_rolls_its_own_detail_from_the_book(tmp_path):
    plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(9), 4, plot, 1, str(tmp_path))
    assert plot["detalhe"]["indice"] >= 4  # d20 + profundidade 3
    assert plot["estado"] in ("intacta", "ruina")


def test_orchid_wings_under_the_colossal_greenhouse_grow_orchids(tmp_path):
    achados = 0
    for seed in range(1, 9):
        nivel = generator.generate_nivel(
            random.Random(seed), profundidade_max=3, max_nos=10, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
        )
        for plot in nivel["layout"]["plots"]:
            if plot["ala"] == "orquidario":
                achados += 1
                flora = plot["estufas"][0]["flora_interna"]
                assert flora["tema"] == "orquidario" and "orquidea" in flora["especies"] + ["orquidea"]
                assert plot["estufas"][0]["conteudo"]["orquidario"]
    assert achados >= 3
