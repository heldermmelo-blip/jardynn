"""CLI: gera uma camada de jardim e imprime (ou salva) como Markdown.

Uso:
    python -m ynn.cli --layer 1 --areas 5 --seed 42
"""

import argparse
import json
import random

from .generator import generate_layer, generate_layout_camada, generate_terreno  # importa antes: garante lotfp-rules no sys.path
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


def render_layer_markdown(layer, areas, terreno=None, layout=None):
    band_label = BAND_LABELS[areas[0]["band"]] if areas else ""
    lines = [f"## Camada {layer} — {band_label}", ""]
    if terreno is not None:
        lines.append(f"**Relevo** ({terreno['tipo_relevo']}): {terreno['descricao']}")
        lines.append("")
    if layout is not None:
        lines.append(f"**Layout**: campo de {layout['field_width']:.0f}x{layout['field_depth']:.0f}m")
        for plot in layout["plots"]:
            if plot["tipo"] != "area":
                lines.append(f"- {plot['tipo']} em ({plot['x']:.1f}, {plot['z']:.1f})")
        lines.append("")
    for area in areas:
        lines.append(f"### Área {area['index']}")
        lines.append(area["text"])
        if area["plantas_obj"]:
            lines.append(f"*(plantas geradas: {len(area['plantas_obj'])}x `{area['plantas_obj'][0]}` e variantes)*")
        if area["galhos_caidos_obj"]:
            lines.append(f"*(galhos caídos: {len(area['galhos_caidos_obj'])}x `{area['galhos_caidos_obj'][0]}` e variantes)*")
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
    parser.add_argument(
        "--terrain-resolution",
        type=int,
        default=65,
        help="Resolução da grade de relevo (pontos por lado; arredondada para 2^n + 1, padrão 65)",
    )
    parser.add_argument(
        "--terrain-cell-size",
        type=float,
        default=2.0,
        help=(
            "Distância entre pontos adjacentes da grade de relevo, em unidades do mundo (padrão 2.0). "
            "O terreno cobre (resolução - 1) * tamanho_celula unidades de lado, centrado na origem — "
            "precisa ser maior que --field-width/--field-depth."
        ),
    )
    parser.add_argument(
        "--field-width", type=float, default=105.0, help="Largura do campo/layout em metros (padrão 105, escala de campo de futebol)"
    )
    parser.add_argument(
        "--field-depth", type=float, default=68.0, help="Profundidade do campo/layout em metros (padrão 68)"
    )
    parser.add_argument(
        "--plot-size", type=float, default=12.0, help="Tamanho de cada lote da grade de layout, em metros (padrão 12)"
    )
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    terreno = generate_terreno(rng, args.layer, resolution=args.terrain_resolution, cell_size=args.terrain_cell_size)
    camada_layout = generate_layout_camada(
        rng,
        args.layer,
        args.areas,
        plant_output_dir=args.plant_output_dir,
        field_width=args.field_width,
        field_depth=args.field_depth,
        plot_size=args.plot_size,
    )
    areas = generate_layer(rng, args.layer, args.areas, plant_output_dir=args.plant_output_dir)
    output = (
        json.dumps(
            {"layer": args.layer, "terreno": terreno, "layout": camada_layout, "areas": areas},
            ensure_ascii=False,
            indent=2,
        )
        if args.json
        else render_layer_markdown(args.layer, areas, terreno=terreno, layout=camada_layout)
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"salvo em: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
