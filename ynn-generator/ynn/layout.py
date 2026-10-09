"""Layout espacial 2D de uma camada — em vez de uma linha reta de áreas,
distribui áreas e estruturas (torres, estufas, gazebos, canteiros) por uma grade de
lotes sobre um terreno do tamanho de um campo de futebol (padrão FIFA:
105m x 68m).

Cada lote é sorteado sem repetição de uma grade de células de
`plot_size` metros (mais um leve jitter, pra não ficar visualmente
perfeito demais); `x`/`z` vêm em coordenadas de mundo já centradas na
origem, no mesmo sistema usado pelo terreno (`ynn.terrain`).
"""

FIELD_WIDTH = 105.0
FIELD_DEPTH = 68.0
PLOT_SIZE = 12.0

N_TORRES_RANGE = (1, 1)
N_ESTUFAS_RANGE = (1, 2)
N_CANTEIROS_RANGE = (1, 3)
N_GAZEBOS_RANGE = (1, 2)


def _grid_cells(field_width, field_depth, plot_size):
    """Todas as células `(coluna, linha)` da grade de lotes que cabem no campo (no mínimo 1x1)."""
    cols = max(1, int(field_width // plot_size))
    rows = max(1, int(field_depth // plot_size))
    return [(c, r) for c in range(cols) for r in range(rows)]


def _cell_to_world(rng, cell, field_width, field_depth, plot_size):
    """Centro da célula em coordenadas de mundo (campo centrado na origem), com jitter de até 15% de `plot_size`
    em cada eixo."""
    col, row = cell
    jitter = plot_size * 0.15
    x = (col + 0.5) * plot_size - field_width / 2 + rng.uniform(-jitter, jitter)
    z = (row + 0.5) * plot_size - field_depth / 2 + rng.uniform(-jitter, jitter)
    return x, z


def generate_layout(
    rng,
    n_areas,
    field_width=FIELD_WIDTH,
    field_depth=FIELD_DEPTH,
    plot_size=PLOT_SIZE,
    n_torres_range=N_TORRES_RANGE,
    n_estufas_range=N_ESTUFAS_RANGE,
    n_canteiros_range=N_CANTEIROS_RANGE,
    n_gazebos_range=N_GAZEBOS_RANGE,
):
    """Sorteia os lotes de uma camada: quantas torres, estufas, canteiros e gazebos (dentro dos intervalos
    `n_*_range`, inclusivos) mais `n_areas` áreas numeradas de 1 a `n_areas`, cada um numa célula diferente.
    Devolve `field_width`, `field_depth`, `plot_size` e `plots` (lista de `{tipo, x, z}`; as áreas levam também
    `area_index`). Levanta `ValueError` se a grade não tiver lotes suficientes."""
    cells = _grid_cells(field_width, field_depth, plot_size)
    # embaralha uma vez; cada lote pega a próxima célula, então nunca há dois no mesmo lugar
    rng.shuffle(cells)

    n_torres = rng.randint(*n_torres_range)
    n_estufas = rng.randint(*n_estufas_range)
    n_canteiros = rng.randint(*n_canteiros_range)
    n_gazebos = rng.randint(*n_gazebos_range)
    n_needed = n_torres + n_estufas + n_canteiros + n_gazebos + n_areas
    if n_needed > len(cells):
        raise ValueError(
            f"grade de {len(cells)} lotes ({plot_size}m) é pequena demais para "
            f"{n_needed} lotes pedidos num campo de {field_width}x{field_depth}m — "
            "aumente field_width/field_depth ou diminua plot_size/n_areas"
        )

    plots = []
    idx = 0

    def _take(n, tipo, area_index=None):
        """Consome as próximas `n` células embaralhadas e cria um lote de `tipo` em cada uma; `area_index` só vai nos lotes de área."""
        nonlocal idx
        for _ in range(n):
            x, z = _cell_to_world(rng, cells[idx], field_width, field_depth, plot_size)
            idx += 1
            plot = {"tipo": tipo, "x": x, "z": z}
            if area_index is not None:
                plot["area_index"] = area_index
            plots.append(plot)

    _take(n_torres, "torre")
    _take(n_estufas, "estufa")
    _take(n_canteiros, "canteiro")
    _take(n_gazebos, "gazebo")
    for area_index in range(1, n_areas + 1):
        _take(1, "area", area_index=area_index)

    return {
        "field_width": field_width,
        "field_depth": field_depth,
        "plot_size": plot_size,
        "plots": plots,
    }
