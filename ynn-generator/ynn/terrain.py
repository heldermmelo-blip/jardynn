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

import math

from . import tables

AMPLITUDE_POR_TIPO = {"plano": 0.0, "leve": 0.5, "acentuado": 1.2, "irregular": 2.0}
RELEVO_ORDEM = ["plano", "leve", "acentuado", "irregular"]
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


def generate_terrain_localizado(rng, pontos, resolution=65, cell_size=2.0, raio_influencia=18.0):
    """Relevo que varia só ao redor de cada local, conforme o detalhe dele.

    `pontos` é uma lista de `(x, z, tipo_relevo)` em coordenadas de mundo.
    Uma única grade de ruído diamond-square é multiplicada, em cada ponto
    da grade, pela maior "influência" entre os locais: a amplitude do
    `tipo_relevo` do local vezes uma gaussiana da distância até ele
    (`raio_influencia` em metros). Longe de qualquer local de relevo
    variável, o chão é plano."""
    size = _nearest_valid_size(resolution)
    base = _diamond_square(rng, size, 2.5, 0.6)
    meia = (size - 1) / 2
    ativos = [(x, z, AMPLITUDE_POR_TIPO[tipo]) for x, z, tipo in pontos if AMPLITUDE_POR_TIPO[tipo] > 0.0]

    alturas = []
    for j in range(size):
        z = (j - meia) * cell_size
        linha = []
        for i in range(size):
            x = (i - meia) * cell_size
            peso = 0.0
            for px, pz, amplitude in ativos:
                d2 = (x - px) ** 2 + (z - pz) ** 2
                peso = max(peso, amplitude * math.exp(-d2 / (raio_influencia**2)))
            linha.append(base[j][i] * peso)
        alturas.append(linha)

    mais_forte = max((tipo for _, _, tipo in pontos), key=RELEVO_ORDEM.index, default="plano")
    descricao = (
        "O relevo varia ao redor de cada local, conforme o detalhe dele."
        if ativos
        else "Terreno nivelado em todo o nível."
    )
    return {
        "descricao": descricao,
        "tipo_relevo": mais_forte,
        "resolucao": size,
        "tamanho_celula": cell_size,
        "alturas": alturas,
        "localizado": True,
    }


def achatar_circulo(terreno, x, z, raio, margem=3.0):
    """Aplaina (z = 0) o relevo dentro de um círculo de `raio` metros em
    (x, z), com uma rampa suave de `margem` metros até o relevo original —
    pra pôr um espelho d'água sem o chão furar a superfície. Altera
    `terreno["alturas"]` no lugar."""
    size = terreno["resolucao"]
    cell = terreno["tamanho_celula"]
    meia = (size - 1) / 2
    for j in range(size):
        pz = (j - meia) * cell
        for i in range(size):
            px = (i - meia) * cell
            d = math.hypot(px - x, pz - z)
            if d >= raio + margem:
                continue
            peso = 0.0 if d <= raio else (d - raio) / margem
            terreno["alturas"][j][i] *= peso
