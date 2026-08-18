"""Perícias do Thief: percentuais de nível 1 (rola d100, sucesso se <= valor).

Mecânica percentual clássica do B/X — diferente do d6-igual-ou-abaixo do
Specialist de `lotfp-rules`.

⚠ Os valores percentuais de nível 1 abaixo são minha melhor estimativa da
tabela clássica, de memória — confira contra o Rules Tome. Ver NOTES.md.
"""

THIEF_SKILLS_LEVEL_1 = {
    "Abrir Fechaduras": 15,
    "Remover Armadilhas": 10,
    "Bater Carteiras": 20,
    "Mover-se em Silêncio": 20,
    "Escalar Superfícies Íngremes": 87,
    "Esconder-se nas Sombras": 10,
}


def roll_skill(rng, skill):
    """Rola d100 contra a perícia `skill` do Thief. Retorna
    `(rolagem, alvo, sucesso)` — sucesso se a rolagem for <= ao alvo."""
    target = THIEF_SKILLS_LEVEL_1[skill]
    roll = rng.randint(1, 100)
    return roll, target, roll <= target
