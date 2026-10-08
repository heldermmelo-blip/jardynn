"""Montagem de áreas e camadas de jardim a partir das tabelas em `tables.py`."""

import math
import os
import random
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
from gielis import pitoresco as _pitoresco  # noqa: E402
from gielis.structures import generate_gazebo as _generate_gazebo_mesh  # noqa: E402
from gielis.greenhouse import generate_greenhouse as _generate_greenhouse_mesh  # noqa: E402
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
CANTEIRO_SPECIES = ("flor", "rosa", "dalia", "margarida", "tulipa", "lavanda", "arbusto")
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

# Portes das estufas: minúsculas, normais e imensas (com várias alas). Há
# ainda a colossal — uma estufa cuja circunferência abarca o nível inteiro,
# com um portal de entrada e outro de saída em lados opostos —, a mais rara
# de todas (1 em 30). Cada estufa pode estar em estado lastimável (painéis
# faltando, moldura enferrujada, trepadeiras mortas) e ter piso em xadrez
# preto e branco; uma minúscula, uma vez em dez, fica no meio de um espelho
# d'água, com um caminho até ela.
ESTUFA_PORTES = ("minuscula", "normal", "imensa")
ESTUFA_PORTES_PESOS = (2, 6, 2)
ESTUFA_COLOSSAL_CHANCE = 1 / 30
ESTUFA_RUINA_CHANCE = 0.4
ESTUFA_XADREZ_CHANCE = 0.3
ESTUFA_ESPELHO_CHANCE = 1 / 10
ESTUFA_MAX_ANDARES = 3
ESTUFA_MOLDURAS = ("verde", "verdete", "branca", "preta")

# Flora de dentro das estufas: varia loucamente de uma pra outra. Cada estufa
# sorteia um tema (ou uma mistura de espécies de vários) e uma densidade,
# desde vazia até uma selva fechada; as em ruína têm menos plantas e boa
# parte delas morta. Espécies são de `gielis.plants`.
ESTUFA_TEMAS = {
    "deserto": ("cacto_coluna", "cacto_barril", "agave"),
    "tropical": ("palmeira", "folha_larga", "samambaia", "videira", "orquidea"),
    "formal": ("topiaria", "cipreste", "rosa", "dalia", "tulipa", "arbusto"),
    "orquidario": ("orquidea", "samambaia", "folha_larga"),
    "sombra": ("samambaia", "cogumelo", "videira", "arbusto"),
}
ESTUFA_TEMA_MISTO_CHANCE = 0.3
ESTUFA_ESPECIES_ALTAS = ("palmeira", "cipreste")  # não cabem nas pequenas
ESTUFA_FLORA_ALTURA_MIN_RAIO = 3.2
# densidade -> (plantas por m², peso se conservada, peso se em ruína)
ESTUFA_DENSIDADES = {
    "vazia": (0.0, 1, 3),
    "rala": (0.05, 3, 4),
    "media": (0.12, 4, 3),
    "densa": (0.25, 3, 1),
    "selva": (0.5, 2, 0),
}
ESTUFA_FLORA_VARIANTES = (2, 3)
ESTUFA_FLORA_MAX_PLANTAS = 260
ESTUFA_FLORA_MARGEM = 0.35  # folga da parede, em metros
ESTUFA_MORTAS_RUINA = (0.4, 0.9)
# alas dentro da colossal: só minúsculas e normais (as imensas não cabem sob o vidro junto com as outras)
ESTUFA_COLOSSAL_ALAS_PESOS = (3, 6)
ESTUFA_COLOSSAL_FLORA_MAX = 500
ESTUFA_COLOSSAL_FLORA_ESCALA = 2.5  # o vidro dela é enorme: plantas maiores

ESTUFA_COLOSSAL_TEXTO = (
    "O nível inteiro está sob o vidro de uma estufa colossal. Os aventureiros entram por um portal "
    "de ferro e vidro numa ponta e só encontram a saída do outro lado."
)

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
        "especie_vegetacao": vegetation_species,
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


def generate_estufa_planta(rng, porte=None):
    """Sorteia a planta de uma estufa: o `porte` (minúscula, normal ou
    imensa), o "dado" que dá a forma e o tamanho (a face do dado é a planta
    baixa; `lados` = cantos = portas), os andares (no máximo
    `ESTUFA_MAX_ANDARES`), o raio, as alas e o padrão delas ("palacio": duas
    alas laterais; "cruz": quatro; "livre": quantas sortear), o estado
    (conservada ou lastimável), o piso em xadrez e a cor da moldura."""
    porte = porte or rng.choices(ESTUFA_PORTES, weights=ESTUFA_PORTES_PESOS)[0]
    dados = list(ESTUFA_DADOS)
    if porte == "minuscula":
        dado = rng.choice([4, 6])
        lados = ESTUFA_DADOS[dado]["lados"]
        raio = rng.uniform(1.2, 1.9)
        andares, alas, padrao = 1, 0, "livre"
    elif porte == "imensa":
        dado = rng.choice([12, 20])
        lados = rng.choice([4, 5, 6, 8])
        raio = rng.uniform(4.5, 6.5)
        andares = rng.choice([2, 3])
        padrao = rng.choices(["palacio", "cruz", "livre"], weights=[3, 3, 4])[0]
        alas = {"palacio": 2 + rng.randint(0, 3), "cruz": 4 + rng.randint(0, 4), "livre": rng.randint(5, 9)}[padrao]
    else:
        dado = rng.choices(dados, weights=[ESTUFA_DADOS[d]["peso"] for d in dados])[0]
        info = ESTUFA_DADOS[dado]
        lados, raio, andares = info["lados"], info["raio"], info["andares"]
        padrao = rng.choices(["livre", "palacio"], weights=[8, 2])[0]
        if padrao == "palacio":
            alas, andares = 2, max(andares, 2)
        else:
            alas = 0 if rng.random() < 0.6 else rng.randint(1, 3)
    ruina = rng.random() < ESTUFA_RUINA_CHANCE
    moldura = "ferrugem" if ruina and rng.random() < 0.7 else rng.choice(ESTUFA_MOLDURAS)
    return {
        "porte": porte,
        "dado": dado,
        "lados": lados,
        "portas": lados,
        "andares": min(andares, ESTUFA_MAX_ANDARES),
        "raio": raio,
        "alas": alas,
        "padrao": padrao,
        "estado": "lastimavel" if ruina else "conservada",
        "piso_xadrez": rng.random() < ESTUFA_XADREZ_CHANCE,
        "moldura": moldura,
    }


def _sorteou_colossal(rng, modo):
    """A estufa colossal (a que cobre o nível inteiro) é a mais rara de
    todas: `modo` "auto" sorteia 1 em 30 por estufa
    (`ESTUFA_COLOSSAL_CHANCE`), "sempre" sempre sai e "nunca" nunca."""
    if modo == "sempre":
        return True
    if modo == "nunca":
        return False
    return rng.random() < ESTUFA_COLOSSAL_CHANCE


def _dentro_do_poligono(px, pz, poligono, margem):
    """Ponto dentro de um polígono convexo, a pelo menos `margem` de cada
    lado."""
    n = len(poligono)
    area2 = sum(poligono[k][0] * poligono[(k + 1) % n][1] - poligono[(k + 1) % n][0] * poligono[k][1] for k in range(n))
    sinal = 1.0 if area2 > 0 else -1.0
    for k in range(n):
        x0, z0 = poligono[k]
        x1, z1 = poligono[(k + 1) % n]
        comprimento = math.hypot(x1 - x0, z1 - z0)
        if comprimento < 1e-9:
            continue
        distancia = sinal * ((x1 - x0) * (pz - z0) - (z1 - z0) * (px - x0)) / comprimento
        if distancia < margem:
            return False
    return True


def _area_poligono(poligono):
    n = len(poligono)
    return abs(sum(poligono[k][0] * poligono[(k + 1) % n][1] - poligono[(k + 1) % n][0] * poligono[k][1] for k in range(n))) / 2.0


def sortear_flora_interna(
    rng, poligonos, raio, ruina, out_dir, prefixo, max_plantas=ESTUFA_FLORA_MAX_PLANTAS, tema=None, densidade=None, evitar=(), escala_extra=1.0
):
    """Sorteia a flora de dentro de uma estufa e gera as malhas. `poligonos`
    são as pegadas convexas dela no plano (x, z), em coordenadas locais do
    Godot; `evitar` é uma lista de `(x, z, raio)` onde não plantar. Devolve
    `tema`, `densidade`, `mortas` (fração de plantas mortas), `especies` e
    `plantas` (uma por exemplar: `especie`, `obj`, `x`, `z`, `escala`, `rot`,
    `morta`). `escala_extra` multiplica o tamanho de todas."""
    if tema is None:
        if rng.random() < ESTUFA_TEMA_MISTO_CHANCE:
            tema = "misto"
        else:
            tema = rng.choice([t for t in sorted(ESTUFA_TEMAS) if t != "orquidario"])  # o orquidário é das alas de orquídea
    if tema == "misto":
        todas = sorted({e for lista in ESTUFA_TEMAS.values() for e in lista})
    else:
        todas = list(ESTUFA_TEMAS[tema])
    if raio < ESTUFA_FLORA_ALTURA_MIN_RAIO:
        todas = [e for e in todas if e not in ESTUFA_ESPECIES_ALTAS] or ["arbusto"]
    n_especies = rng.randint(2, min(5, len(todas))) if len(todas) > 1 else 1
    especies = rng.sample(todas, n_especies)

    if densidade is None:
        nomes = list(ESTUFA_DENSIDADES)
        pesos = [ESTUFA_DENSIDADES[n][2 if ruina else 1] for n in nomes]
        densidade = rng.choices(nomes, weights=pesos)[0]
    taxa = ESTUFA_DENSIDADES[densidade][0]
    mortas = rng.uniform(*ESTUFA_MORTAS_RUINA) if ruina else 0.0

    area = sum(_area_poligono(poly) for poly in poligonos)
    quantidade = 0 if taxa == 0.0 else min(max_plantas, max(2, round(area * taxa)))

    escala_max = 1.0 if raio >= 4.0 else max(0.4, raio / 4.0)
    plantas = []
    caminhos = {}
    if quantidade:
        todos = [pt for poly in poligonos for pt in poly]
        x_min, x_max = min(p[0] for p in todos), max(p[0] for p in todos)
        z_min, z_max = min(p[1] for p in todos), max(p[1] for p in todos)
        for especie in especies:
            caminhos[especie] = []
            for v in range(1, rng.randint(*ESTUFA_FLORA_VARIANTES) + 1):
                path = os.path.join(out_dir, f"{prefixo}_flora_{especie}_{v}.obj")
                caminhos[especie].append(_generate_plant_mesh(rng, especie, out_path=path)[0])
        tentativas = 0
        while len(plantas) < quantidade and tentativas < quantidade * 40:
            tentativas += 1
            px, pz = rng.uniform(x_min, x_max), rng.uniform(z_min, z_max)
            if not any(_dentro_do_poligono(px, pz, poly, ESTUFA_FLORA_MARGEM) for poly in poligonos):
                continue
            if any(math.hypot(px - ex, pz - ez) < er for ex, ez, er in evitar):
                continue
            especie = rng.choice(especies)
            plantas.append(
                {
                    "especie": especie,
                    "obj": rng.choice(caminhos[especie]),
                    "x": round(px, 3),
                    "z": round(pz, 3),
                    "escala": round(rng.uniform(0.8, 1.3) * escala_max * escala_extra, 3),
                    "rot": round(rng.uniform(0.0, math.tau), 3),
                    "morta": rng.random() < mortas,
                }
            )
    return {"tema": tema, "densidade": densidade, "mortas": round(mortas, 2), "especies": especies, "plantas": plantas}


def _montar_estufa(rng, layer, i, out_dir, porte=None, espelho_permitido=True, tema_flora=None):
    """Sorteia a planta de uma estufa e gera suas malhas (uma por material).
    Devolve os campos que vão no lote: `planta`, `obj` (a moldura), `malhas`,
    `pegadas` (polígonos no plano (x, z) do Godot, pra espalhar a flora),
    `raio_ocupado`, `conteudo` e, se tiver porta, `porta_angulo_godot`. Uma
    minúscula, uma vez em dez, ganha um `espelho_dagua` ao redor."""
    planta = generate_estufa_planta(rng, porte)
    espelho = None
    if espelho_permitido and planta["porte"] == "minuscula" and rng.random() < ESTUFA_ESPELHO_CHANCE:
        planta["raio"] = rng.uniform(2.2, 2.5)  # ainda a menor classe, mas com porta
        espelho = {"raio": rng.uniform(5.5, 8.0)}
    out_path = os.path.join(out_dir, f"camada{layer}_estufa_{i}.obj")
    path, info = _generate_greenhouse_mesh(
        rng,
        sides=planta["lados"],
        n_floors=planta["andares"],
        radius=planta["raio"],
        n_wings=planta["alas"],
        ruined=planta["estado"] == "lastimavel",
        checker=planta["piso_xadrez"],
        padrao=planta["padrao"],
        out_path=out_path,
    )
    planta["alas"] = info["n_alas"]
    campos = {
        "planta": planta,
        "obj": path,
        "malhas": info["malhas"],
        "pegadas": [[(x, -y) for x, y in poly] for poly in info["pegadas"]],
        "raio_ocupado": info["raio_ocupado"],
        "conteudo": generate_estufa_conteudo(rng, layer),
    }
    if info["portas_angulos"]:
        campos["porta_angulo_godot"] = -info["portas_angulos"][0]
    # rng próprio (semeado pela planta): a flora não muda o resto do nível
    flora_rng = random.Random(f"flora-{layer}-{i}-{planta['raio']:.3f}-{planta['lados']}")
    campos["flora_interna"] = sortear_flora_interna(
        flora_rng,
        campos["pegadas"],
        planta["raio"],
        planta["estado"] == "lastimavel",
        out_dir,
        f"camada{layer}_estufa_{i}",
        tema=tema_flora,
    )
    if espelho is not None:
        campos["espelho_dagua"] = espelho
        campos["raio_ocupado"] = max(info["raio_ocupado"], espelho["raio"] + 1.0)
    return campos


def _montar_estufa_colossal(rng, out_dir, raio, evitar=()):
    """A estufa cuja circunferência abarca o nível inteiro: um domo de 32
    lados e 3 pavimentos centrado na origem, com um portal de entrada do lado
    da entrada do mapa (z negativo) e outro de saída no lado oposto."""
    lados = 32
    ruina = rng.random() < ESTUFA_RUINA_CHANCE
    planta = {
        "porte": "colossal",
        "dado": None,
        "lados": lados,
        "portas": 2,
        "andares": 3,
        "raio": raio,
        "alas": 0,
        "padrao": "colossal",
        "estado": "lastimavel" if ruina else "conservada",
        "piso_xadrez": rng.random() < ESTUFA_XADREZ_CHANCE,
        "moldura": "ferrugem" if ruina and rng.random() < 0.7 else rng.choice(ESTUFA_MOLDURAS),
    }
    path, info = _generate_greenhouse_mesh(
        rng,
        sides=lados,
        n_floors=3,
        radius=raio,
        ruined=ruina,
        checker=planta["piso_xadrez"],
        bay=raio / 18.0,
        fase=math.pi / 2 - math.pi / lados,
        portas_angulos=[math.pi / 2, -math.pi / 2],
        out_path=os.path.join(out_dir, "nivel_estufa_colossal.obj"),
    )
    disco = [(math.cos(math.tau * k / 32) * (raio - 1.5), math.sin(math.tau * k / 32) * (raio - 1.5)) for k in range(32)]
    flora = sortear_flora_interna(
        random.Random(f"flora-colossal-{raio:.3f}"),
        [disco],
        raio,
        ruina,
        out_dir,
        "nivel_estufa_colossal",
        max_plantas=ESTUFA_COLOSSAL_FLORA_MAX,
        tema="tropical",
        densidade="rala" if ruina else "media",
        evitar=evitar,
        escala_extra=ESTUFA_COLOSSAL_FLORA_ESCALA,
    )
    return {
        "planta": planta,
        "obj": path,
        "malhas": info["malhas"],
        "flora_interna": flora,
        "raio": raio,
        "portas": [{"tipo": "entrada", "x": 0.0, "z": -raio}, {"tipo": "saida", "x": 0.0, "z": raio}],
        "texto": ESTUFA_COLOSSAL_TEXTO,
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


PITORESCOS = tuple(_pitoresco.GERADORES)  # tipos de lote que são estruturas pitorescas do livro
PITORESCO_MARGEM_TERRENO = 3.0


def _montar_pitoresco(rng, tipo, layer, i, out_dir):
    """Gera a malha de uma estrutura pitoresca (fonte, estátuas, labirinto,
    mausoléu, lago ou gramado de xadrez) e devolve os campos do lote: `obj`
    (grupo principal), `malhas` (uma por material), `raio_ocupado`,
    `rotacao_y` (sorteada; ou, se a estrutura tem porta, a que a vira pro
    caminho, ajustada depois) e os dados extras da própria estrutura."""
    out_path = os.path.join(out_dir, f"camada{layer}_{tipo}_{i}.obj")
    path, info = _pitoresco.GERADORES[tipo](rng, out_path=out_path)
    campos = {
        "obj": path,
        "malhas": info["malhas"],
        "raio_ocupado": info["raio_ocupado"],
        "pitoresco": {k: v for k, v in info.items() if k not in ("malhas", "raio_ocupado", "porta_angulo")},
    }
    if "porta_angulo" in info:
        campos["porta_angulo_godot"] = -info["porta_angulo"]
    else:
        campos["rotacao_y"] = round(rng.uniform(0.0, math.tau), 3)
    return campos


def generate_orquidario_conteudo(rng, layer):
    """Conteúdo de um orquidário: sempre orquídeas raras, que um colecionador
    compra por `1d10 x profundidade` de prata (`valor_prata`). Em metade das
    vezes não há mais nada; na outra metade, algo mais de `ESTUFA_CONTEUDO`
    (menos o que dispensa plantas, que aqui não faz sentido) divide o lugar
    com as orquídeas."""
    texto = rng.choice(tables.ORQUIDARIO_TEXTOS)
    conteudo = {"texto": texto, "valor_prata": rng.randint(1, 10) * layer, "orquidario": True}
    if rng.random() < 0.5:
        return conteudo
    extra = generate_estufa_conteudo(rng, layer)
    conteudo["texto"] = f"{texto} {extra['texto']}"
    for chave in ("valor_ouro", "criatura"):
        if extra.get(chave) is not None:
            conteudo[chave] = extra[chave]
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
        plot.update(_montar_estufa(rng, layer, i, out_dir))
    elif plot["tipo"] == "gazebo":
        out_path = os.path.join(out_dir, f"camada{layer}_gazebo_{i}.obj")
        path, _ = _generate_gazebo_mesh(rng, out_path=out_path)
        plot["obj"] = path
        plot["conteudo"] = generate_gazebo_conteudo(rng, layer)
    elif plot["tipo"] == "canteiro":
        especie = tables.CANTEIRO_ESPECIE_POR_LOCAL.get(plot.get("local")) or rng.choice(CANTEIRO_SPECIES)
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
    estufa_colossal="auto",
):
    """Produtor de níveis no estilo do livro: um mapa de pontos
    (`ynn.pointcrawl`) com a entrada na camada 0 e locais cada vez mais
    estranhos até `profundidade_max`, cada um sorteado em `d20 +
    profundidade` (Local e Detalhe). Os nós viram lotes posicionados no
    campo; a profundidade de um nó (+1) faz o papel do número da camada
    para escolher a banda de conteúdo. O relevo varia só ao redor dos
    locais cujo detalhe pede (`generate_terrain_localizado`).

    As estufas são montadas antes do layout, que precisa dos tamanhos delas
    pra não as sobrepor (e pra manter as minúsculas afastadas entre si).
    `estufa_colossal`: "auto" (1 em 30 por estufa), "sempre" (força uma) ou
    "nunca". Se sair, o nível inteiro fica sob uma estufa colossal, com
    entrada e saída em lados opostos.

    Devolve um dict pronto para virar JSON: `terreno`, `layout` (com
    `plots`, `arestas` e, se houver, `portas_estufa`), `areas` (o conteúdo
    narrativo dos nós do tipo "area", cruzado por `area_index`) e, se
    houver, `estufa_colossal`."""
    grafo = pointcrawl.generate_pointcrawl(rng, profundidade_max, max_nos)
    out_dir = plant_output_dir or PLANT_OUTPUT_DIR

    nos_estufa = [no for no in grafo["nos"] if no["tipo"] == "estufa"]
    # "sempre" força o nível colossal; em "auto" cada estufa do mapa tem 1 em
    # 30 de ser a colossal. Quando sai, o nível inteiro é só de alas de vidro.
    colossal = estufa_colossal == "sempre" or any(_sorteou_colossal(rng, estufa_colossal) for _ in nos_estufa)
    if colossal:
        for no in grafo["nos"]:
            (nome, subtipo), _ = pointcrawl.roll_tabela(rng, tables.ALAS_VIDRO, no["profundidade"])
            no["tipo"], no["local"], no["ala"] = "estufa", nome, subtipo
        nos_estufa = list(grafo["nos"])

    estufas = {}
    for no in nos_estufa:
        camada = no["profundidade"] + 1
        if colossal:
            porte = rng.choices(["minuscula", "normal"], weights=ESTUFA_COLOSSAL_ALAS_PESOS)[0]
            campos = _montar_estufa(
                rng, camada, no["id"] + 1, out_dir, porte=porte, espelho_permitido=False,
                tema_flora="orquidario" if no["ala"] == "orquidario" else None,
            )
            if no["ala"] == "orquidario":
                campos["conteudo"] = generate_orquidario_conteudo(rng, camada)
            campos["ala"] = no["ala"]
            estufas[no["id"]] = campos
        else:
            estufas[no["id"]] = _montar_estufa(rng, camada, no["id"] + 1, out_dir)

    pitorescos = {}
    if not colossal:
        for no in grafo["nos"]:
            if no["tipo"] in PITORESCOS:
                pitorescos[no["id"]] = _montar_pitoresco(rng, no["tipo"], no["profundidade"] + 1, no["id"] + 1, out_dir)

    raios = {id_: campos["raio_ocupado"] for id_, campos in {**estufas, **pitorescos}.items()}
    # dentro da colossal as alas não precisam se afastar umas das outras como
    # as minúsculas do jardim aberto
    grupos = (
        {}
        if colossal
        else {id_: "minuscula" for id_, campos in estufas.items() if campos["planta"].get("porte") == "minuscula"}
    )
    plots = pointcrawl.layout_grafo(rng, grafo, field_width, field_depth, raios=raios, grupos=grupos)
    posicao = {p["no_id"]: p for p in plots}

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
        elif plot["tipo"] == "estufa":
            plot.update(estufas[plot["no_id"]])
            pai = grafo["nos"][plot["no_id"]]["pai"]
            if "porta_angulo_godot" in plot:
                alvo = posicao[pai] if pai is not None else None
                direcao = math.atan2(alvo["z"] - plot["z"], alvo["x"] - plot["x"]) if alvo else math.pi / 2
                plot["rotacao_y"] = plot["porta_angulo_godot"] - direcao
                if "espelho_dagua" in plot:
                    plot["espelho_dagua"]["caminho_angulo"] = direcao
        elif plot["tipo"] in PITORESCOS:
            plot.update(pitorescos[plot["no_id"]])
            if "porta_angulo_godot" in plot:
                pai = grafo["nos"][plot["no_id"]]["pai"]
                alvo = posicao[pai] if pai is not None else None
                direcao = math.atan2(alvo["z"] - plot["z"], alvo["x"] - plot["x"]) if alvo else math.pi / 2
                plot["rotacao_y"] = plot["porta_angulo_godot"] - direcao
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
    for plot in plots:
        if "espelho_dagua" in plot:
            terrain.achatar_circulo(terreno, plot["x"], plot["z"], plot["espelho_dagua"]["raio"], 3.0)
        elif plot["tipo"] in PITORESCOS:  # labirinto, lago, mausoléu... não ficam em terreno ondulado
            terrain.achatar_circulo(terreno, plot["x"], plot["z"], plot["raio_ocupado"], PITORESCO_MARGEM_TERRENO)

    nivel = {
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
    if colossal:
        afastamento = max(math.hypot(p["x"], p["z"]) + p.get("raio_ocupado", 6.0) for p in plots)
        evitar = [(p["x"], p["z"], p.get("raio_ocupado", 6.0) + 1.5) for p in plots]
        colossal = _montar_estufa_colossal(rng, out_dir, min(80.0, max(55.0, afastamento + 6.0)), evitar=evitar)
        mais_fundo = max(grafo["nos"], key=lambda no: (no["profundidade"], no["id"]))["id"]
        entrada, saida = colossal["portas"]
        entrada["no_id"], saida["no_id"] = 0, mais_fundo
        posicao[mais_fundo]["saida_nivel"] = True
        nivel["layout"]["portas_estufa"] = colossal["portas"]
        nivel["estufa_colossal"] = colossal
    return nivel
