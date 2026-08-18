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
