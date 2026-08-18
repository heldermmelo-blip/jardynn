"""Estatísticas de nível 1 por classe — as 4 classes humanas clássicas mais
as 3 demi-humanas (B/X usa "raça como classe": Dwarf, Elf e Halfling são
cada uma sua própria classe, não uma raça combinável com outra classe).

⚠ dado_de_vida e bonus_ataque_nivel_1 são minha melhor estimativa da
estrutura do B/X/OSE — confira contra o Rules Tome (a declaração de Open
Game Content fica na Section 15, no final do livro). Ver NOTES.md.
"""

CLASSES = {
    "fighter": {"nome": "Fighter", "dado_de_vida": 8, "bonus_ataque_nivel_1": 1},
    "cleric": {"nome": "Cleric", "dado_de_vida": 6, "bonus_ataque_nivel_1": 0},
    "magic_user": {"nome": "Magic-User", "dado_de_vida": 4, "bonus_ataque_nivel_1": 0},
    "thief": {"nome": "Thief", "dado_de_vida": 4, "bonus_ataque_nivel_1": 0},
    "dwarf": {"nome": "Dwarf", "dado_de_vida": 8, "bonus_ataque_nivel_1": 1},
    "elf": {"nome": "Elf", "dado_de_vida": 6, "bonus_ataque_nivel_1": 0},
    "halfling": {"nome": "Halfling", "dado_de_vida": 6, "bonus_ataque_nivel_1": 0},
}

# Elf combina luta e magia (a marca registrada da classe no B/X): conjura
# como Magic-User além de lutar. Ver spells.py.
CASTS_MAGIC_USER_SPELLS = {"magic_user", "elf"}
