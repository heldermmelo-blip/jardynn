"""Geração do relevo (grade de pontos com altura) de uma camada.

O "descritor de localidade" é sorteado uma vez por camada em
`tables.LOCALIDADE`, filtrado por banda como as demais tabelas. O
`tipo_relevo` resultante decide a amplitude do heightmap: `"plano"` não
gera variação nenhuma; os demais usam o algoritmo diamond-square (puro
Python, sem numpy) para uma grade quadrada de alturas determinística a
partir do `rng` recebido.

O resultado é uma grade de pontos (heightmap), não uma malha triangulada
— isso fica a cargo de quem consome o JSON (ex. `Main.gd`, via
`SurfaceTool`).
"""

from . import tables

AMPLITUDE_POR_TIPO = {"plano": 0.0, "leve": 0.5, "acentuado": 1.2, "irregular": 2.0}
RUGOSIDADE_POR_TIPO = {"plano": 0.5, "leve": 0.55, "acentuado": 0.6, "irregular": 0.75}


def _localidade_for_band(band):
    return [(text, tipo) for text, bands, tipo in tables.LOCALIDADE if bands == "all" or band in bands]


def _pick_localidade(rng, band):
    return rng.choice(_localidade_for_band(band))


def _nearest_valid_size(resolution):
    """Menor tamanho de grade `2**n + 1` (exigido pelo diamond-square) >= resolution."""
    n = 1
    while (2**n) + 1 < resolution:
        n += 1
    return (2**n) + 1


def _flat_grid(size):
    return [[0.0] * size for _ in range(size)]


def _diamond_square(rng, size, amplitude, rugosidade):
    grid = _flat_grid(size)
    last = size - 1
    grid[0][0] = rng.uniform(-amplitude, amplitude)
    grid[0][last] = rng.uniform(-amplitude, amplitude)
    grid[last][0] = rng.uniform(-amplitude, amplitude)
    grid[last][last] = rng.uniform(-amplitude, amplitude)

    step = last
    scale = amplitude
    while step > 1:
        half = step // 2

        # passo diamante: centro de cada quadrado = média dos 4 cantos
        for y in range(half, size, step):
            for x in range(half, size, step):
                media = (grid[y - half][x - half] + grid[y - half][x + half] + grid[y + half][x - half] + grid[y + half][x + half]) / 4.0
                grid[y][x] = media + rng.uniform(-scale, scale)

        # passo quadrado: centro de cada losango = média dos vizinhos existentes
        for y in range(0, size, half):
            start_x = half if y % step == 0 else 0
            for x in range(start_x, size, step):
                vizinhos = []
                if y - half >= 0:
                    vizinhos.append(grid[y - half][x])
                if y + half < size:
                    vizinhos.append(grid[y + half][x])
                if x - half >= 0:
                    vizinhos.append(grid[y][x - half])
                if x + half < size:
                    vizinhos.append(grid[y][x + half])
                grid[y][x] = sum(vizinhos) / len(vizinhos) + rng.uniform(-scale, scale)

        step = half
        scale *= rugosidade

    return grid


def generate_terrain(rng, band, resolution=65, cell_size=2.0):
    texto, tipo_relevo = _pick_localidade(rng, band)
    size = _nearest_valid_size(resolution)
    amplitude = AMPLITUDE_POR_TIPO[tipo_relevo]

    if amplitude == 0.0:
        alturas = _flat_grid(size)
    else:
        alturas = _diamond_square(rng, size, amplitude, RUGOSIDADE_POR_TIPO[tipo_relevo])

    return {
        "descricao": texto,
        "tipo_relevo": tipo_relevo,
        "resolucao": size,
        "tamanho_celula": cell_size,
        "alturas": alturas,
    }
