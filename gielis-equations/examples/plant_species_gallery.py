"""Gera um .obj de exemplo de cada espécie disponível em `gielis.plants`.

Uso:
    python examples/plant_species_gallery.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gielis.plants import SPECIES, generate_plant

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "especies")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, species in enumerate(SPECIES):
        rng = random.Random(i)
        out_path = os.path.join(OUTPUT_DIR, f"{species}.obj")
        path, skeleton = generate_plant(rng, species, out_path=out_path)
        print(f"{species}: {path} ({len(skeleton)} segmento(s) no esqueleto)")
