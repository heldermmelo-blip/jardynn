"""Equipamento inicial e carga (encumbrance) por slots.

⚠ A lista de equipamento inicial e a fórmula de `slot_limit` são minha
melhor estimativa da mecânica de carga, não uma transcrição do livro.
Ver NOTES.md.
"""

STARTING_EQUIPMENT = [
    ("Mochila", 1),
    ("Ração de viagem (1 semana)", 1),
    ("Cantil de água", 1),
    ("Corda (15m)", 1),
    ("Pederneira e isqueiro", 1),
    ("Tocha (3)", 1),
]


def slot_limit(strength_score):
    """Quantidade de slots que o personagem carrega sem penalidade,
    proporcional à Força."""
    return 10 + max(0, strength_score - 10)


def total_slots(equipment):
    return sum(slots for _, slots in equipment)
