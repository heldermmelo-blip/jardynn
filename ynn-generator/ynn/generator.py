"""Montagem de áreas e camadas de jardim a partir das tabelas em `tables.py`."""

import os
import sys

from . import tables

_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LOTFP_PATH = os.path.join(_WORKSPACE_ROOT, "lotfp-rules")
if _LOTFP_PATH not in sys.path:
    sys.path.insert(0, _LOTFP_PATH)

from lotfp.character import create_character  # noqa: E402

WYRD_CHANCE = {"jardim_externo": 0.10, "jardim_profundo": 0.35, "nucleo_selvagem": 0.65}
DENIZEN_CHANCE = {"jardim_externo": 0.45, "jardim_profundo": 0.55, "nucleo_selvagem": 0.60}
TREASURE_CHANCE = {"jardim_externo": 0.15, "jardim_profundo": 0.22, "nucleo_selvagem": 0.30}
ATMOSPHERE_CHANCE = 0.4


def band_for_layer(layer):
    if layer <= 2:
        return "jardim_externo"
    if layer <= 4:
        return "jardim_profundo"
    return "nucleo_selvagem"


def _entries_for_band(entries, band):
    return [text for text, bands in entries if bands == "all" or band in bands]


def _pick(rng, entries, band):
    return rng.choice(_entries_for_band(entries, band))


def _denizens_for_band(band):
    return [(text, class_key) for text, bands, class_key in tables.DENIZENS if bands == "all" or band in bands]


def _pick_denizen(rng, band):
    return rng.choice(_denizens_for_band(band))


def generate_area(rng, layer, index):
    band = band_for_layer(layer)
    parts = [_pick(rng, tables.VEGETATION, band)]

    if rng.random() < ATMOSPHERE_CHANCE:
        parts.append(_pick(rng, tables.ATMOSPHERE, band))

    parts.append(f"Aqui há {_pick(rng, tables.FEATURES, band)}.")

    denizen, denizen_class, npc = None, None, None
    if rng.random() < DENIZEN_CHANCE[band]:
        denizen, denizen_class = _pick_denizen(rng, band)
        parts.append(f"Você nota {denizen}.")
        if denizen_class is not None:
            npc = create_character(rng, denizen_class)

    wyrd = _pick(rng, tables.WYRD, band) if rng.random() < WYRD_CHANCE[band] else None
    if wyrd is not None:
        parts.append(wyrd)

    treasure = _pick(rng, tables.TREASURE, band) if rng.random() < TREASURE_CHANCE[band] else None
    if treasure is not None:
        parts.append(f"Entre a vegetação, há {treasure}.")

    return {
        "index": index,
        "layer": layer,
        "band": band,
        "text": " ".join(parts),
        "has_denizen": denizen is not None,
        "has_wyrd": wyrd is not None,
        "has_treasure": treasure is not None,
        "npc": npc,
    }


def generate_layer(rng, layer, n_areas):
    return [generate_area(rng, layer, i + 1) for i in range(n_areas)]
