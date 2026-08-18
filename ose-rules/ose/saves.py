"""Testes de Resistência (saving throws) de nível 1.

As 5 categorias abaixo são as clássicas do B/X (Moldvay/Cook) — a mesma
estrutura reproduzida, como Open Game Content, por praticamente todo
retroclone do gênero (Basic Fantasy RPG, Labyrinth Lord, OSRIC etc.), e
presumivelmente a mesma usada pelo OSE. Mecânica: rola 1d20; sucesso se
o resultado for >= ao valor-alvo (quanto menor o alvo, mais fácil passar).

⚠ Os valores-alvo por classe no nível 1 são minha melhor estimativa da
tabela clássica, de memória — confira contra o Rules Tome antes de usar
em mesa séria. Ver NOTES.md.
"""

SAVE_CATEGORIES = [
    "Morte ou Veneno",
    "Varinhas",
    "Paralisia ou Petrificação",
    "Sopro de Dragão",
    "Cajados, Bastões ou Magias",
]

SAVES_LEVEL_1 = {
    "fighter": {
        "Morte ou Veneno": 12,
        "Varinhas": 13,
        "Paralisia ou Petrificação": 14,
        "Sopro de Dragão": 15,
        "Cajados, Bastões ou Magias": 16,
    },
    "cleric": {
        "Morte ou Veneno": 11,
        "Varinhas": 12,
        "Paralisia ou Petrificação": 14,
        "Sopro de Dragão": 16,
        "Cajados, Bastões ou Magias": 15,
    },
    "magic_user": {
        "Morte ou Veneno": 13,
        "Varinhas": 14,
        "Paralisia ou Petrificação": 13,
        "Sopro de Dragão": 16,
        "Cajados, Bastões ou Magias": 15,
    },
    "thief": {
        "Morte ou Veneno": 13,
        "Varinhas": 14,
        "Paralisia ou Petrificação": 13,
        "Sopro de Dragão": 16,
        "Cajados, Bastões ou Magias": 15,
    },
    "dwarf": {
        "Morte ou Veneno": 8,
        "Varinhas": 9,
        "Paralisia ou Petrificação": 10,
        "Sopro de Dragão": 13,
        "Cajados, Bastões ou Magias": 12,
    },
    "elf": {
        "Morte ou Veneno": 12,
        "Varinhas": 13,
        "Paralisia ou Petrificação": 13,
        "Sopro de Dragão": 15,
        "Cajados, Bastões ou Magias": 15,
    },
    "halfling": {
        "Morte ou Veneno": 8,
        "Varinhas": 9,
        "Paralisia ou Petrificação": 10,
        "Sopro de Dragão": 13,
        "Cajados, Bastões ou Magias": 12,
    },
}


def roll_save(rng, class_key, category):
    """Rola 1d20 contra o Teste de Resistência `category` da classe
    `class_key`. Retorna `(rolagem, alvo, sucesso)`."""
    target = SAVES_LEVEL_1[class_key][category]
    roll = rng.randint(1, 20)
    return roll, target, roll >= target
