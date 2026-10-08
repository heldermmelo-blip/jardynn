"""CLI: gera um nível (ou uma camada) de jardim e imprime (ou salva) como
Markdown ou JSON.

Uso:
    python -m ynn.cli --seed 42                      # modo livro (padrão)
    python -m ynn.cli --modo livro --profundidade 5 --seed 42
    python -m ynn.cli --modo grade --layer 1 --areas 5 --seed 42
"""

import argparse
import json
import random

from .generator import (  # importa antes: garante lotfp-rules no sys.path
    generate_layer,
    generate_layout_camada,
    generate_nivel,
    generate_terreno,
)
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


def _render_estrutura(plot):
    """Linhas Markdown de um lote não-narrativo (torre, estufa, gazebo);
    lista vazia para os demais tipos."""
    lines = []
    pos = f"({plot['x']:.1f}, {plot['z']:.1f})"
    if plot["tipo"] == "torre":
        conteudo = plot["conteudo"]
        lines.append(f"- torre em {pos}, {conteudo['n_andares']} andares")
        for andar in conteudo["andares"]:
            marca = " (topo)" if andar["numero"] == conteudo["n_andares"] else ""
            lines.append(f"  - andar {andar['numero']}{marca}: {andar['texto']}")
            if andar.get("tesouro") is not None:
                lines.append(f"    - tesouro: {andar['tesouro']}")
            if andar.get("denizen") is not None:
                lines.append(f"    - encontro: {andar['denizen']}")
    elif plot["tipo"] == "estufa" and plot.get("colossal"):
        lines.append(f"- estufa em {pos}: a colossal — o nível inteiro está sob o vidro dela")
    elif plot["tipo"] == "estufa":
        planta = plot["planta"]
        dado = f"d{planta['dado']}, " if planta.get("dado") else ""
        lines.append(
            f"- estufa {planta['porte']} em {pos}: {dado}{planta['lados']} lados, "
            f"{planta['andares']} andar(es), raio {planta['raio']:.1f} m, {planta['alas']} ala(s), "
            f"{'em estado lastimável' if planta['estado'] == 'lastimavel' else 'conservada'}"
            f"{', piso em xadrez' if planta['piso_xadrez'] else ''}"
            f"{', no meio de um espelho d' + chr(39) + 'água' if plot.get('espelho_dagua') else ''}"
        )
        flora = plot.get("flora_interna")
        if flora:
            mortas = f", {round(flora['mortas'] * 100)}% mortas" if flora["mortas"] else ""
            lines.append(
                f"  - flora {flora['densidade']} ({len(flora['plantas'])} plantas, tema {flora['tema']}: "
                f"{', '.join(flora['especies'])}{mortas})"
            )
        conteudo = plot["conteudo"]
        lines.append(f"  - {conteudo['texto']}")
        if conteudo.get("valor_ouro") is not None:
            lines.append(f"    - vale {conteudo['valor_ouro']} de ouro")
        if conteudo.get("criatura") is not None:
            lines.append(f"    - criatura: {conteudo['criatura']['nome']}")
    elif plot["tipo"] == "gazebo":
        conteudo = plot["conteudo"]
        lines.append(f"- gazebo em {pos}: {conteudo['texto']}")
        lines.append(f"  - bibelô: {conteudo['bibelo']}")
        lines.append(f"  - tesouro: {conteudo['tesouro']}")
        lines.append(f"  - {conteudo['refugio']}")
    return lines


def _render_area(area):
    lines = [area["text"]]
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
    return lines


def render_layer_markdown(layer, areas, terreno=None, layout=None):
    band_label = BAND_LABELS[areas[0]["band"]] if areas else ""
    lines = [f"## Camada {layer} — {band_label}", ""]
    if terreno is not None:
        lines.append(f"**Relevo** ({terreno['tipo_relevo']}): {terreno['descricao']}")
        lines.append("")
    if layout is not None:
        lines.append(f"**Layout**: campo de {layout['field_width']:.0f}x{layout['field_depth']:.0f}m")
        for plot in layout["plots"]:
            estrutura = _render_estrutura(plot)
            if estrutura:
                lines.extend(estrutura)
            elif plot["tipo"] != "area":
                lines.append(f"- {plot['tipo']} em ({plot['x']:.1f}, {plot['z']:.1f})")
        lines.append("")
    for area in areas:
        lines.append(f"### Área {area['index']}")
        lines.extend(_render_area(area))
        lines.append("")
    return "\n".join(lines)


def render_nivel_markdown(nivel):
    layout = nivel["layout"]
    terreno = nivel["terreno"]
    areas = {a["index"]: a for a in nivel["areas"]}
    lines = [f"## Nível — profundidade máxima {nivel['profundidade_maxima']}", ""]
    lines.append(f"**Relevo** (mais forte: {terreno['tipo_relevo']}): {terreno['descricao']}")
    lines.append(f"**Campo**: {layout['field_width']:.0f}x{layout['field_depth']:.0f}m, {len(layout['plots'])} locais")
    lines.append("")

    for plot in sorted(layout["plots"], key=lambda p: (p["profundidade"], p["no_id"])):
        lines.append(f"### Profundidade {plot['profundidade']} — {plot['local']} (nó {plot['no_id']}, {plot['tipo']})")
        detalhe = plot["detalhe"]
        lines.append(f"*Detalhe* ({detalhe['tipo_relevo']}): {detalhe['texto']}")
        if detalhe.get("tesouro"):
            lines.append(f"*Achado extra*: {detalhe['tesouro']}")
        if "saida" in detalhe["efeitos"]:
            lines.append("*Há uma porta de volta ao mundo real aqui.*")
        if plot["tipo"] == "area":
            lines.extend(_render_area(areas[plot["area_index"]]))
        else:
            lines.extend(_render_estrutura(plot))
        lines.append("")

    colossal = nivel.get("estufa_colossal")
    if colossal:
        lines.append("### Estufa colossal")
        lines.append(colossal["texto"])
        for porta in layout.get("portas_estufa", []):
            lines.append(f"- portal de {porta['tipo']} em ({porta['x']:.1f}, {porta['z']:.1f}), junto ao nó {porta['no_id']}")
        lines.append("")

    lines.append("### Ligações")
    for aresta in layout["arestas"]:
        lines.append(f"- {aresta['de']} → {aresta['para']} ({aresta['tipo']})")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Gerador de níveis de jardim (inspirado na estrutura de The Gardens of Ynn)"
    )
    parser.add_argument(
        "--modo",
        choices=["livro", "grade"],
        default="livro",
        help=(
            "livro (padrão): mapa de pontos como o do livro — entrada na camada 0, locais sorteados em "
            "d20 + profundidade, ramificações e atalhos. grade: o layout anterior, lotes sorteados numa "
            "grade, com uma camada só (--layer/--areas)."
        ),
    )
    parser.add_argument("--profundidade", type=int, default=4, help="[livro] Camadas além da entrada (padrão 4)")
    parser.add_argument("--max-nos", type=int, default=14, help="[livro] Máximo de locais no mapa (padrão 14)")
    parser.add_argument(
        "--estufa-colossal",
        choices=["auto", "sempre", "nunca"],
        default="auto",
        help=(
            "[livro] A estufa colossal cobre o nível inteiro, com entrada e saída em lados opostos. "
            "auto (padrão): é a mais rara de todas, 1 em 30 por estufa; sempre: força uma; nunca: desliga."
        ),
    )
    parser.add_argument("--layer", type=int, default=1, help="[grade] Número da camada (profundidade)")
    parser.add_argument("--areas", type=int, default=5, help="[grade] Quantidade de áreas a gerar")
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
        "--plot-size", type=float, default=12.0, help="[grade] Tamanho de cada lote da grade de layout, em metros (padrão 12)"
    )
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)

    if args.modo == "livro":
        nivel = generate_nivel(
            rng,
            profundidade_max=args.profundidade,
            max_nos=args.max_nos,
            plant_output_dir=args.plant_output_dir,
            field_width=args.field_width,
            field_depth=args.field_depth,
            resolution=args.terrain_resolution,
            cell_size=args.terrain_cell_size,
            estufa_colossal=args.estufa_colossal,
        )
        output = json.dumps(nivel, ensure_ascii=False, indent=2) if args.json else render_nivel_markdown(nivel)
    else:
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
