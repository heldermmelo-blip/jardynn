"""Montagem de áreas e camadas de jardim a partir das tabelas em `tables.py`."""

import os
import sys

from . import layout, pointcrawl, tables, terrain

_YNN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKSPACE_ROOT = os.path.dirname(_YNN_ROOT)

for _sibling in ("lotfp-rules", "gielis-equations"):
    _path = os.path.join(_WORKSPACE_ROOT, _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from lotfp.character import create_character  # noqa: E402
from gielis.plants import generate_fallen_branch as _generate_fallen_branch_mesh  # noqa: E402
from gielis.plants import generate_plant as _generate_plant_mesh  # noqa: E402
from gielis.structures import generate_gazebo as _generate_gazebo_mesh  # noqa: E402
from gielis.structures import generate_greenhouse as _generate_greenhouse_mesh  # noqa: E402
from gielis.structures import TOWER_FLOOR_HEIGHT, TOWER_STAIRWELL_RADIUS  # noqa: E402
from gielis.structures import generate_tower as _generate_tower_mesh  # noqa: E402
from gielis.structures import generate_tower_vines as _generate_tower_vines_mesh  # noqa: E402

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

# Espécie e densidade dos canteiros do layout (ver `ynn.layout`) — uma
# única espécie por canteiro, em quantidade parecida com PLANT_VARIANT_RANGE.
CANTEIRO_SPECIES = ("flor", "arbusto")
CANTEIRO_VARIANT_RANGE = (4, 8)

# A torre é uma mini-masmorra vertical, não só decoração: cada andar (menos
# o topo) sorteia um conteúdo em TORRE_ANDARES; o topo sorteia em
# TORRE_TOPO, separadamente. A malha (gielis.structures.generate_tower)
# recebe o mesmo número de andares, pra bater com o conteúdo.
N_ANDARES_TORRE_RANGE = (3, 8)
IVY_VARIANT_RANGE = (3, 6)

# Nem toda torre é igual: algumas ganham trepadeiras subindo pelas paredes,
# algumas perdem o telhado e deixam algo brotar no topo, e uma em cada dez
# fica inclinada. Cada efeito é sorteado por torre (`sortear_extras_torre`).
TORRE_TREPADEIRA_CHANCE = 0.6
TORRE_TOPO_BROTADO_CHANCE = 0.4
TORRE_INCLINADA_CHANCE = 1 / 10
TORRE_INCLINACAO_GRAUS = (4.0, 12.0)
TORRE_TOPO_VARIANTES = {"arvore": (1, 2), "arbusto": (2, 3), "flor": (3, 4), "samambaia": (2, 3), "cogumelo": (2, 4)}

# Tamanho/forma de cada estufa vêm de um "dado" sorteado: a face do dado é a
# planta baixa (`lados` = número de cantos/portas), dados maiores dão
# estufas maiores, e os dois maiores ganham mais andares. `raio` é o raio
# circunscrito da planta em metros (limitado pra caber num lote de 12 m);
# `peso` deixa as estufas gigantes raras.
ESTUFA_DADOS = {
    4: dict(lados=3, raio=3.0, andares=1, peso=4),
    6: dict(lados=4, raio=3.6, andares=1, peso=4),
    8: dict(lados=3, raio=4.2, andares=1, peso=3),
    10: dict(lados=4, raio=4.8, andares=1, peso=2),
    12: dict(lados=5, raio=5.3, andares=2, peso=2),
    20: dict(lados=3, raio=5.8, andares=3, peso=1),
}

REFUGIO_GAZEBO = (
    "Abrigo noturno: com uma chama acesa sob o telhado (vela, lampião ou fogueira), "
    "as criaturas do jardim não entram para atacar quem está lá dentro."
)


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


def _torre_andar_for_band(entries, band):
    return [(text, tipo, prop, rotulo) for text, bands, tipo, prop, rotulo in entries if bands == "all" or band in bands]


def _pick_andar_conteudo(rng, entries, band, numero):
    texto, tipo, prop, rotulo = rng.choice(_torre_andar_for_band(entries, band))
    andar = {"numero": numero, "texto": texto, "prop": prop, "rotulo": rotulo}
    if tipo == "tesouro":
        andar["tesouro"] = _pick(rng, tables.TREASURE, band)
    elif tipo == "encontro":
        denizen, denizen_class, denizen_creature = _pick_denizen(rng, band)
        andar["denizen"] = denizen
        if denizen_class is not None:
            andar["npc"] = create_character(rng, denizen_class)
        elif denizen_creature is not None:
            andar["criatura"] = instantiate_creature(rng, denizen_creature)
    return andar


def _vegetation_for_band(band):
    return [(text, species) for text, bands, species in tables.VEGETATION if bands == "all" or band in bands]


def _pick_vegetation(rng, band):
    return rng.choice(_vegetation_for_band(band))


def generate_area(rng, layer, index, plant_output_dir=None, local=None, sem_habitantes=False):
    """`local` (opcional) é o nome do local sorteado no mapa de pontos
    (`ynn.pointcrawl`): abre o texto e substitui o elemento notável sorteado
    em FEATURES. `sem_habitantes` suprime o sorteio de denizens (detalhe
    "vazio")."""
    band = band_for_layer(layer)
    vegetation_text, vegetation_species = _pick_vegetation(rng, band)
    parts = [f"{local}.", vegetation_text] if local else [vegetation_text]

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

    if local is None:
        parts.append(f"Aqui há {_pick(rng, tables.FEATURES, band)}.")

    denizen, denizen_class, denizen_creature, npc, creature = None, None, None, None, None
    if not sem_habitantes and rng.random() < DENIZEN_CHANCE[band]:
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


def generate_terreno(rng, layer, resolution=65, cell_size=2.0):
    band = band_for_layer(layer)
    return terrain.generate_terrain(rng, band, resolution=resolution, cell_size=cell_size)


def sortear_extras_torre(rng, layer):
    """Sorteia os efeitos opcionais de uma torre: `topo` (texto, espécie) de
    `tables.TORRE_BROTO` se ela perdeu o telhado e algo brotou lá em cima, ou
    None; `trepadeiras` (bool) se há plantas subindo pelas paredes; e
    `inclinacao` (`graus`, `azimute` em rad) se ela está torta, ou None."""
    band = band_for_layer(layer)
    topo = None
    if rng.random() < TORRE_TOPO_BROTADO_CHANCE:
        entradas = [(texto, especie) for texto, especie, bandas in tables.TORRE_BROTO if bandas == "all" or band in bandas]
        topo = rng.choice(entradas)
    trepadeiras = rng.random() < TORRE_TREPADEIRA_CHANCE
    inclinacao = None
    if rng.random() < TORRE_INCLINADA_CHANCE:
        inclinacao = {"graus": rng.uniform(*TORRE_INCLINACAO_GRAUS), "azimute": rng.uniform(0.0, 6.283185307179586)}
    return {"topo": topo, "trepadeiras": trepadeiras, "inclinacao": inclinacao}


def generate_torre_conteudo(rng, layer, n_andares_range=N_ANDARES_TORRE_RANGE):
    """Sorteia o conteúdo da torre: um número de andares (`n_andares_range`,
    padrão 3-8) e um conteúdo original por andar — os normais de
    `tables.TORRE_ANDARES`, o último de `tables.TORRE_TOPO` (mais raro e
    significativo). Cada andar pode carregar um tesouro (`tables.TREASURE`)
    ou um denizen/NPC/criatura (`tables.DENIZENS`), igual às áreas."""
    band = band_for_layer(layer)
    n_andares = rng.randint(*n_andares_range)  # padrão 3-8: o equivalente a d6+2 do livro

    andares = [_pick_andar_conteudo(rng, tables.TORRE_ANDARES, band, numero) for numero in range(1, n_andares)]
    andares.append(_pick_andar_conteudo(rng, tables.TORRE_TOPO, band, n_andares))

    return {"n_andares": n_andares, "andares": andares}


def generate_estufa_planta(rng):
    """Sorteia o "dado" de uma estufa e devolve sua planta: número de lados
    (= cantos = portas), andares e raio, conforme `ESTUFA_DADOS`."""
    dados = list(ESTUFA_DADOS)
    dado = rng.choices(dados, weights=[ESTUFA_DADOS[d]["peso"] for d in dados])[0]
    info = ESTUFA_DADOS[dado]
    return {
        "dado": dado,
        "lados": info["lados"],
        "portas": info["lados"],
        "andares": info["andares"],
        "raio": info["raio"],
    }


def generate_estufa_conteudo(rng, layer):
    """Sorteia o conteúdo de uma estufa em `tables.ESTUFA_CONTEUDO`: texto,
    e conforme o tipo, um valor em ouro (`1d6 + camada`, crescente com a
    profundidade) ou a ficha de uma criatura."""
    band = band_for_layer(layer)
    entries = [
        (texto, tipo, criatura_key)
        for texto, bandas, tipo, criatura_key in tables.ESTUFA_CONTEUDO
        if bandas == "all" or band in bandas
    ]
    texto, tipo, criatura_key = rng.choice(entries)
    conteudo = {"texto": texto}
    if tipo == "valor":
        conteudo["valor_ouro"] = rng.randint(1, 6) + layer
    elif tipo == "criatura":
        conteudo["criatura"] = instantiate_creature(rng, criatura_key)
    return conteudo


def generate_gazebo_conteudo(rng, layer):
    """Conteúdo de um gazebo: o estado do pavilhão, um bibelô largado
    dentro, um tesouro (`tables.TREASURE`) e a regra de abrigo noturno."""
    band = band_for_layer(layer)
    return {
        "texto": _pick(rng, tables.GAZEBO_ESTADO, band),
        "bibelo": _pick(rng, tables.GAZEBO_BIBELOS, band),
        "tesouro": _pick(rng, tables.TREASURE, band),
        "refugio": REFUGIO_GAZEBO,
    }


def _preencher_lote(rng, layer, plot, i, out_dir):
    """Gera a malha e o conteúdo de um lote não-narrativo (torre, estufa,
    gazebo ou canteiro), gravando os resultados no próprio `plot`. `i` só
    entra no nome dos arquivos."""
    if plot["tipo"] == "torre":
        conteudo = generate_torre_conteudo(rng, layer)
        out_path = os.path.join(out_dir, f"camada{layer}_torre_{i}.obj")
        extras = sortear_extras_torre(rng, layer)
        path, skeleton = _generate_tower_mesh(
            rng, conteudo["n_andares"], out_path=out_path, roof=extras["topo"] is None
        )
        plot["obj"] = path
        plot["conteudo"] = conteudo
        # Medidas dessa torre específica (cada uma tem seus andares e raio),
        # pra o Godot encaixar os objetos de cada andar no piso em anel.
        plot["geometria"] = {
            "altura_andar": TOWER_FLOOR_HEIGHT,
            "raio_vao": TOWER_STAIRWELL_RADIUS,
            "raios_andar": [float(seg["r0"]) for seg in skeleton],
            "porta_angulo": float(skeleton[0]["porta_angulo"]),
            "altura_total": float(skeleton[0]["altura_total"]),
            "raio_topo": float(skeleton[0]["raio_topo"]),
        }

        n_ivy = rng.randint(*IVY_VARIANT_RANGE)
        ivy_paths = []
        for variant in range(1, n_ivy + 1):
            ivy_path = os.path.join(out_dir, f"camada{layer}_torre_{i}_hera_{variant}.obj")
            path, _ = _generate_plant_mesh(rng, "videira", out_path=ivy_path)
            ivy_paths.append(path)
        plot["hera_obj"] = ivy_paths

        if extras["topo"] is not None:
            texto_topo, especie_topo = extras["topo"]
            paths = []
            for variant in range(1, rng.randint(*TORRE_TOPO_VARIANTES[especie_topo]) + 1):
                topo_path = os.path.join(out_dir, f"camada{layer}_torre_{i}_topo_{variant}.obj")
                path, _ = _generate_plant_mesh(rng, especie_topo, out_path=topo_path)
                paths.append(path)
            plot["topo_obj"] = paths
            conteudo["topo_brotado"] = {"texto": texto_topo, "especie": especie_topo}
        if extras["trepadeiras"]:
            path, _ = _generate_tower_vines_mesh(
                rng, skeleton, out_path=os.path.join(out_dir, f"camada{layer}_torre_{i}_trepadeiras.obj")
            )
            plot["trepadeiras_obj"] = path
        if extras["inclinacao"] is not None:
            plot["inclinacao"] = extras["inclinacao"]
    elif plot["tipo"] == "estufa":
        planta = generate_estufa_planta(rng)
        out_path = os.path.join(out_dir, f"camada{layer}_estufa_{i}.obj")
        path, _ = _generate_greenhouse_mesh(
            rng, sides=planta["lados"], n_floors=planta["andares"], radius=planta["raio"], out_path=out_path
        )
        plot["obj"] = path
        plot["planta"] = planta
        plot["conteudo"] = generate_estufa_conteudo(rng, layer)
    elif plot["tipo"] == "gazebo":
        out_path = os.path.join(out_dir, f"camada{layer}_gazebo_{i}.obj")
        path, _ = _generate_gazebo_mesh(rng, out_path=out_path)
        plot["obj"] = path
        plot["conteudo"] = generate_gazebo_conteudo(rng, layer)
    elif plot["tipo"] == "canteiro":
        especie = rng.choice(CANTEIRO_SPECIES)
        n_variants = rng.randint(*CANTEIRO_VARIANT_RANGE)
        paths = []
        for variant in range(1, n_variants + 1):
            out_path = os.path.join(out_dir, f"camada{layer}_canteiro_{i}_{especie}_{variant}.obj")
            path, _ = _generate_plant_mesh(rng, especie, out_path=out_path)
            paths.append(path)
        plot["especie"] = especie
        plot["plantas_obj"] = paths


def generate_layout_camada(rng, layer, n_areas, plant_output_dir=None, **layout_kwargs):
    """Gera o layout 2D da camada (`ynn.layout.generate_layout`) e já
    preenche as malhas de cada estrutura não-narrativa (torre, estufa,
    gazebo, canteiro) diretamente nos lotes — as áreas (`tipo == "area"`) só
    carregam a posição; o conteúdo delas continua vindo de `generate_area`,
    cruzado por `area_index`."""
    camada_layout = layout.generate_layout(rng, n_areas, **layout_kwargs)
    out_dir = plant_output_dir or PLANT_OUTPUT_DIR

    for i, plot in enumerate(camada_layout["plots"], start=1):
        _preencher_lote(rng, layer, plot, i, out_dir)

    return camada_layout


def generate_nivel(
    rng,
    profundidade_max=4,
    max_nos=14,
    plant_output_dir=None,
    field_width=layout.FIELD_WIDTH,
    field_depth=layout.FIELD_DEPTH,
    resolution=65,
    cell_size=2.0,
):
    """Produtor de níveis no estilo do livro: um mapa de pontos
    (`ynn.pointcrawl`) com a entrada na camada 0 e locais cada vez mais
    estranhos até `profundidade_max`, cada um sorteado em `d20 +
    profundidade` (Local e Detalhe). Os nós viram lotes posicionados no
    campo; a profundidade de um nó (+1) faz o papel do número da camada
    para escolher a banda de conteúdo. O relevo varia só ao redor dos
    locais cujo detalhe pede (`generate_terrain_localizado`).

    Devolve um dict pronto para virar JSON: `terreno`, `layout` (com
    `plots` e `arestas`) e `areas` (o conteúdo narrativo dos nós do tipo
    "area", cruzado por `area_index`)."""
    grafo = pointcrawl.generate_pointcrawl(rng, profundidade_max, max_nos)
    plots = pointcrawl.layout_grafo(rng, grafo, field_width, field_depth)
    out_dir = plant_output_dir or PLANT_OUTPUT_DIR

    areas = []
    for i, plot in enumerate(plots, start=1):
        camada = plot["profundidade"] + 1
        efeitos = plot["detalhe"]["efeitos"]
        if plot["tipo"] == "area":
            area = generate_area(
                rng,
                camada,
                len(areas) + 1,
                plant_output_dir=plant_output_dir,
                local=plot["local"],
                sem_habitantes="vazio" in efeitos,
            )
            area["no_id"] = plot["no_id"]
            areas.append(area)
            plot["area_index"] = area["index"]
        else:
            _preencher_lote(rng, camada, plot, i, out_dir)
        if "tesouro" in efeitos:
            plot["detalhe"]["tesouro"] = _pick(rng, tables.TREASURE, band_for_layer(camada))

    terreno = terrain.generate_terrain_localizado(
        rng,
        [(p["x"], p["z"], p["detalhe"]["tipo_relevo"]) for p in plots],
        resolution=resolution,
        cell_size=cell_size,
    )
    return {
        "modo": "livro",
        "profundidade_maxima": profundidade_max,
        "terreno": terreno,
        "layout": {
            "field_width": field_width,
            "field_depth": field_depth,
            "plots": plots,
            "arestas": grafo["arestas"],
        },
        "areas": areas,
    }
