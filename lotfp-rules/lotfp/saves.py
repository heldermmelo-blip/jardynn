"""Testes de Resistência (saving throws) de nível 1.

Mecânica: rola 1d20; sucesso se o resultado for >= ao valor-alvo da
categoria (quanto menor o alvo, mais fácil passar). Categorias e a
estrutura de "cada classe é melhor em algumas" são clássicas do gênero,
implementadas aqui como código original.

SAVES_LEVEL_1 são os valores-alvo do nível 1 de cada classe, conferidos contra
as tabelas do livro. Ver NOTES.md.
"""

SAVE_CATEGORIES = ["Paralisia", "Veneno", "Sopro", "Dispositivos Mágicos", "Magia"]

SAVES_LEVEL_1 = {
    "fighter": {"Paralisia": 14, "Veneno": 12, "Sopro": 15, "Dispositivos Mágicos": 13, "Magia": 16},
    "specialist": {"Paralisia": 14, "Veneno": 16, "Sopro": 15, "Dispositivos Mágicos": 14, "Magia": 14},
    "magic_user": {"Paralisia": 13, "Veneno": 13, "Sopro": 16, "Dispositivos Mágicos": 13, "Magia": 14},
    "cleric": {"Paralisia": 14, "Veneno": 11, "Sopro": 16, "Dispositivos Mágicos": 12, "Magia": 15},
}


def roll_save(rng, class_key, category):
    """Rola 1d20 contra o Teste de Resistência `category` da classe
    `class_key`. Retorna `(rolagem, alvo, sucesso)`."""
    target = SAVES_LEVEL_1[class_key][category]
    roll = rng.randint(1, 20)
    return roll, target, roll >= target
