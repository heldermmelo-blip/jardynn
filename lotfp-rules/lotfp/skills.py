"""Perícias do Specialist: lista base e alocação de pontos de nível 1.

Conferido contra o livro: toda perícia "x-em-6" começa em 1-em-6 para todos
os personagens e cada ponto do Specialist soma 1 (teto 6-em-6). Ataque
Furtivo é diferente: é um multiplicador de dano (começa em ×1; cada ponto
soma +1, sem teto). Ver NOTES.md.
"""

SNEAK_ATTACK = "Sneak Attack"

SPECIALIST_SKILLS = [
    "Architecture",
    "Bushcraft",
    "Climb",
    "Languages",
    "Search",
    "Sleight of Hand",
    SNEAK_ATTACK,
    "Stealth",
    "Tinker",
]

BASE_RATING = 1
SPECIALIST_BASE_RATING = 1
MAX_RATING = 6


def allocate_skill_points(rng, points, base_ratings=None):
    """Distribui `points` aleatoriamente entre as perícias do Specialist,
    respeitando o teto de `MAX_RATING`-em-6 (menos no Ataque Furtivo, que é
    um multiplicador de dano e não tem teto)."""
    ratings = dict(base_ratings or {skill: SPECIALIST_BASE_RATING for skill in SPECIALIST_SKILLS})
    remaining = points
    while remaining > 0:
        # perícia já no teto é sorteada de novo, sem gastar o ponto
        skill = rng.choice(list(ratings.keys()))
        if skill == SNEAK_ATTACK or ratings[skill] < MAX_RATING:
            ratings[skill] += 1
            remaining -= 1
    return ratings
