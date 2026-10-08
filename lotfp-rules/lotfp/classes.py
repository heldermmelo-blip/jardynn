"""Estatísticas de nível 1 por classe, conferidas contra o livro de regras
(tabelas de cada classe e de Pontos de Vida / Bônus de Ataque). Ver NOTES.md.
"""

CLASSES = {
    "fighter": {
        "nome": "Fighter",
        "dado_de_vida": 8,
        "pontos_de_vida_minimos": 8,
        "bonus_ataque_nivel_1": 2,
    },
    "specialist": {
        "nome": "Specialist",
        "dado_de_vida": 6,
        "pontos_de_vida_minimos": 4,
        "bonus_ataque_nivel_1": 1,
        "pontos_pericia_nivel_1": 4,
    },
    "magic_user": {
        "nome": "Magic-User",
        "dado_de_vida": 6,
        "pontos_de_vida_minimos": 3,
        "bonus_ataque_nivel_1": 1,
    },
    "cleric": {
        "nome": "Cleric",
        "dado_de_vida": 6,
        "pontos_de_vida_minimos": 4,
        "bonus_ataque_nivel_1": 1,
    },
}
