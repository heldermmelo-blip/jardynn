import random

from ynn.creatures import CREATURES, instantiate_creature, roll_dice


def test_roll_dice_basic():
    rng = random.Random(0)
    result = roll_dice(rng, "2d6+1")
    assert 3 <= result <= 13


def test_roll_dice_rejects_bad_notation():
    try:
        roll_dice(random.Random(0), "não é um dado")
    except ValueError:
        pass
    else:
        raise AssertionError("esperava ValueError para notação inválida")


def test_all_creatures_instantiate_with_positive_hp():
    for key in CREATURES:
        creature = instantiate_creature(random.Random(1), key)
        assert creature["pontos_de_vida"] >= 1
        assert creature["nome"]
        assert creature["ataques"]


def test_instantiate_does_not_mutate_template():
    template_before = dict(CREATURES["gato_sem_rosto"])
    instantiate_creature(random.Random(2), "gato_sem_rosto")
    assert CREATURES["gato_sem_rosto"] == template_before
