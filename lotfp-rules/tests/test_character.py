import random

from lotfp.character import create_character
from lotfp.classes import CLASSES


def test_all_classes_generate_without_error():
    for class_key in CLASSES:
        rng = random.Random(1)
        character = create_character(rng, class_key)
        assert character["pontos_de_vida"] >= CLASSES[class_key]["pontos_de_vida_minimos"]
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


def test_level_1_numbers_match_the_rulebook():
    from lotfp.saves import SAVES_LEVEL_1

    assert CLASSES["fighter"]["bonus_ataque_nivel_1"] == 2
    assert all(CLASSES[k]["bonus_ataque_nivel_1"] == 1 for k in ("specialist", "magic_user", "cleric"))
    ordem = ("fighter", "specialist", "magic_user", "cleric")
    assert [CLASSES[k]["dado_de_vida"] for k in ordem] == [8, 6, 6, 6]
    assert [CLASSES[k]["pontos_de_vida_minimos"] for k in ordem] == [8, 4, 3, 4]
    # ordem: Paralisia, Veneno, Sopro, Dispositivos Mágicos, Magia
    assert list(SAVES_LEVEL_1["fighter"].values()) == [14, 12, 15, 13, 16]
    assert list(SAVES_LEVEL_1["specialist"].values()) == [14, 16, 15, 14, 14]
    assert list(SAVES_LEVEL_1["magic_user"].values()) == [13, 13, 16, 13, 14]
    assert list(SAVES_LEVEL_1["cleric"].values()) == [14, 11, 16, 12, 15]


def test_sneak_attack_is_a_multiplier_without_the_six_cap():
    from lotfp.skills import SNEAK_ATTACK, allocate_skill_points

    ratings = allocate_skill_points(random.Random(1), 4)
    assert all(v <= 6 for k, v in ratings.items() if k != SNEAK_ATTACK)
    assert allocate_skill_points(random.Random(1), 10, {SNEAK_ATTACK: 1})[SNEAK_ATTACK] == 11


def test_encumbrance_points_follow_the_table():
    from lotfp.equipment import encumbrance_points, movement

    assert [encumbrance_points(n) for n in (5, 6, 11, 16, 21)] == [0, 1, 2, 3, 4]
    assert encumbrance_points(6, chain_armor=True, oversized_items=1) == 3
    assert movement(0)[1] == 120 and movement(3)[1] == 60 and movement(5)[1] == 0
