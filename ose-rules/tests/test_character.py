import random

from ose.character import create_character
from ose.classes import CLASSES


def test_all_classes_generate_without_error():
    for class_key in CLASSES:
        rng = random.Random(1)
        character = create_character(rng, class_key)
        assert character["pontos_de_vida"] >= 1
        assert len(character["atributos"]) == 6


def test_same_seed_is_deterministic():
    char_a = create_character(random.Random(42), "fighter")
    char_b = create_character(random.Random(42), "fighter")
    assert char_a == char_b


def test_ac_is_descending_and_dex_modified():
    from ose.character import BASE_AC

    character = create_character(random.Random(3), "fighter")
    dex_mod = character["modificadores"]["Destreza"]
    assert character["classe_de_armadura"] == BASE_AC - dex_mod


def test_thief_has_percentile_skills_others_dont():
    thief = create_character(random.Random(1), "thief")
    fighter = create_character(random.Random(1), "fighter")
    assert "pericias" in thief
    assert "pericias" not in fighter
    assert all(0 < v <= 100 for v in thief["pericias"].values())


def test_cleric_has_no_spells_at_level_1():
    for seed in range(50):
        cleric = create_character(random.Random(seed), "cleric")
        assert "magias_preparadas" not in cleric


def test_magic_user_and_elf_have_one_spell():
    from ose.spells import SPELL_SLOTS_LEVEL_1

    for class_key in ("magic_user", "elf"):
        character = create_character(random.Random(5), class_key)
        assert len(character["magias_preparadas"]) == SPELL_SLOTS_LEVEL_1[class_key]


def test_elf_uses_magic_user_spell_list():
    from ose.spells import SPELLS

    elf = create_character(random.Random(5), "elf")
    magic_user_names = {spell["nome"] for spell in SPELLS["magic_user"]}
    assert all(spell["nome"] in magic_user_names for spell in elf["magias_preparadas"])


def test_all_classes_have_all_save_categories():
    from ose.saves import SAVE_CATEGORIES

    for class_key in CLASSES:
        character = create_character(random.Random(2), class_key)
        assert set(character["testes_de_resistencia"].keys()) == set(SAVE_CATEGORIES)
