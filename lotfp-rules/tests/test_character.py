import random

from lotfp.character import create_character
from lotfp.classes import CLASSES


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


def test_specialist_has_skills_others_dont():
    specialist = create_character(random.Random(1), "specialist")
    fighter = create_character(random.Random(1), "fighter")
    assert "pericias" in specialist
    assert "pericias" not in fighter


def test_specialist_skill_points_are_spent():
    from lotfp.skills import SPECIALIST_BASE_RATING

    specialist = create_character(random.Random(3), "specialist")
    points_spent = sum(r - SPECIALIST_BASE_RATING for r in specialist["pericias"].values())
    assert points_spent == CLASSES["specialist"]["pontos_pericia_nivel_1"]


def test_casters_have_spells_others_dont():
    from lotfp.spells import SPELL_SLOTS_LEVEL_1

    for class_key in ("magic_user", "cleric"):
        character = create_character(random.Random(5), class_key)
        assert len(character["magias_preparadas"]) == SPELL_SLOTS_LEVEL_1[class_key]

    for class_key in ("fighter", "specialist"):
        character = create_character(random.Random(5), class_key)
        assert "magias_preparadas" not in character


def test_magic_user_grimoire_matches_prepared_spells():
    magic_user = create_character(random.Random(9), "magic_user")
    assert magic_user["grimorio"] == magic_user["magias_preparadas"]


def test_cleric_has_no_grimoire():
    cleric = create_character(random.Random(9), "cleric")
    assert "grimorio" not in cleric


def test_all_classes_have_all_save_categories():
    from lotfp.saves import SAVE_CATEGORIES

    for class_key in CLASSES:
        character = create_character(random.Random(2), class_key)
        assert set(character["testes_de_resistencia"].keys()) == set(SAVE_CATEGORIES)


def test_roll_save_respects_target():
    from lotfp.saves import roll_save

    class FixedRng:
        def randint(self, a, b):
            return a  # sempre o mínimo possível

    roll, target, success = roll_save(FixedRng(), "fighter", "Paralisia")
    assert roll == 1
    assert success is (roll >= target)
