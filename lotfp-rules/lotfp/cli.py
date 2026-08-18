"""CLI: gera um personagem de nível 1.

Uso:
    python -m lotfp.cli --classe fighter --seed 42
"""

import argparse
import random

from .character import create_character
from .classes import CLASSES


def render_character(character):
    lines = [f"## {character['classe']} (nível 1)", ""]
    lines.append("**Atributos**")
    for name, score in character["atributos"].items():
        mod = character["modificadores"][name]
        sign = "+" if mod >= 0 else ""
        lines.append(f"- {name}: {score} ({sign}{mod})")
    lines.append("")
    lines.append(f"**Pontos de vida:** {character['pontos_de_vida']}")
    lines.append(f"**Bônus de ataque:** +{character['bonus_ataque']}")
    if "pericias" in character:
        lines.append("")
        lines.append("**Perícias**")
        for skill, rating in character["pericias"].items():
            lines.append(f"- {skill}: {rating}-em-6")
    lines.append("")
    lines.append("**Equipamento inicial**")
    for item, slots in character["equipamento"]:
        lines.append(f"- {item} ({slots} slot{'s' if slots != 1 else ''})")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gerador de personagem de nível 1 (LotFP)")
    parser.add_argument("--classe", choices=list(CLASSES.keys()), default="fighter")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    character = create_character(rng, args.classe)
    print(render_character(character))


if __name__ == "__main__":
    main()
