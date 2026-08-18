"""Monta um personagem completo de nível 1."""

from . import abilities, classes, equipment, skills


def create_character(rng, class_key):
    class_data = classes.CLASSES[class_key]
    ability_scores = abilities.roll_abilities(rng)
    con_mod = abilities.modifier(ability_scores["Constituição"])
    hp = max(1, rng.randint(1, class_data["dado_de_vida"]) + con_mod)

    character = {
        "classe": class_data["nome"],
        "atributos": ability_scores,
        "modificadores": {name: abilities.modifier(score) for name, score in ability_scores.items()},
        "pontos_de_vida": hp,
        "bonus_ataque": class_data["bonus_ataque_nivel_1"],
        "equipamento": list(equipment.STARTING_EQUIPMENT),
    }

    if class_key == "specialist":
        character["pericias"] = skills.allocate_skill_points(rng, class_data["pontos_pericia_nivel_1"])

    return character
