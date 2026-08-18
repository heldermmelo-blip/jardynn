"""Estatísticas de nível 1 por classe.

⚠ dado_de_vida, bonus_ataque_nivel_1 e pontos_pericia_nivel_1 são minha
melhor estimativa do sistema, não uma transcrição do livro — confira
contra sua cópia de LotFP antes de usar em mesa. Ver NOTES.md.
"""

CLASSES = {
    "fighter": {
        "nome": "Fighter",
        "dado_de_vida": 8,
        "bonus_ataque_nivel_1": 1,
    },
    "specialist": {
        "nome": "Specialist",
        "dado_de_vida": 6,
        "bonus_ataque_nivel_1": 0,
        "pontos_pericia_nivel_1": 4,
    },
    "magic_user": {
        "nome": "Magic-User",
        "dado_de_vida": 4,
        "bonus_ataque_nivel_1": 0,
    },
    "cleric": {
        "nome": "Cleric",
        "dado_de_vida": 6,
        "bonus_ataque_nivel_1": 0,
    },
}
