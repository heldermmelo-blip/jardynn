import random

from ynn.generator import band_for_layer, generate_area, generate_layer


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
