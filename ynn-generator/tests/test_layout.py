import random

import pytest

from ynn.layout import generate_layout


def test_generate_layout_returns_expected_plot_count():
    rng = random.Random(1)
    result = generate_layout(
        rng,
        n_areas=5,
        n_torres_range=(1, 1),
        n_estufas_range=(2, 2),
        n_canteiros_range=(3, 3),
        n_gazebos_range=(2, 2),
    )
    assert len(result["plots"]) == 1 + 2 + 3 + 2 + 5

    counts = {}
    for plot in result["plots"]:
        counts[plot["tipo"]] = counts.get(plot["tipo"], 0) + 1
    assert counts == {"torre": 1, "estufa": 2, "canteiro": 3, "gazebo": 2, "area": 5}


def test_default_layout_includes_at_least_one_gazebo():
    for seed in range(20):
        result = generate_layout(random.Random(seed), n_areas=3)
        assert any(plot["tipo"] == "gazebo" for plot in result["plots"])


def test_area_plots_have_matching_indices():
    rng = random.Random(2)
    result = generate_layout(rng, n_areas=4)
    area_indices = sorted(p["area_index"] for p in result["plots"] if p["tipo"] == "area")
    assert area_indices == [1, 2, 3, 4]


def test_non_area_plots_have_no_area_index():
    rng = random.Random(3)
    result = generate_layout(rng, n_areas=3)
    for plot in result["plots"]:
        if plot["tipo"] != "area":
            assert "area_index" not in plot


def test_plots_stay_within_field_bounds():
    rng = random.Random(4)
    field_width, field_depth = 105.0, 68.0
    result = generate_layout(rng, n_areas=5, field_width=field_width, field_depth=field_depth)
    for plot in result["plots"]:
        assert -field_width / 2 <= plot["x"] <= field_width / 2
        assert -field_depth / 2 <= plot["z"] <= field_depth / 2


def test_plots_do_not_overlap_the_same_cell():
    # Cada lote vem de uma célula distinta da grade (embaralhada, sem
    # reposição) — com jitter pequeno (15% do plot_size), lotes de células
    # vizinhas não deveriam colidir.
    rng = random.Random(5)
    result = generate_layout(rng, n_areas=6, plot_size=12.0)
    positions = [(p["x"], p["z"]) for p in result["plots"]]
    for i, (x1, z1) in enumerate(positions):
        for x2, z2 in positions[i + 1 :]:
            assert (x1 - x2) ** 2 + (z1 - z2) ** 2 > 0.01


def test_raises_when_grid_too_small_for_requested_plots():
    rng = random.Random(6)
    with pytest.raises(ValueError):
        generate_layout(rng, n_areas=100, field_width=20.0, field_depth=20.0, plot_size=12.0)


def test_same_seed_is_deterministic():
    result_a = generate_layout(random.Random(42), n_areas=5)
    result_b = generate_layout(random.Random(42), n_areas=5)
    assert result_a == result_b
