"""Atributos: rolagem 3d6 em ordem e tabela de modificadores.

Escala de modificador clássica do OSR (usada por LotFP e a maioria dos
retroclones): 3=-3, 4-5=-2, 6-8=-1, 9-12=0, 13-15=+1, 16-17=+2, 18=+3.
"""

ABILITY_NAMES = ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"]


def roll_3d6(rng):
    return sum(rng.randint(1, 6) for _ in range(3))


def modifier(score):
    if score <= 3:
        return -3
    if score <= 5:
        return -2
    if score <= 8:
        return -1
    if score <= 12:
        return 0
    if score <= 15:
        return 1
    if score <= 17:
        return 2
    return 3


def roll_abilities(rng):
    return {name: roll_3d6(rng) for name in ABILITY_NAMES}
