"""Equipamento inicial e carga (encumbrance) por pontos de carga.

A carga segue a tabela do livro: ninguém soma peso; contam-se itens
diferentes (6+, 11+, 16+ e 21+ dão 1 ponto cada), cota de malha (+1), armadura
de placas (+2) e cada item de tamanho exagerado (+1). 0-1 pontos = sem
penalidade; 2 = leve; 3 = pesada; 4 = severa; 5+ = sem movimento. Ver NOTES.md.

A lista de equipamento inicial é só um kit genérico de aventureiro
(original); o livro manda comprar o equipamento com 3d6 × 10 de prata.
"""

STARTING_EQUIPMENT = [
    "Mochila",
    "Ração de viagem (1 semana)",
    "Cantil de água",
    "Corda (15m)",
    "Pederneira e isqueiro",
    "Tocha (3)",
]

# pontos de carga -> (estado, movimento de exploração por turno, em pés)
ENCUMBRANCE_LEVELS = {
    0: ("sem carga excessiva", 120),
    1: ("sem carga excessiva", 120),
    2: ("levemente sobrecarregado", 90),
    3: ("muito sobrecarregado", 60),
    4: ("severamente sobrecarregado", 30),
}
OVERLOADED = ("sem condições de se mover", 0)


def starting_money(rng):
    """Moedas de prata iniciais: 3d6 × 10."""
    return sum(rng.randint(1, 6) for _ in range(3)) * 10


def encumbrance_points(n_distinct_items, chain_armor=False, plate_armor=False, oversized_items=0):
    points = sum(1 for limite in (6, 11, 16, 21) if n_distinct_items >= limite)
    points += 1 if chain_armor else 0
    points += 2 if plate_armor else 0
    return points + oversized_items


def movement(points):
    """`(estado, pés por turno de exploração)` para os pontos de carga dados."""
    return ENCUMBRANCE_LEVELS.get(points, OVERLOADED)
