import random

from ynn.terrain import _nearest_valid_size, generate_terrain, generate_terrain_localizado
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


def test_localized_terrain_is_flat_when_every_detail_is_flat():
    terreno = generate_terrain_localizado(random.Random(1), [(0, 0, "plano"), (10, 10, "plano")], resolution=17)
    assert all(h == 0.0 for row in terreno["alturas"] for h in row)
    assert terreno["tipo_relevo"] == "plano"


def test_localized_terrain_varies_only_near_the_local_that_asks_for_it():
    cell = 4.0
    resolution = 33
    terreno = generate_terrain_localizado(
        random.Random(2), [(-30.0, 0.0, "irregular")], resolution=resolution, cell_size=cell, raio_influencia=12.0
    )
    meia = (resolution - 1) / 2

    def desvio(x_ini, x_fim):
        valores = []
        for j in range(resolution):
            for i in range(resolution):
                x = (i - meia) * cell
                if x_ini <= x <= x_fim:
                    valores.append(abs(terreno["alturas"][j][i]))
        return max(valores)

    assert desvio(-40, -20) > 0.1  # perto do local irregular, o chão varia
    assert desvio(30, 60) < 1e-3  # longe dele, fica plano
    assert terreno["tipo_relevo"] == "irregular"


def test_localized_terrain_strongest_type_and_determinism():
    pontos = [(0, 0, "leve"), (20, 0, "acentuado")]
    a = generate_terrain_localizado(random.Random(3), pontos, resolution=17)
    b = generate_terrain_localizado(random.Random(3), pontos, resolution=17)
    assert a == b
    assert a["tipo_relevo"] == "acentuado"
