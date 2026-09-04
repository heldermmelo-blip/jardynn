import random

from ynn.terrain import _nearest_valid_size, generate_terrain
from ynn.generator import generate_terreno


def test_nearest_valid_size_rounds_up_to_power_of_two_plus_one():
    assert _nearest_valid_size(1) == 3
    assert _nearest_valid_size(3) == 3
    assert _nearest_valid_size(4) == 5
    assert _nearest_valid_size(9) == 9
    assert _nearest_valid_size(10) == 17


def test_generate_terrain_grid_is_square_with_requested_resolution():
    rng = random.Random(1)
    terreno = generate_terrain(rng, "jardim_externo", resolution=9)
    assert terreno["resolucao"] == 9
    assert len(terreno["alturas"]) == 9
    assert all(len(row) == 9 for row in terreno["alturas"])


def test_flat_type_produces_all_zero_grid():
    found_flat = False
    for seed in range(200):
        terreno = generate_terrain(random.Random(seed), "jardim_externo", resolution=5)
        if terreno["tipo_relevo"] == "plano":
            found_flat = True
            assert all(altura == 0.0 for row in terreno["alturas"] for altura in row)
    assert found_flat


def test_varying_type_produces_non_constant_grid():
    found_varying = False
    for seed in range(200):
        terreno = generate_terrain(random.Random(seed), "nucleo_selvagem", resolution=9)
        if terreno["tipo_relevo"] != "plano":
            found_varying = True
            alturas_planas = [altura for row in terreno["alturas"] for altura in row]
            assert len(set(alturas_planas)) > 1
    assert found_varying


def test_same_seed_is_deterministic():
    terreno_a = generate_terrain(random.Random(42), "jardim_profundo", resolution=9)
    terreno_b = generate_terrain(random.Random(42), "jardim_profundo", resolution=9)
    assert terreno_a == terreno_b


def test_generate_terreno_uses_band_for_layer():
    rng = random.Random(3)
    terreno = generate_terreno(rng, layer=5, resolution=5, cell_size=1.5)
    assert terreno["tamanho_celula"] == 1.5
    assert terreno["resolucao"] == 5
