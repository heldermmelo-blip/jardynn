"""Feitiços de nível 1 (Magic-User/Elf) e vagas de magia por classe.

Os nomes de feitiço abaixo são os clássicos do B/X (Analyze, Charm
Person, Detect Magic etc.) — amplamente reproduzidos como Open Game
Content em praticamente todo retroclone do gênero. As descrições são um
resumo conciso, nas minhas palavras, do efeito clássico de cada um, não
uma transcrição literal do Rules Tome.

⚠ SPELL_SLOTS_LEVEL_1 reflete uma estrutura do B/X clássico da qual tenho
razoável confiança (Magic-User e Elf preparam 1 magia de nível 1; Cleric
NÃO tem magia no nível 1 — só passa a rezar a partir do nível 2), mas
confira contra o Rules Tome. Ver NOTES.md.
"""

SPELL_SLOTS_LEVEL_1 = {
    "magic_user": 1,
    "elf": 1,
    "cleric": 0,
}

SPELLS = {
    "magic_user": [
        {"nome": "Charm Person", "descricao": "Domina a vontade de um humanoide, que passa a tratar o conjurador como amigo de confiança."},
        {"nome": "Detect Magic", "descricao": "Revela quais objetos ou pontos próximos têm encantamento, por um tempo curto."},
        {"nome": "Floating Disc", "descricao": "Cria um disco invisível flutuante que carrega peso e segue o conjurador."},
        {"nome": "Hold Portal", "descricao": "Tranca magicamente uma porta ou portal por um tempo."},
        {"nome": "Light", "descricao": "Cria uma fonte de luz que passa a seguir um objeto ou ponto indicado."},
        {"nome": "Protection from Evil", "descricao": "Cria uma barreira que dificulta o contato e os ataques de criaturas malignas ou invocadas."},
        {"nome": "Read Languages", "descricao": "Permite ler textos em idiomas desconhecidos ou mapas cifrados por um tempo."},
        {"nome": "Read Magic", "descricao": "Permite compreender inscrições e pergaminhos mágicos — necessário para copiar magias para o próprio grimório."},
        {"nome": "Sleep", "descricao": "Faz um pequeno grupo de criaturas fracas cair num sono súbito e profundo."},
        {"nome": "Ventriloquism", "descricao": "Faz a própria voz parecer vir de outro lugar à escolha do conjurador."},
    ],
    "cleric": [
        {"nome": "Cure Light Wounds", "descricao": "Restaura uma pequena quantidade de pontos de vida ao toque (disponível a partir do nível 2)."},
        {"nome": "Detect Evil", "descricao": "Revela a presença de intenção ou influência maligna nas proximidades (disponível a partir do nível 2)."},
        {"nome": "Protection from Evil", "descricao": "Cria uma barreira que dificulta o contato e os ataques de criaturas malignas (disponível a partir do nível 2)."},
        {"nome": "Purify Food and Water", "descricao": "Remove contaminação e veneno de comida e bebida (disponível a partir do nível 2)."},
    ],
}


def prepare_spells(rng, class_key):
    """Sorteia as magias de nível 1 preparadas para uma classe conjuradora,
    respeitando o número de vagas em `SPELL_SLOTS_LEVEL_1`. Cleric tem 0
    vagas no nível 1 — sempre retorna lista vazia. Elf usa a lista de
    Magic-User. Retorna lista vazia para classes não-conjuradoras."""
    spell_list_key = "magic_user" if class_key == "elf" else class_key
    available = SPELLS.get(spell_list_key)
    if not available:
        return []
    n_slots = min(SPELL_SLOTS_LEVEL_1.get(class_key, 0), len(available))
    return rng.sample(available, n_slots)
