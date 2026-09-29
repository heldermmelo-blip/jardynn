import os
import random

from ynn.generator import band_for_layer, generate_area, generate_layer, generate_layout_camada


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
        rng, layer=1, n_areas=2, n_torres_range=(1, 1), n_estufas_range=(1, 1), n_canteiros_range=(1, 1)
    )
    by_tipo = {}
    for plot in camada_layout["plots"]:
        by_tipo.setdefault(plot["tipo"], []).append(plot)

    torre = by_tipo["torre"][0]
    assert os.path.exists(torre["obj"])
    assert os.path.getsize(torre["obj"]) > 0

    estufa = by_tipo["estufa"][0]
    assert os.path.exists(estufa["obj"])
    assert os.path.getsize(estufa["obj"]) > 0

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


def test_ground_cover_vegetation_has_no_species():
    from ynn import tables

    ground_cover_entries = [
        (text, species) for text, bands, species in tables.VEGETATION if "gramado" in text.lower() or "musgo" in text.lower()
    ]
    assert ground_cover_entries
    assert all(species is None for _, species in ground_cover_entries)
