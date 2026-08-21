"""CLI: gera um personagem de nível 1.

Uso:
    python -m ose.cli --classe fighter --seed 42
"""

import argparse
import json
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
    lines.append(f"**Classe de Armadura:** {character['classe_de_armadura']} (descendente — menor é melhor)")
    lines.append(f"**Bônus de ataque:** +{character['bonus_ataque']}")
    lines.append("")
    lines.append("**Testes de Resistência** (rola 1d20, sucesso se >= alvo)")
    for category, target in character["testes_de_resistencia"].items():
        lines.append(f"- {category}: {target}+")
    if "pericias" in character:
        lines.append("")
        lines.append("**Perícias do Thief** (rola d100, sucesso se <= valor)")
        for skill, value in character["pericias"].items():
            lines.append(f"- {skill}: {value}%")
    if "magias_preparadas" in character:
        lines.append("")
        lines.append("**Magias preparadas**")
        for spell in character["magias_preparadas"]:
            lines.append(f"- {spell['nome']}: {spell['descricao']}")
        if "grimorio" in character:
            lines.append("")
            lines.append("**Grimório:** " + ", ".join(spell["nome"] for spell in character["grimorio"]))
    lines.append("")
    lines.append("**Equipamento inicial**")
    for item, slots in character["equipamento"]:
        lines.append(f"- {item} ({slots} slot{'s' if slots != 1 else ''})")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gerador de personagem de nível 1 (OSE)")
    parser.add_argument("--classe", choices=list(CLASSES.keys()), default="fighter")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="Gera JSON em vez de Markdown (para consumo por outras ferramentas, ex. Godot)")
    parser.add_argument("--output", type=str, default=None, help="Arquivo de saída; padrão imprime no terminal")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    character = create_character(rng, args.classe)
    output = json.dumps(character, ensure_ascii=False, indent=2) if args.json else render_character(character)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"salvo em: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
