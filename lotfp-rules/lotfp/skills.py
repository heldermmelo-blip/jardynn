"""Perícias do Specialist: lista base e alocação de pontos de nível 1.

⚠ A lista de perícias e os valores-base (1-em-6 geral, 2-em-6 para o
Specialist) são minha melhor estimativa — confira contra o livro.
Ver NOTES.md.
"""

SPECIALIST_SKILLS = [
    "Architecture",
    "Bushcraft",
    "Climbing",
    "Concealment",
    "Languages",
    "Search",
    "Sleight of Hand",
    "Sneak Attack",
    "Stealth",
    "Tinkering",
]

BASE_RATING = 1
SPECIALIST_BASE_RATING = 2
MAX_RATING = 6


def allocate_skill_points(rng, points, base_ratings=None):
    """Distribui `points` aleatoriamente entre as perícias do Specialist,
    respeitando o teto de `MAX_RATING`-em-6."""
    ratings = dict(base_ratings or {skill: SPECIALIST_BASE_RATING for skill in SPECIALIST_SKILLS})
    remaining = points
    while remaining > 0 and any(r < MAX_RATING for r in ratings.values()):
        skill = rng.choice(list(ratings.keys()))
        if ratings[skill] < MAX_RATING:
            ratings[skill] += 1
            remaining -= 1
    return ratings
