import os
import random

from ynn.generator import band_for_layer, generate_area, generate_layer, generate_layout_camada, generate_torre_conteudo


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


def test_fallen_branches_produce_meshes_and_are_rare():
    found_branches = False
    triggered = 0
    n_seeds = 60
    for seed in range(n_seeds):
        area = generate_area(random.Random(seed), layer=1, index=1)
        if area["galhos_caidos_obj"]:
            found_branches = True
            triggered += 1
            assert 1 <= len(area["galhos_caidos_obj"]) <= 3  # FALLEN_BRANCH_COUNT_RANGE
            for path in area["galhos_caidos_obj"]:
                assert os.path.exists(path)
                assert os.path.getsize(path) > 0
            assert "galhos cortados ou caídos" in area["text"]
    assert found_branches
    # FALLEN_BRANCH_CHANCE é 1/6 (~16.7%); com só 60 seeds (rápido, dado o
    # custo de gerar malhas), a margem tem que ser bem folgada (~5 desvios
    # padrão) pra não falhar por azar estatístico — o objetivo aqui é só
    # pegar um bug grosseiro (chance trocada por 1.0, nunca dispara etc.),
    # não validar a taxa exata.
    assert 0.03 < triggered / n_seeds < 0.45


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
    assert torre["conteudo"]["n_andares"] == len(torre["conteudo"]["andares"])
    assert len(torre["hera_obj"]) >= 3  # IVY_VARIANT_RANGE mínimo
    for path in torre["hera_obj"]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    estufa = by_tipo["estufa"][0]
    assert os.path.exists(estufa["obj"])
    assert os.path.getsize(estufa["obj"]) > 0
    assert estufa["planta"]["dado"] in (4, 6, 8, 10, 12, 20)
    assert estufa["planta"]["portas"] == estufa["planta"]["lados"]
    assert estufa["conteudo"]["texto"]

    gazebo = by_tipo["gazebo"][0]
    assert os.path.exists(gazebo["obj"])
    assert os.path.getsize(gazebo["obj"]) > 0
    for chave in ("texto", "bibelo", "tesouro", "refugio"):
        assert gazebo["conteudo"][chave]

    canteiro = by_tipo["canteiro"][0]
    assert canteiro["especie"] in ("flor", "arbusto")
    assert len(canteiro["plantas_obj"]) >= 4  # CANTEIRO_VARIANT_RANGE mínimo
    for path in canteiro["plantas_obj"]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    assert len(by_tipo["area"]) == 2
    for plot in by_tipo["area"]:
        assert "obj" not in plot
        assert "plantas_obj" not in plot


def test_estufa_planta_follows_dice_table():
    from ynn.generator import ESTUFA_DADOS, generate_estufa_planta

    vistos = set()
    for seed in range(300):
        planta = generate_estufa_planta(random.Random(seed))
        info = ESTUFA_DADOS[planta["dado"]]
        assert planta["lados"] == info["lados"] == planta["portas"]
        assert planta["andares"] == info["andares"]
        assert planta["raio"] == info["raio"]
        vistos.add(planta["dado"])
    assert vistos == set(ESTUFA_DADOS)  # todos os tamanhos aparecem


def test_estufa_bigger_dice_are_bigger_and_taller():
    from ynn.generator import ESTUFA_DADOS

    assert ESTUFA_DADOS[12]["andares"] == 2
    assert ESTUFA_DADOS[20]["andares"] == 3
    assert all(ESTUFA_DADOS[d]["andares"] == 1 for d in (4, 6, 8, 10))
    assert ESTUFA_DADOS[4]["raio"] < ESTUFA_DADOS[12]["raio"]
    # Cabe num lote (12 m): o raio circunscrito não passa da metade do lote.
    assert all(info["raio"] <= 6.0 for info in ESTUFA_DADOS.values())


def test_estufa_conteudo_table_references_valid_creatures():
    from ynn import tables
    from ynn.creatures import CREATURES

    for texto, _bandas, tipo, criatura_key in tables.ESTUFA_CONTEUDO:
        assert tipo in ("valor", "criatura", None)
        if tipo == "criatura":
            assert criatura_key in CREATURES
        else:
            assert criatura_key is None


def test_estufa_conteudo_fills_value_or_creature():
    from ynn.generator import generate_estufa_conteudo

    visto_valor = visto_criatura = visto_simples = False
    for seed in range(200):
        layer = 3
        conteudo = generate_estufa_conteudo(random.Random(seed), layer)
        assert conteudo["texto"]
        if "valor_ouro" in conteudo:
            visto_valor = True
            assert 1 + layer <= conteudo["valor_ouro"] <= 6 + layer
        elif "criatura" in conteudo:
            visto_criatura = True
            assert conteudo["criatura"]["pontos_de_vida"] >= 1
        else:
            visto_simples = True
    assert visto_valor and visto_criatura and visto_simples


def test_estufa_conteudo_respects_bands():
    from ynn.generator import generate_estufa_conteudo

    for seed in range(200):
        conteudo = generate_estufa_conteudo(random.Random(seed), layer=1)  # jardim_externo
        assert "criatura" not in conteudo  # monstros só do jardim profundo em diante
        assert "lacrada" not in conteudo["texto"]


def test_gazebo_conteudo_fields_and_determinism():
    from ynn.generator import REFUGIO_GAZEBO, generate_gazebo_conteudo

    a = generate_gazebo_conteudo(random.Random(7), layer=3)
    b = generate_gazebo_conteudo(random.Random(7), layer=3)
    assert a == b
    assert a["refugio"] == REFUGIO_GAZEBO
    assert a["texto"] and a["bibelo"] and a["tesouro"]


def test_torre_conteudo_has_one_entry_per_floor():
    for seed in range(30):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        assert 3 <= conteudo["n_andares"] <= 8  # N_ANDARES_TORRE_RANGE
        assert len(conteudo["andares"]) == conteudo["n_andares"]
        assert [a["numero"] for a in conteudo["andares"]] == list(range(1, conteudo["n_andares"] + 1))


def test_torre_topo_is_the_last_floor_and_distinct_table():
    from ynn import tables

    topo_textos = {entrada[0] for entrada in tables.TORRE_TOPO}
    andar_textos = {entrada[0] for entrada in tables.TORRE_ANDARES}
    assert topo_textos.isdisjoint(andar_textos)

    for seed in range(30):
        conteudo = generate_torre_conteudo(random.Random(seed), layer=3)
        topo = conteudo["andares"][-1]
        assert topo["numero"] == conteudo["n_andares"]
        assert topo["texto"] in topo_textos


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
