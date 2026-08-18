"""Feitiços de nível 1 e vagas de magia por classe.

Mecânica vancian clássica do sistema (o conjurador prepara/reza de véspera
um número limitado de magias; lançar gasta a vaga até o dia seguinte) —
implementada como código original. Nomes, descrições e efeitos dos
feitiços abaixo são meus, não uma transcrição do livro.

⚠ SPELL_SLOTS_LEVEL_1 (quantas vagas de magia de nível 1 um Magic-User ou
Cleric de nível 1 tem) é minha melhor estimativa — confira contra o livro.
Ver NOTES.md.
"""

SPELL_SLOTS_LEVEL_1 = {
    "magic_user": 1,
    "cleric": 1,
}

SPELLS = {
    "magic_user": [
        {
            "nome": "Mísseis de Força",
            "descricao": (
                "Conjura pequenos projéteis de força pura que acertam automaticamente um "
                "alvo à vista, causando dano leve."
            ),
        },
        {
            "nome": "Detectar Magia",
            "descricao": "Permite perceber a presença e a intensidade geral de magia em objetos ou lugares próximos, por um tempo curto.",
        },
        {
            "nome": "Ler Magia",
            "descricao": (
                "Permite compreender texto escrito em código arcano — necessário para copiar "
                "magias de outra fonte para o próprio grimório."
            ),
        },
        {
            "nome": "Sono Profundo",
            "descricao": "Faz um pequeno grupo de criaturas fracas cair num sono súbito e profundo.",
        },
        {
            "nome": "Escudo Arcano",
            "descricao": "Cria uma barreira invisível que melhora a defesa do conjurador por um tempo.",
        },
        {
            "nome": "Luz",
            "descricao": "Cria uma fonte de luz que passa a seguir um objeto ou ponto indicado pelo conjurador.",
        },
    ],
    "cleric": [
        {
            "nome": "Curar Ferimentos Leves",
            "descricao": "Restaura uma pequena quantidade de pontos de vida ao toque.",
        },
        {
            "nome": "Bênção",
            "descricao": "Fortalece brevemente a resolução de aliados próximos em combate.",
        },
        {
            "nome": "Detectar o Profano",
            "descricao": "Revela a presença de corrupção ou influência sobrenatural maligna nas proximidades.",
        },
        {
            "nome": "Purificar",
            "descricao": "Remove venenos leves ou contaminação de comida e bebida, ou trata uma pequena ferida infeccionada.",
        },
    ],
}


def prepare_spells(rng, class_key):
    """Sorteia as magias de nível 1 preparadas (Magic-User) ou concedidas
    pela prece (Cleric), respeitando o número de vagas em
    `SPELL_SLOTS_LEVEL_1`. Retorna lista vazia para classes sem magia."""
    available = SPELLS.get(class_key)
    if not available:
        return []
    n_slots = min(SPELL_SLOTS_LEVEL_1.get(class_key, 0), len(available))
    return rng.sample(available, n_slots)
