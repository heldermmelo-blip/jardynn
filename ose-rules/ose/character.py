"""Monta um personagem completo de nível 1.

CA (Classe de Armadura) aqui é **descendente**, como no B/X clássico:
9 é o padrão desarmado/sem armadura, e valores menores são melhores.
Isso é o oposto da convenção ascendente usada em `lotfp-rules`.
"""

from . import abilities, classes, equipment, saves, skills, spells

BASE_AC = 9


def create_character(rng, class_key):
    """Gera um personagem de nível 1 da classe `class_key` (chave de `classes.CLASSES`).
    Rola os atributos em ordem, PV (dado de vida + mod. de Constituição, mínimo 1), CA descendente
    (`BASE_AC` menos o mod. de Destreza), bônus de ataque, equipamento e testes de resistência.
    Thief ganha perícias percentuais; Magic-User e Elf ganham magias preparadas e grimório. Devolve um dict
    serializável em JSON, com chaves em português."""
    class_data = classes.CLASSES[class_key]
    ability_scores = abilities.roll_abilities(rng)
    modifiers = {name: abilities.modifier(score) for name, score in ability_scores.items()}
    con_mod = modifiers["Constituição"]
    dex_mod = modifiers["Destreza"]
    # PV = dado de vida + mod. de Constituição, nunca menos que 1
    hp = max(1, rng.randint(1, class_data["dado_de_vida"]) + con_mod)

    character = {
        "classe": class_data["nome"],
        "atributos": ability_scores,
        "modificadores": modifiers,
        "pontos_de_vida": hp,
        # CA descendente: Destreza alta reduz o valor, que é a defesa melhor
        "classe_de_armadura": BASE_AC - dex_mod,
        "bonus_ataque": class_data["bonus_ataque_nivel_1"],
        "equipamento": list(equipment.STARTING_EQUIPMENT),
        "testes_de_resistencia": dict(saves.SAVES_LEVEL_1[class_key]),
    }

    if class_key == "thief":
        character["pericias"] = dict(skills.THIEF_SKILLS_LEVEL_1)

    # Cleric tem 0 vagas no nível 1: `prepare_spells` devolve lista vazia e nada é gravado
    if class_key in classes.CASTS_MAGIC_USER_SPELLS or class_key == "cleric":
        prepared = spells.prepare_spells(rng, class_key)
        if prepared:
            character["magias_preparadas"] = prepared
            if class_key in classes.CASTS_MAGIC_USER_SPELLS:
                character["grimorio"] = list(prepared)

    return character
