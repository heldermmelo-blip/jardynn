import os
import random

from ynn.generator import band_for_layer, generate_area, generate_layer, generate_layout_camada, generate_torre_conteudo

from ynn import generator
from ynn.generator import CANTEIRO_SPECIES


def test_band_for_layer():
    assert band_for_layer(1) == "jardim_externo"
    assert band_for_layer(2) == "jardim_externo"
    assert band_for_layer(3) == "jardim_profundo"
    assert band_for_layer(4) == "jardim_profundo"
    assert band_for_layer(5) == "nucleo_selvagem"
    assert band_for_layer(20) == "nucleo_selvagem"


def test_generate_layer_returns_requested_count():
    rng = random.Random(0)
    areas = generate_layer(rng, layer=1, n_areas=7)
    assert len(areas) == 7
    assert [a["index"] for a in areas] == list(range(1, 8))


def test_same_seed_is_deterministic():
    areas_a = generate_layer(random.Random(42), layer=3, n_areas=5)
    areas_b = generate_layer(random.Random(42), layer=3, n_areas=5)
    assert [a["text"] for a in areas_a] == [b["text"] for b in areas_b]


def test_all_layers_generate_without_error():
    for layer in range(1, 11):
        rng = random.Random(layer)
        areas = generate_layer(rng, layer=layer, n_areas=3)
        for area in areas:
            assert area["text"]
            assert area["layer"] == layer


def test_generate_area_text_is_nonempty():
    rng = random.Random(1)
    area = generate_area(rng, layer=1, index=1)
    assert isinstance(area["text"], str)
    assert len(area["text"]) > 0


def test_denizen_with_class_produces_npc_stats():
    found_npc = False
    for seed in range(200):
        area = generate_area(random.Random(seed), layer=3, index=1)
        if area["npc"] is not None:
            found_npc = True
            assert area["npc"]["pontos_de_vida"] >= 1
            assert area["has_denizen"] is True
    assert found_npc


def test_area_without_stated_denizen_has_no_npc():
    rng = random.Random(2)
    area = generate_area(rng, layer=1, index=1)
    if not area["has_denizen"]:
        assert area["npc"] is None


def test_denizen_with_creature_produces_creature_stats():
    found_creature = False
    for seed in range(200):
        area = generate_area(random.Random(seed), layer=3, index=1)
        if area["criatura"] is not None:
            found_creature = True
            assert area["criatura"]["pontos_de_vida"] >= 1
            assert area["has_denizen"] is True
            assert area["npc"] is None  # nunca os dois ao mesmo tempo
    assert found_creature


def test_npc_and_creature_are_mutually_exclusive():
    for seed in range(200):
        area = generate_area(random.Random(seed), layer=3, index=1)
        assert not (area["npc"] is not None and area["criatura"] is not None)


def test_vegetation_with_species_produces_plant_meshes():
    found_plant = False
    for seed in range(50):
        area = generate_area(random.Random(seed), layer=1, index=1)
        if area["plantas_obj"]:
            found_plant = True
            assert len(area["plantas_obj"]) >= 3  # PLANT_VARIANT_RANGE mínimo
            for path in area["plantas_obj"]:
                assert os.path.exists(path)
                assert os.path.getsize(path) > 0
    assert found_plant


def test_ground_cover_area_has_no_plant_meshes():
    for seed in range(50):
        area = generate_area(random.Random(seed), layer=1, index=1)
        if not area["plantas_obj"]:
            assert area["plantas_obj"] == []


def test_area_without_fallen_branches_has_empty_list():
    for seed in range(50):
        area = generate_area(random.Random(seed), layer=1, index=1)
        if not area["galhos_caidos_obj"]:
            assert area["galhos_caidos_obj"] == []
            assert "galhos cortados ou caídos" not in area["text"]


def test_generate_layout_camada_populates_structure_meshes():
    rng = random.Random(1)
    camada_layout = generate_layout_camada(
        rng,
        layer=1,
        n_areas=2,
        n_torres_range=(1, 1),
        n_estufas_range=(1, 1),
        n_canteiros_range=(1, 1),
        n_gazebos_range=(1, 1),
    )
    by_tipo = {}
    for plot in camada_layout["plots"]:
        by_tipo.setdefault(plot["tipo"], []).append(plot)

    torre = by_tipo["torre"][0]
    assert os.path.exists(torre["obj"])
    assert os.path.getsize(torre["obj"]) > 0
    assert torre["conteudo"]["n_andares"] + 1 == len(torre["conteudo"]["andares"])  # o topo rola duas vezes
    assert len(torre["hera_obj"]) >= 3  # IVY_VARIANT_RANGE mínimo
    for path in torre["hera_obj"]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    estufa = by_tipo["estufa"][0]
    assert os.path.exists(estufa["obj"]) and os.path.getsize(estufa["obj"]) > 0
    assert 2 <= len(estufa["estufas"]) <= 5  # um punhado de dados
    for casa in estufa["estufas"]:
        assert casa["planta"]["dado"] in (4, 6, 8, 10, 12, 20)
        assert casa["planta"]["portas"] == casa["planta"]["lados"]
        assert casa["conteudo"]["texto"]

    gazebo = by_tipo["gazebo"][0]
    assert os.path.exists(gazebo["obj"])
    assert os.path.getsize(gazebo["obj"]) > 0
    for chave in ("texto", "bibelo", "tesouro", "refugio"):
        assert gazebo["conteudo"][chave]

    canteiro = by_tipo["canteiro"][0]
    assert canteiro["especie"] in CANTEIRO_SPECIES
    assert len(canteiro["plantas_obj"]) >= 4  # CANTEIRO_VARIANT_RANGE mínimo
    for path in canteiro["plantas_obj"]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    assert len(by_tipo["area"]) == 2
    for plot in by_tipo["area"]:
        assert "obj" not in plot
        assert "plantas_obj" not in plot


def test_estufa_conteudo_table_references_valid_creatures():
    from ynn import tables
    from ynn.creatures import CREATURES

    for texto, _bandas, tipo, criatura_key in tables.ESTUFA_CONTEUDO:
        assert tipo in ("valor", "criatura", None)
        if tipo == "criatura":
            assert criatura_key in CREATURES
        else:
            assert criatura_key is None


def test_gazebo_conteudo_fields_and_determinism():
    from ynn.generator import REFUGIO_GAZEBO, generate_gazebo_conteudo

    a = generate_gazebo_conteudo(random.Random(7), layer=3)
    b = generate_gazebo_conteudo(random.Random(7), layer=3)
    assert a == b
    assert a["refugio"] == REFUGIO_GAZEBO
    assert a["texto"] and a["bibelo"] and a["tesouro"]


def test_torre_conteudo_has_one_entry_per_floor_and_two_on_top():
    for seed in range(30):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        n = conteudo["n_andares"]
        assert 3 <= n <= 8  # N_ANDARES_TORRE_RANGE
        assert len(conteudo["andares"]) == n + 1  # d12 em cada andar, d12 duas vezes no topo
        assert [a["numero"] for a in conteudo["andares"]] == list(range(1, n + 1)) + [n]
        assert [a.get("extra", False) for a in conteudo["andares"]] == [False] * n + [True]


def test_torre_topo_is_the_last_floor_and_distinct_table():
    from ynn import tables

    topo_textos = {entrada[0] for entrada in tables.TORRE_TOPO}
    andar_textos = {entrada[0] for entrada in tables.TORRE_ANDARES}
    assert topo_textos.isdisjoint(andar_textos)

    for seed in range(30):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        topos = [a for a in conteudo["andares"] if a["numero"] == conteudo["n_andares"]]
        assert len(topos) == 2 and topos[0]["texto"] != topos[1]["texto"]
        assert all(t["texto"] in topo_textos for t in topos)


def test_torre_andares_carry_a_prop_and_label():
    for seed in range(20):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        for andar in conteudo["andares"]:
            assert andar["rotulo"]
            assert "prop" in andar
            if andar.get("denizen") is not None:
                assert andar["prop"] == "criatura"


def test_every_tower_prop_has_a_godot_builder():
    from pathlib import Path

    from ynn import tables

    scripts = (Path(__file__).resolve().parents[2] / "jardynn-game" / "scripts").glob("*.gd")
    fonte = " ".join(path.read_text(encoding="utf-8") for path in scripts)
    props = {entrada[3] for entrada in tables.TORRE_ANDARES + tables.TORRE_TOPO if entrada[3]}
    assert len(props) >= 15
    for prop in props:
        assert f'"{prop}"' in fonte, f"nenhum script do Godot tem construtor para o prop {prop!r}"


def test_towers_differ_in_floors_and_geometry():
    from ynn.generator import _preencher_lote

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        torres = []
        for seed in (1, 2, 3, 4, 5, 6):
            plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
            _preencher_lote(random.Random(seed), 3, plot, seed, tmp)
            torres.append(plot)
    andares = {t["conteudo"]["n_andares"] for t in torres}
    assert len(andares) > 1  # cada torre tem seus próprios andares, sorteados por dados
    for t in torres:
        geo = t["geometria"]
        assert len(geo["raios_andar"]) == t["conteudo"]["n_andares"]
        assert geo["altura_andar"] > 0 and 0 < geo["raio_vao"] < min(geo["raios_andar"])
        assert 0.0 <= geo["porta_angulo"] < 6.2832


def test_torre_andar_com_tesouro_ou_encontro_preenchido():
    found_tesouro = False
    found_encontro = False
    for seed in range(60):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        for andar in conteudo["andares"]:
            if andar.get("tesouro") is not None:
                found_tesouro = True
            if andar.get("denizen") is not None:
                found_encontro = True
    assert found_tesouro
    assert found_encontro


def test_torre_conteudo_is_deterministic():
    conteudo_a = generate_torre_conteudo(random.Random(42), layer=3)
    conteudo_b = generate_torre_conteudo(random.Random(42), layer=3)
    assert conteudo_a == conteudo_b


def test_ground_cover_vegetation_has_no_species():
    from ynn import tables

    ground_cover_entries = [
        (text, species) for text, bands, species in tables.VEGETATION if "gramado" in text.lower() or "musgo" in text.lower()
    ]
    assert ground_cover_entries
    assert all(species is None for _, species in ground_cover_entries)


def test_preencher_lote_writes_all_tower_extras(monkeypatch, tmp_path):
    from ynn import generator

    forcado = {
        "topo": ("Uma árvore antiga criou raízes no topo.", "arvore"),
        "trepadeiras": True,
        "inclinacao": {"graus": 8.0, "azimute": 1.0},
    }
    monkeypatch.setattr(generator, "sortear_extras_torre", lambda rng, layer, efeitos=(), **kw: forcado)
    plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(3), 3, plot, 1, str(tmp_path))

    assert plot["inclinacao"] == forcado["inclinacao"]
    assert os.path.getsize(plot["trepadeiras_obj"]) > 0
    assert 1 <= len(plot["topo_obj"]) <= 2  # TORRE_TOPO_VARIANTES["arvore"]
    assert all(os.path.getsize(path) > 0 for path in plot["topo_obj"])
    assert plot["conteudo"]["topo_brotado"]["especie"] == "arvore"
    assert plot["geometria"]["altura_total"] == plot["conteudo"]["n_andares"] * plot["geometria"]["altura_andar"]
    # destelhada: a malha acaba no topo (só a cornija passa)
    with open(plot["obj"]) as f:
        alturas = [float(line.split()[2]) for line in f if line.startswith("v ")]
    assert max(alturas) <= plot["geometria"]["altura_total"] + 0.3


def test_preencher_lote_without_extras_keeps_the_conical_roof(monkeypatch, tmp_path):
    from ynn import generator

    monkeypatch.setattr(
        generator, "sortear_extras_torre", lambda rng, layer, efeitos=(), **kw: {"topo": None, "trepadeiras": False, "inclinacao": None}
    )
    plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(3), 3, plot, 1, str(tmp_path))
    assert "topo_obj" not in plot and "trepadeiras_obj" not in plot and "inclinacao" not in plot
    with open(plot["malhas"]["telhado"]) as f:  # o telhado tem malha própria
        alturas = [float(line.split()[2]) for line in f if line.startswith("v ")]
    assert max(alturas) > plot["geometria"]["altura_total"] + 2.0  # telhado


def test_tower_tables_are_the_two_d12_of_the_book():
    from ynn import tables

    assert len(tables.TORRE_ANDARES) == 12 and len(tables.TORRE_TOPO) == 12
    assert all(entrada[1] == "all" for entrada in tables.TORRE_ANDARES + tables.TORRE_TOPO)  # o livro não filtra por banda
    props = [e[3] for e in tables.TORRE_ANDARES]
    assert props[:5] == [None, "bau", "criatura", "criatura", "mobilia"]  # nada, tesouro, mora, explora, móveis
    assert props[5:] == ["estante", "ninhos", "teias", "esqueleto", "caixotes", "quadros", "espelho"]
    assert [e[3] for e in tables.TORRE_TOPO] == [
        "sino", "telescopio", "camera_escura", "bau_grande", "biblioteca", "criatura",
        "armadilha", "armadura", "maquina", "espelho_sinal", "caixao", "lampada",
    ]


def test_tower_floor_rolls_are_a_fair_d12():
    from collections import Counter

    contagem = Counter()
    for seed in range(1500):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3, n_andares_range=(8, 8))
        for andar in conteudo["andares"][:7]:
            contagem[andar["rotulo"]] += 1
    assert len(contagem) == 12  # os dois encontros têm rótulos diferentes
    esperado = 1500 * 7 / 12
    assert all(abs(c - esperado) < esperado * 0.15 for c in contagem.values())


def test_bookshelf_has_a_one_in_six_spellbook_with_a_first_level_spell():
    achados = estantes = 0
    for seed in range(3000):
        andar = generator._montar_andar(random.Random(seed), tables_andar("estante"), 3, 1, 5, False)
        estantes += 1
        if "livro_de_magias" in andar:
            achados += 1
            assert andar["livro_de_magias"]["nivel"] == 1 and andar["livro_de_magias"]["nome"]
    assert abs(achados / estantes - 1 / 6) < 0.025


def tables_andar(prop):
    from ynn import tables

    return next(e for e in tables.TORRE_ANDARES + tables.TORRE_TOPO if e[3] == prop)


def test_paintings_are_d4_each_worth_100_gold_times_depth():
    for layer in (1, 3, 5):
        for seed in range(100):
            q = generator._montar_andar(random.Random(seed), tables_andar("quadros"), layer, 1, 5, False)["quadros"]
            assert 1 <= q["quantidade"] <= 4 and q["valor_ouro"] == q["quantidade"] * 100 * layer


def test_top_floor_hoard_is_three_treasures_and_library_has_the_dice_ladder():
    for seed in range(60):
        tesouros = generator._montar_andar(random.Random(seed), tables_andar("bau_grande"), 3, 6, 6, True)
        assert len(tesouros["tesouros"]) == 3 and tesouros["tesouro"] == tesouros["tesouros"][0]
        biblioteca = generator._montar_andar(random.Random(seed), tables_andar("biblioteca"), 3, 6, 6, True)["biblioteca"]
        assert 1 <= biblioteca["nivel_1"] <= 12 and 1 <= biblioteca["nivel_2"] <= 10 and 1 <= biblioteca["nivel_3"] <= 8
        assert 1 <= biblioteca["nivel_4"] <= 6 and 1 <= biblioteca["nivel_5"] <= 4 and biblioteca["nivel_6_ou_mais"] == 1


def test_top_floor_monster_is_rolled_deeper_by_the_number_of_floors():
    from ynn.generator import band_for_layer

    # camada 1 sozinha é jardim externo; somando 8 andares vira o núcleo selvagem
    assert band_for_layer(1) != band_for_layer(1 + 8)
    forte = {generator._montar_andar(random.Random(s), tables_andar("criatura"), 1, 8, 8, True).get("denizen") for s in range(80)}
    fraco = {generator._montar_andar(random.Random(s), tables_andar("criatura"), 1, 8, 8, False).get("denizen") for s in range(80)}
    assert forte != fraco


def test_tower_plot_has_door_windows_climbing_rules_and_materials(tmp_path):
    from ynn import tables
    from ynn.generator import _preencher_lote

    for seed in range(1, 7):
        plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
        _preencher_lote(random.Random(seed), 3, plot, seed, str(tmp_path))
        n = plot["conteudo"]["n_andares"]
        assert plot["porta"]["estado"] == "entreaberta"
        assert {"tijolo", "madeira", "tapete", "agua", "papel"} <= set(plot["malhas"])
        assert {j["andar"] for j in plot["geometria"]["janelas"]} == set(range(2, n + 1))
        assert plot["escalada"]["andares_com_janela"] == list(range(2, n + 1))
        assert plot["escalada"]["trepadeiras"] == ("trepadeiras_obj" in plot)
        assert plot["escalada"]["regra"] == tables.TORRE_ESCALADA_REGRA


def test_fallen_branches_come_with_ruin_and_only_with_ruin():
    for seed in range(30):
        ruina = generate_area(random.Random(seed), layer=1, index=1, ruina=True)
        assert 1 <= len(ruina["galhos_caidos_obj"]) <= 3  # 1d3
        assert all(os.path.exists(p) and os.path.getsize(p) > 0 for p in ruina["galhos_caidos_obj"])
        assert "galhos cortados ou caídos" in ruina["text"]
        inteira = generate_area(random.Random(seed), layer=1, index=1, ruina=False)
        assert inteira["galhos_caidos_obj"] == [] and "galhos cortados ou caídos" not in inteira["text"]


def test_an_area_opens_with_its_place_name_and_the_places_own_text():
    from ynn import tables

    for nome, texto in tables.LOCAL_TEXTOS.items():
        area = generate_area(random.Random(1), layer=1, index=1, local=nome)
        assert area["text"].startswith(f"{nome}. {texto}")
    assert set(tables.LOCAL_TEXTOS) == {nome for nome, _ in tables.LOCAIS}


def test_tower_extras_come_from_the_details_effects_not_from_chances():
    import math

    from ynn.generator import (
        TORRE_INCLINA_COM,
        TORRE_INCLINACAO_GRAUS,
        TORRE_SEM_TELHADO_COM,
        sortear_extras_torre,
    )

    # a torre do livro é sempre coberta de hera
    assert all(sortear_extras_torre(random.Random(s), 3)["trepadeiras"] for s in range(50))
    # sem efeito nenhum: telhado inteiro e torre reta
    neutro = sortear_extras_torre(random.Random(1), 3, ("vazio",))
    assert neutro["topo"] is None and neutro["inclinacao"] is None
    # o chão que se mexe inclina a torre
    for efeito in TORRE_INCLINA_COM:
        e = sortear_extras_torre(random.Random(2), 3, (efeito,))
        assert TORRE_INCLINACAO_GRAUS[0] <= e["inclinacao"]["graus"] <= TORRE_INCLINACAO_GRAUS[1]
        assert 0.0 <= e["inclinacao"]["azimute"] < 2 * math.pi
    # fogo queima o telhado; mato abre caminho e algo brota no topo
    for efeito in ("queimado", "fumegante"):
        assert sortear_extras_torre(random.Random(3), 3, (efeito,))["topo"][1] is None
    brotos = {sortear_extras_torre(random.Random(s), 3, ("fertil",))["topo"][1] for s in range(200)}
    assert brotos and None not in brotos


def test_tower_top_species_exist_and_respect_bands():
    from gielis.plants import SPECIES

    from ynn import tables
    from ynn.generator import TORRE_TOPO_VARIANTES, sortear_extras_torre

    for _texto, especie, _bandas in tables.TORRE_BROTO:
        assert especie in SPECIES and especie in TORRE_TOPO_VARIANTES
    externo = {sortear_extras_torre(random.Random(s), 1, ("fertil",))["topo"][1] for s in range(300)}
    selvagem = {sortear_extras_torre(random.Random(s), 5, ("fertil",))["topo"][1] for s in range(300)}
    assert externo <= {"arvore", "arbusto", "flor"} and "cogumelo" in selvagem


def test_a_burned_tower_loses_its_roof_and_tilting_details_tilt_it(tmp_path):
    plot = {"tipo": "torre", "x": 0.0, "z": 0.0, "detalhe": {"efeitos": ["queimado"], "texto": "x", "tipo_relevo": "plano"}}
    generator._preencher_lote(random.Random(3), 3, plot, 1, str(tmp_path), ["queimado"])
    assert "telhado" not in plot["malhas"] and "topo_obj" not in plot and plot["conteudo"]["topo_queimado"]["texto"]
    assert plot["estado"] == "ruina" and "inclinacao" not in plot
    torta = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(3), 3, torta, 2, str(tmp_path), ["convulso"])
    assert torta["inclinacao"]["graus"] > 3.9 and "telhado" in torta["malhas"]  # inclinada e com telhado
    inteira = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(3), 3, inteira, 3, str(tmp_path), ["bem_cuidado"])
    assert inteira["estado"] == "intacta" and inteira["escalada"]["trepadeiras"]


def test_a_fertile_tower_grows_something_on_its_open_top(tmp_path):
    plot = {"tipo": "torre", "x": 0.0, "z": 0.0}
    generator._preencher_lote(random.Random(4), 3, plot, 1, str(tmp_path), ["fertil"])
    assert plot["conteudo"]["topo_brotado"]["especie"] and plot["topo_obj"] and "telhado" not in plot["malhas"]
