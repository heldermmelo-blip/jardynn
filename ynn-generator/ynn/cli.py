"""CLI: gera uma camada de jardim e imprime (ou salva) como Markdown.

Uso:
    python -m ynn.cli --layer 1 --areas 5 --seed 42
"""

import argparse
import json
import random

from .generator import generate_layer  # importa antes: garante lotfp-rules no sys.path
from .tables import BAND_LABELS

from lotfp.cli import render_character


def render_creature(creature):
    lines = [f"**{creature['nome']}**"]
    lines.append(
        f"CA {creature['ca']} · DV {creature['dv']} · PV {creature['pontos_de_vida']} · Moral {creature['moral']}"
    )
    lines.append(f"Movimento: {creature['movimento']}")
    lines.append("Ataques: " + "; ".join(f"{nome} ({dano})" for nome, dano in creature["ataques"]))
    lines.append(f"Resistência: {creature['resistencia']}+ (rola 1d20)")
    lines.append(f"Especial: {creature['especial']}")
    return "\n".join(lines)


def render_layer_markdown(layer, areas):
    band_label = BAND_LABELS[areas[0]["band"]] if areas else ""
    lines = [f"## Camada {layer} — {band_label}", ""]
    for area in areas:
        lines.append(f"### Área {area['index']}")
        lines.append(area["text"])
        if area["planta_obj"] is not None:
            lines.append(f"*(planta gerada: `{area['planta_obj']}`)*")
        if area["npc"] is not None:
            lines.append("")
            lines.append(render_character(area["npc"]))
        if area["criatura"] is not None:
            lines.append("")
            lines.append(render_creature(area["criatura"]))
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Gerador de camadas de jardim (inspirado na estrutura de The Gardens of Ynn)"
    )
    parser.add_argument("--layer", type=int, default=1, help="Número da camada (profundidade)")
    parser.add_argument("--areas", type=int, default=5, help="Quantidade de áreas a gerar")
    parser.add_argument("--seed", type=int, default=None, help="Seed para reprodutibilidade")
    parser.add_argument(
        "--json", action="store_true", help="Gera JSON em vez de Markdown (para consumo por outras ferramentas, ex. Godot)"
    )
    parser.add_argument("--output", type=str, default=None, help="Arquivo de saída; padrão imprime no terminal")
    parser.add_argument(
        "--plant-output-dir",
        type=str,
        default=None,
        help="Pasta onde salvar as malhas .obj das plantas (padrão: ynn-generator/output/plantas)",
    )
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    areas = generate_layer(rng, args.layer, args.areas, plant_output_dir=args.plant_output_dir)
    output = (
        json.dumps({"layer": args.layer, "areas": areas}, ensure_ascii=False, indent=2)
        if args.json
        else render_layer_markdown(args.layer, areas)
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"salvo em: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
