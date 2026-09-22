"""Montagem de áreas e camadas de jardim a partir das tabelas em `tables.py`."""

import os
import sys

from . import tables, terrain

_YNN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKSPACE_ROOT = os.path.dirname(_YNN_ROOT)

for _sibling in ("lotfp-rules", "gielis-equations"):
    _path = os.path.join(_WORKSPACE_ROOT, _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from lotfp.character import create_character  # noqa: E402
from gielis.plants import generate_fallen_branch as _generate_fallen_branch_mesh  # noqa: E402
from gielis.plants import generate_plant as _generate_plant_mesh  # noqa: E402

from .creatures import instantiate_creature

PLANT_OUTPUT_DIR = os.path.join(_YNN_ROOT, "output", "plantas")

WYRD_CHANCE = {"jardim_externo": 0.10, "jardim_profundo": 0.35, "nucleo_selvagem": 0.65}
DENIZEN_CHANCE = {"jardim_externo": 0.45, "jardim_profundo": 0.55, "nucleo_selvagem": 0.60}
TREASURE_CHANCE = {"jardim_externo": 0.15, "jardim_profundo": 0.22, "nucleo_selvagem": 0.30}
ATMOSPHERE_CHANCE = 0.4

# Um jardim de verdade não tem uma planta solitária por área — gera alguns
# exemplares variados da espécie dominante (mesma espécie, formas
# diferentes a cada chamada de `_generate_plant_mesh` pelo `rng` seguir
# andando); a densidade exata varia de área pra área.
PLANT_VARIANT_RANGE = (3, 6)

# Um jardim sem cuidado tem galhos cortados ou caídos largados pelo chão —
# um detrito raro, não uma espécie viva (ver gielis.plants.generate_fallen_branch).
FALLEN_BRANCH_CHANCE = 1 / 6
FALLEN_BRANCH_COUNT_RANGE = (1, 3)


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
    return [
        (text, class_key, creature_key)
        for text, bands, class_key, creature_key in tables.DENIZENS
        if bands == "all" or band in bands
    ]


def _pick_denizen(rng, band):
    return rng.choice(_denizens_for_band(band))


def _vegetation_for_band(band):
    return [(text, species) for text, bands, species in tables.VEGETATION if bands == "all" or band in bands]


def _pick_vegetation(rng, band):
    return rng.choice(_vegetation_for_band(band))


def generate_area(rng, layer, index, plant_output_dir=None):
    band = band_for_layer(layer)
    vegetation_text, vegetation_species = _pick_vegetation(rng, band)
    parts = [vegetation_text]

    plant_obj_paths = []
    if vegetation_species is not None:
        out_dir = plant_output_dir or PLANT_OUTPUT_DIR
        n_variants = rng.randint(*PLANT_VARIANT_RANGE)
        for variant in range(1, n_variants + 1):
            out_path = os.path.join(out_dir, f"camada{layer}_area{index}_{vegetation_species}_{variant}.obj")
            path, _ = _generate_plant_mesh(rng, vegetation_species, out_path=out_path)
            plant_obj_paths.append(path)

    fallen_branch_paths = []
    if rng.random() < FALLEN_BRANCH_CHANCE:
        out_dir = plant_output_dir or PLANT_OUTPUT_DIR
        n_branches = rng.randint(*FALLEN_BRANCH_COUNT_RANGE)
        for branch in range(1, n_branches + 1):
            out_path = os.path.join(out_dir, f"camada{layer}_area{index}_galho_caido_{branch}.obj")
            path, _ = _generate_fallen_branch_mesh(rng, out_path=out_path)
            fallen_branch_paths.append(path)
        parts.append(
            "No chão, alguns galhos cortados ou caídos jazem esquecidos — sinal de um jardim que já não recebe cuidado."
        )

    if rng.random() < ATMOSPHERE_CHANCE:
        parts.append(_pick(rng, tables.ATMOSPHERE, band))

    parts.append(f"Aqui há {_pick(rng, tables.FEATURES, band)}.")

    denizen, denizen_class, denizen_creature, npc, creature = None, None, None, None, None
    if rng.random() < DENIZEN_CHANCE[band]:
        denizen, denizen_class, denizen_creature = _pick_denizen(rng, band)
        parts.append(f"Você nota {denizen}.")
        if denizen_class is not None:
            npc = create_character(rng, denizen_class)
        elif denizen_creature is not None:
            creature = instantiate_creature(rng, denizen_creature)

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
        "criatura": creature,
        "plantas_obj": plant_obj_paths,
        "galhos_caidos_obj": fallen_branch_paths,
    }


def generate_layer(rng, layer, n_areas, plant_output_dir=None):
    return [generate_area(rng, layer, i + 1, plant_output_dir=plant_output_dir) for i in range(n_areas)]


def generate_terreno(rng, layer, resolution=33, cell_size=3.0):
    band = band_for_layer(layer)
    return terrain.generate_terrain(rng, band, resolution=resolution, cell_size=cell_size)
