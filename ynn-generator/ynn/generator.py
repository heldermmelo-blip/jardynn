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
from lotfp import spells as _lotfp_spells  # noqa: E402
from gielis.plants import generate_fallen_branch as _generate_fallen_branch_mesh  # noqa: E402
from gielis.plants import ESPECIES_L as _ARVORES_L  # noqa: E402
from gielis.plants import generate_plant as _generate_plant_mesh  # noqa: E402
from gielis import ferragens as _ferragens  # noqa: E402
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
FALLEN_BRANCH_COUNT_RANGE = (1, 3)  # onde há ruína, 1d3 galhos caídos

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
# O estado de um lugar vem do Detalhe sorteado (tabela do livro): só "Bem
# Cuidado" e "Coberto de Hera" o deixam inteiro; nos demais jaz em ruínas.
DETALHES_INTEIROS = ("bem_cuidado", "hera")
# Efeitos do Detalhe que mexem na torre (nada de porcentagens minhas):
TORRE_INCLINA_COM = ("estrondo", "convulso", "abismos", "invertido", "flutuante")  # o chão se mexe
TORRE_SEM_TELHADO_COM = ("queimado", "fumegante", "fertil")  # o telhado queimou, ou o mato abriu caminho
TORRE_INCLINACAO_GRAUS = (4.0, 12.0)
TORRE_TOPO_VARIANTES = {"arvore": (1, 2), "arbusto": (2, 3), "flor": (3, 4), "samambaia": (2, 3), "cogumelo": (2, 4)}

# Estufas como no livro: um punhado de dados jogados no papel, cada um uma
# casa de vidro. A face do dado é a planta baixa (`lados` = cantos = portas),
# o d12 tem 2 andares e o d20, 3; o número tirado diz o que tem lá dentro
# (`tables.ESTUFA_CONTEUDO`, de 1 a 12; 13 ou mais é a estufa lacrada).
# `raio` é o raio circunscrito, em metros: dado maior, casa maior.
ESTUFA_DADOS = {
    4: dict(lados=3, raio=2.4, andares=1),
    6: dict(lados=4, raio=3.0, andares=1),
    8: dict(lados=3, raio=3.5, andares=1),
    10: dict(lados=4, raio=4.0, andares=1),
    12: dict(lados=5, raio=4.6, andares=2),
    20: dict(lados=3, raio=5.4, andares=3),
}
ESTUFA_LACRADA_A_PARTIR_DE = 13
ESTUFA_MAX_ANDARES = 3
ESTUFA_MOLDURAS = ("verde", "verdete", "branca", "preta")
ESTUFA_FOLGA = 1.6  # distância mínima entre duas casas do mesmo conjunto
# A flora de cada casa segue o que ela guarda: resultado do dado (1..13) ->
# (tema, densidade). Tema None sorteia; "vazia" não planta nada.
ESTUFA_FLORA_POR_RESULTADO = {
    1: ("tropical", "densa"),
    2: (None, "vazia"),
    3: ("sombra", "media"),
    4: ("tropical", "media"),
    5: ("formal", "media"),
    6: ("formal", "rala"),
    7: ("tropical", "media"),
    8: (None, "vazia"),
    9: ("sombra", "rala"),
    10: ("formal", "rala"),
    11: ("sombra", "densa"),
    12: (None, "media"),
    13: ("tropical", "selva"),
}
ESTUFA_PISO_XADREZ_COM = (6, 10)  # o salão de chá e as gaiolas de ouro: pisos de salão

# Flora de dentro das estufas: varia loucamente de uma pra outra. Cada estufa
# sorteia um tema (ou uma mistura de espécies de vários) e uma densidade,
# desde vazia até uma selva fechada; as em ruína têm menos plantas e boa
# parte delas morta. Espécies são de `gielis.plants`.
ESTUFA_TEMAS = {
    "deserto": ("cacto_coluna", "cacto_barril", "agave", "dracena_dragao"),
    "tropical": ("palmeira", "folha_larga", "samambaia", "videira", "orquidea"),
    "formal": ("topiaria", "cipreste", "rosa", "dalia", "tulipa", "arbusto"),
    "orquidario": ("orquidea", "samambaia", "folha_larga"),
    "sombra": ("samambaia", "cogumelo", "videira", "arbusto"),
}
ESTUFA_TEMA_MISTO_CHANCE = 0.3  # só vale quando o tema não vem do conteúdo
ESTUFA_ESPECIES_ALTAS = ("palmeira", "cipreste", "dracena_dragao")  # não cabem nas pequenas
ESTUFA_ARVORE_ALTURA = (2.5, 4.5)  # as árvores de L-system dentro de uma estufa são mudas, não veteranas
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


TORRE_LIVRO_DE_MAGIAS_CHANCE = 1 / 6  # numa estante revirada, 1 em 6 de achar um livro de magias (de 1º nível)
TORRE_QUADROS_MAX = 4  # 1d4 retratos, cada um vale 100 de ouro x profundidade
TORRE_BIBLIOTECA_DADOS = (("nivel_1", 12), ("nivel_2", 10), ("nivel_3", 8), ("nivel_4", 6), ("nivel_5", 4))


def _montar_andar(rng, entrada, layer, numero, n_andares, topo):
    """Monta o conteúdo de um andar a partir de uma entrada de
    `TORRE_ANDARES`/`TORRE_TOPO`, com a mecânica do livro: uma estante tem
    1 em 6 de esconder um livro de magias; retratos são 1d4, cada um vale 100 de
    ouro vezes a profundidade; no topo, o grande tesouro são 3 achados e o
    monstro poderoso é sorteado somando os andares à profundidade, e a
    biblioteca guarda 1d12 magias de 1º nível, 1d10 de 2º, 1d8 de 3º, 1d6 de
    4º, 1d4 de 5º e uma de 6º ou mais."""
    texto, _bandas, tipo, prop, rotulo = entrada
    band = band_for_layer(layer)
    forte = band_for_layer(layer + n_andares) if topo else band
    andar = {"numero": numero, "texto": texto, "prop": prop, "rotulo": rotulo}
    if tipo == "tesouro":
        if topo and prop == "bau_grande":
            andar["tesouros"] = [_pick(rng, tables.TREASURE, forte) for _ in range(3)]
            andar["tesouro"] = andar["tesouros"][0]
        else:
            andar["tesouro"] = _pick(rng, tables.TREASURE, band)
    elif tipo == "encontro":
        denizen, denizen_class, denizen_creature = _pick_denizen(rng, forte)
        andar["denizen"] = denizen
        if denizen_class is not None:
            andar["npc"] = create_character(rng, denizen_class)
        elif denizen_creature is not None:
            andar["criatura"] = instantiate_creature(rng, denizen_creature)
    if prop == "estante" and rng.random() < TORRE_LIVRO_DE_MAGIAS_CHANCE:
        magia = rng.choice(_lotfp_spells.SPELLS["magic_user"])
        andar["livro_de_magias"] = {"nome": magia["nome"], "descricao": magia["descricao"], "nivel": 1}
    elif prop == "quadros":
        n = rng.randint(1, TORRE_QUADROS_MAX)
        andar["quadros"] = {"quantidade": n, "valor_ouro": n * 100 * layer}
    elif prop == "biblioteca":
        andar["biblioteca"] = {nivel: rng.randint(1, dado) for nivel, dado in TORRE_BIBLIOTECA_DADOS}
        andar["biblioteca"]["nivel_6_ou_mais"] = 1
    return andar


def _vegetation_for_band(band):
    return [(text, species) for text, bands, species in tables.VEGETATION if bands == "all" or band in bands]


def _pick_vegetation(rng, band):
    return rng.choice(_vegetation_for_band(band))


def generate_area(rng, layer, index, plant_output_dir=None, local=None, sem_habitantes=False, ruina=False):
    """`local` (opcional) é o nome do local sorteado no mapa de pontos
    (`ynn.pointcrawl`): abre o texto e substitui o elemento notável sorteado
    em FEATURES. `sem_habitantes` suprime o sorteio de denizens (detalhe
    "vazio"). `ruina` espalha de 1 a 3 galhos caídos: o lugar já não recebe
    cuidado."""
    band = band_for_layer(layer)
    vegetation_text, vegetation_species = _pick_vegetation(rng, band)
    parts = [f"{local}.", vegetation_text] if local else [vegetation_text]
    if local and tables.LOCAL_TEXTOS.get(local):
        parts.insert(1, tables.LOCAL_TEXTOS[local])

    plant_obj_paths = []
    if vegetation_species is not None:
        out_dir = plant_output_dir or PLANT_OUTPUT_DIR
        n_variants = rng.randint(*PLANT_VARIANT_RANGE)
        for variant in range(1, n_variants + 1):
            out_path = os.path.join(out_dir, f"camada{layer}_area{index}_{vegetation_species}_{variant}.obj")
            path, _ = _generate_plant_mesh(rng, vegetation_species, out_path=out_path)
            plant_obj_paths.append(path)

    fallen_branch_paths = []
    if ruina:
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


def sortear_extras_torre(rng, layer, efeitos=()):
    """Efeitos opcionais de uma torre, lidos do Detalhe do local (`efeitos`):
    `topo` (texto, espécie) de `tables.TORRE_BROTO` se o telhado se foi e algo brotou
    ("Fértil"), ou um topo queimado ("Queimado"/"Fumegante": `(texto, None)`), ou
    None se o telhado está inteiro; `trepadeiras` é sempre verdadeiro (a torre do livro
    é coberta de hera); e `inclinacao` (`graus`, `azimute` em rad) se o chão se
    mexe (`TORRE_INCLINA_COM`), ou None."""
    band = band_for_layer(layer)
    topo = None
    if "fertil" in efeitos:
        entradas = [(texto, especie) for texto, especie, bandas in tables.TORRE_BROTO if bandas == "all" or band in bandas]
        topo = rng.choice(entradas)
    elif any(e in efeitos for e in TORRE_SEM_TELHADO_COM):
        topo = ("O telhado queimou e caiu, deixando o topo aberto ao céu, enegrecido.", None)
    inclinacao = None
    if any(e in efeitos for e in TORRE_INCLINA_COM):
        inclinacao = {"graus": rng.uniform(*TORRE_INCLINACAO_GRAUS), "azimute": rng.uniform(0.0, 6.283185307179586)}
    return {"topo": topo, "trepadeiras": True, "inclinacao": inclinacao}


def generate_torre_conteudo(rng, layer, n_andares_range=N_ANDARES_TORRE_RANGE):
    """Sorteia o conteúdo da torre como o livro: `n_andares_range` andares
    (padrão 3-8, o `d6+2` do livro); cada andar de baixo rola 1d12 em
    `tables.TORRE_ANDARES`; o último rola 1d12 duas vezes (sem repetir) em
    `tables.TORRE_TOPO` — por isso `andares` tem uma entrada a mais, com o
    mesmo `numero` do topo e `extra: True` na segunda. Um andar pode carregar
    um tesouro (`tables.TREASURE`) ou um denizen/NPC/criatura."""
    n_andares = rng.randint(*n_andares_range)

    andares = [
        _montar_andar(rng, tables.TORRE_ANDARES[rng.randint(1, 12) - 1], layer, numero, n_andares, False)
        for numero in range(1, n_andares)
    ]
    rolagens = []
    while len(rolagens) < 2:
        r = rng.randint(1, 12)
        if r not in rolagens:
            rolagens.append(r)
    for k, r in enumerate(rolagens):
        andar = _montar_andar(rng, tables.TORRE_TOPO[r - 1], layer, n_andares, n_andares, True)
        if k > 0:
            andar["extra"] = True
        andares.append(andar)

    return {"n_andares": n_andares, "andares": andares}


def sortear_dados_estufa(rng, n=None):
    """Joga um punhado de dados (`1d4 + 1`, ou `n`) pra desenhar as estufas: cada um
    é `{"dado", "resultado"}`, com o resultado de 1 até as faces do dado."""
    n = n or rng.randint(1, 4) + 1
    dados = []
    for _ in range(n):
        dado = rng.choice(sorted(ESTUFA_DADOS))
        dados.append({"dado": dado, "resultado": rng.randint(1, dado)})
    return dados

def _dispor_circulos(rng, raios, folga=ESTUFA_FOLGA):
    """Posiciona círculos de `raios` encostados uns nos outros (com `folga`), como
    dados caídos juntos no papel; o primeiro fica na origem. Devolve as posições."""
    pos = [(0.0, 0.0)]
    for k in range(1, len(raios)):
        melhor = None
        for _ in range(80):
            base = rng.randrange(k)
            ang = rng.uniform(0.0, math.tau)
            dist = raios[base] + raios[k] + folga + rng.uniform(0.0, 1.2)
            c = (pos[base][0] + dist * math.cos(ang), pos[base][1] + dist * math.sin(ang))
            if all(math.hypot(c[0] - q[0], c[1] - q[1]) >= raios[j] + raios[k] + folga - 1e-9 for j, q in enumerate(pos)):
                cx = sum(q[0] for q in pos) / len(pos)
                cz = sum(q[1] for q in pos) / len(pos)
                d0 = math.hypot(c[0] - cx, c[1] - cz)
                if melhor is None or d0 < melhor[0]:
                    melhor = (d0, c)
        pos.append(melhor[1] if melhor else (pos[-1][0] + raios[k - 1] + raios[k] + folga, 0.0))
    cx = sum(q[0] for q in pos) / len(pos)
    cz = sum(q[1] for q in pos) / len(pos)
    return [(x - cx, z - cz) for x, z in pos]

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
                altura = rng.uniform(*ESTUFA_ARVORE_ALTURA) if especie in _ARVORES_L else None
                caminhos[especie].append(_generate_plant_mesh(rng, especie, out_path=path, altura=altura)[0])
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


def _montar_estufas(rng, layer, i, out_dir, orquidario=False, ruina=False, n_dados=None):
    """Monta o conjunto de estufas de um local "Estufas" (ou "Orquidários"): joga os
    dados (`sortear_dados_estufa`) e, pra cada um, gera uma casa de vidro com a planta
    baixa do dado, o conteúdo do número tirado e a flora de dentro. As casas ficam
    encostadas, como dados caídos no papel. Devolve os campos do lote: `estufas` (uma por
    dado, com `x`/`z` locais, `planta`, `obj`, `malhas`, `pegadas`, `conteudo`,
    `flora_interna`, `porta_angulo_godot`), `raio_ocupado` e `obj` (o da primeira)."""
    dados = sortear_dados_estufa(rng, n_dados)
    raios = [ESTUFA_DADOS[d["dado"]]["raio"] * rng.uniform(0.94, 1.06) for d in dados]
    posicoes = _dispor_circulos(rng, raios)
    estufas = []
    for k, (d, raio, (px, pz)) in enumerate(zip(dados, raios, posicoes)):
        info_dado = ESTUFA_DADOS[d["dado"]]
        resultado = d["resultado"]
        indice = min(resultado, ESTUFA_LACRADA_A_PARTIR_DE)
        checker = indice in ESTUFA_PISO_XADREZ_COM
        planta = {
            "dado": d["dado"],
            "resultado": resultado,
            "lados": info_dado["lados"],
            "portas": info_dado["lados"],
            "andares": min(info_dado["andares"], ESTUFA_MAX_ANDARES),
            "raio": raio,
            "estado": "lastimavel" if ruina else "conservada",
            "piso_xadrez": checker,
            "moldura": "ferrugem" if ruina else rng.choice(ESTUFA_MOLDURAS),
            "lacrada": resultado >= ESTUFA_LACRADA_A_PARTIR_DE,
        }
        path, info = _generate_greenhouse_mesh(
            rng,
            sides=planta["lados"],
            n_floors=planta["andares"],
            radius=raio,
            n_wings=0,
            ruined=ruina,
            checker=checker,
            padrao="livre",
            out_path=os.path.join(out_dir, f"camada{layer}_estufa_{i}_{k + 1}.obj"),
        )
        conteudo = (
            generate_orquidario_conteudo(rng, layer, resultado) if orquidario else generate_estufa_conteudo(rng, layer, resultado)
        )
        pegadas = [[(x, -y) for x, y in poly] for poly in info["pegadas"]]
        tema, densidade = ESTUFA_FLORA_POR_RESULTADO[indice]
        if orquidario:
            tema = "orquidario"
            densidade = "media" if densidade == "vazia" else densidade  # um orquidário sempre tem orquídeas
        flora_rng = random.Random(f"flora-{layer}-{i}-{k}-{raio:.3f}-{resultado}")
        flora = sortear_flora_interna(
            flora_rng, pegadas, raio, ruina, out_dir, f"camada{layer}_estufa_{i}_{k + 1}", tema=tema, densidade=densidade
        )
        estufa = {
            "dado": d["dado"],
            "resultado": resultado,
            "x": round(px, 3),
            "z": round(pz, 3),
            "planta": planta,
            "obj": path,
            "malhas": info["malhas"],
            "pegadas": pegadas,
            "raio_ocupado": info["raio_ocupado"],
            "conteudo": conteudo,
            "flora_interna": flora,
        }
        if info["portas_angulos"]:
            estufa["porta_angulo_godot"] = -info["portas_angulos"][0]
        estufas.append(estufa)
    raio_total = max(math.hypot(e["x"], e["z"]) + e["raio_ocupado"] for e in estufas) + 1.0
    return {"estufas": estufas, "raio_ocupado": raio_total, "obj": estufas[0]["obj"]}

def _montar_cupula(rng, out_dir, prefixo, raio, ruina):
    """Cúpula de vidro sobre um local "Teto de Vidro": o lugar inteiro fica dentro de
    uma única estufa gigante (32 lados, 2 ou 3 pavimentos), com uma porta voltada pro
    caminho. Devolve `raio`, `andares`, `obj`, `malhas`, `estado` e `porta_angulo_godot`."""
    andares = 2 if raio < 14.0 else 3
    path, info = _generate_greenhouse_mesh(
        rng,
        sides=32,
        n_floors=andares,
        radius=raio,
        bay=max(1.25, raio / 16.0),
        fase=math.pi / 2 - math.pi / 32,
        portas_angulos=[math.pi / 2],
        ruined=ruina,
        checker=False,
        out_path=os.path.join(out_dir, f"{prefixo}_cupula.obj"),
    )
    return {
        "raio": raio,
        "andares": andares,
        "obj": path,
        "malhas": info["malhas"],
        "estado": "lastimavel" if ruina else "conservada",
        "porta_angulo_godot": -math.pi / 2,
    }


def _montar_estufa_colossal(rng, out_dir, raio, evitar=(), ruina=True):
    """A estufa cuja circunferência abarca o nível inteiro: um domo de 32
    lados e 3 pavimentos centrado na origem, com um portal de entrada do lado
    da entrada do mapa (z negativo) e outro de saída no lado oposto."""
    lados = 32
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
        "piso_xadrez": True,
        "moldura": "ferrugem" if ruina else rng.choice(ESTUFA_MOLDURAS),
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

def generate_estufa_conteudo(rng, layer, resultado=None):
    """O conteúdo de uma casa de vidro, na tabela do livro (`tables.ESTUFA_CONTEUDO`):
    o número tirado no dado (`resultado`, de 1 a 12; 13 ou mais é a estufa lacrada) diz
    o que há lá dentro. Rola 1d12 se não vier um resultado. Devolve `texto`, `resultado`
    e, conforme o item, `valor_ouro` (plantas raras: 1d4 + profundidade; gaiolas: 1d10 +
    profundidade) ou `criatura` e `quantidade` (os jarros carnívoros são 1d4 + 1)."""
    resultado = resultado if resultado is not None else rng.randint(1, 12)
    indice = min(resultado, ESTUFA_LACRADA_A_PARTIR_DE)
    texto, _bandas, tipo, criatura_key = tables.ESTUFA_CONTEUDO[indice - 1]
    conteudo = {"texto": texto, "resultado": resultado}
    if tipo == "valor":
        conteudo["valor_ouro"] = (rng.randint(1, 4) if indice == 1 else rng.randint(1, 10)) + layer
    elif tipo == "criatura":
        conteudo["criatura"] = instantiate_creature(rng, criatura_key)
        if criatura_key == "jarro_carnivoro":
            conteudo["quantidade"] = rng.randint(1, 4) + 1
    return conteudo

PITORESCOS = tuple(_pitoresco.GERADORES)  # tipos de lote que são estruturas pitorescas do livro
PITORESCO_MARGEM_TERRENO = 3.0


def _montar_pitoresco(rng, tipo, layer, i, out_dir, ruina=True):
    """Gera a malha de uma estrutura pitoresca (fonte, estátuas, labirinto,
    mausoléu, lago ou gramado de xadrez) e devolve os campos do lote: `obj`
    (grupo principal), `malhas` (uma por material), `raio_ocupado`,
    `rotacao_y` (sorteada; ou, se a estrutura tem porta, a que a vira pro
    caminho, ajustada depois) e os dados extras da própria estrutura."""
    out_path = os.path.join(out_dir, f"camada{layer}_{tipo}_{i}.obj")
    estilo = _ferragens.sortear_estilo(rng)
    path, info = _pitoresco.GERADORES[tipo](rng, out_path=out_path, ruina=ruina, estilo=estilo)
    campos = {
        "estado": "ruina" if ruina else "intacta",
        "estilo": estilo,
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


def generate_orquidario_conteudo(rng, layer, resultado=None):
    """Conteúdo de um orquidário: sempre orquídeas raras, que um colecionador compra por
    `1d10 x profundidade` de prata (`valor_prata`). Como no livro, é a tabela das estufas,
    mas os resultados pares viram "nada de interessante além das orquídeas"."""
    resultado = resultado if resultado is not None else rng.randint(1, 12)
    texto = rng.choice(tables.ORQUIDARIO_TEXTOS)
    conteudo = {"texto": texto, "valor_prata": rng.randint(1, 10) * layer, "orquidario": True, "resultado": resultado}
    if resultado % 2 == 0 and resultado < ESTUFA_LACRADA_A_PARTIR_DE:
        return conteudo
    extra = generate_estufa_conteudo(rng, layer, resultado)
    conteudo["texto"] = f"{texto} {extra['texto']}"
    for chave in ("valor_ouro", "criatura", "quantidade"):
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


def _preencher_lote(rng, layer, plot, i, out_dir, efeitos=None):
    """Gera a malha e o conteúdo de um lote não-narrativo (torre, estufa,
    gazebo ou canteiro), gravando os resultados no próprio `plot`. `i` só
    entra no nome dos arquivos. `efeitos` são os do Detalhe do local: ele decide
    se a estrutura está inteira ("Bem Cuidado"/"Coberto de Hera") ou em ruínas; sem
    `efeitos`, rola um Detalhe na profundidade do lote (`layer - 1`)."""
    if efeitos is None:
        detalhe = plot.get("detalhe") or pointcrawl.roll_detalhe(rng, layer - 1)
        plot.setdefault("detalhe", detalhe)
        efeitos = detalhe["efeitos"]
    ruina = not any(e in efeitos for e in DETALHES_INTEIROS)
    if plot["tipo"] == "torre":
        conteudo = generate_torre_conteudo(rng, layer)
        out_path = os.path.join(out_dir, f"camada{layer}_torre_{i}.obj")
        estilo = _ferragens.sortear_estilo(rng)
        extras = sortear_extras_torre(rng, layer, efeitos)
        path, skeleton = _generate_tower_mesh(
            rng, conteudo["n_andares"], out_path=out_path, roof=extras["topo"] is None, estilo=estilo, ruina=ruina
        )
        plot["estado"] = "ruina" if ruina else "intacta"
        plot["estilo"] = estilo
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
            "janelas": skeleton[0]["janelas"],
        }
        plot["malhas"] = skeleton[0]["malhas"]  # tijolo, madeira, telhado, tapete, água, papel
        plot["porta"] = {"estado": "entreaberta"}

        n_ivy = rng.randint(*IVY_VARIANT_RANGE)
        ivy_paths = []
        for variant in range(1, n_ivy + 1):
            ivy_path = os.path.join(out_dir, f"camada{layer}_torre_{i}_hera_{variant}.obj")
            path, _ = _generate_plant_mesh(rng, "videira", out_path=ivy_path)
            ivy_paths.append(path)
        plot["hera_obj"] = ivy_paths

        if extras["topo"] is not None:
            texto_topo, especie_topo = extras["topo"]
            if especie_topo is None:  # telhado queimado: o topo fica aberto e enegrecido, sem nada brotando
                conteudo["topo_queimado"] = {"texto": texto_topo}
            else:
                paths = []
                for variant in range(1, rng.randint(*TORRE_TOPO_VARIANTES[especie_topo]) + 1):
                    topo_path = os.path.join(out_dir, f"camada{layer}_torre_{i}_topo_{variant}.obj")
                    path, _ = _generate_plant_mesh(rng, especie_topo, out_path=topo_path)
                    paths.append(path)
                plot["topo_obj"] = paths
                conteudo["topo_brotado"] = {"texto": texto_topo, "especie": especie_topo}
        plot["escalada"] = {
            "andares_com_janela": sorted({j["andar"] for j in skeleton[0]["janelas"]}),
            "trepadeiras": bool(extras["trepadeiras"]),
            "regra": tables.TORRE_ESCALADA_REGRA,
        }
        if extras["trepadeiras"]:
            path, _ = _generate_tower_vines_mesh(
                rng, skeleton, out_path=os.path.join(out_dir, f"camada{layer}_torre_{i}_trepadeiras.obj")
            )
            plot["trepadeiras_obj"] = path
        if extras["inclinacao"] is not None:
            plot["inclinacao"] = extras["inclinacao"]
    elif plot["tipo"] in ("estufa", "orquidario"):
        plot["estado"] = "ruina" if ruina else "intacta"
        plot.update(_montar_estufas(rng, layer, i, out_dir, orquidario=plot["tipo"] == "orquidario", ruina=ruina))
    elif plot["tipo"] == "gazebo":
        out_path = os.path.join(out_dir, f"camada{layer}_gazebo_{i}.obj")
        estilo = _ferragens.sortear_estilo(rng)
        path, skeleton = _generate_gazebo_mesh(rng, out_path=out_path, estilo=estilo, ruina=ruina)
        plot["estado"] = "ruina" if ruina else "intacta"
        plot["estilo"] = estilo
        plot["malhas"] = skeleton[0]["malhas"]
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


def _ruina(efeitos):
    """Um lugar só está inteiro se o Detalhe é "Bem Cuidado" ou "Coberto de Hera"."""
    return not any(e in efeitos for e in DETALHES_INTEIROS)


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
    profundidade` (Local e Detalhe, as tabelas do livro). Os nós viram lotes
    posicionados no campo; a profundidade de um nó (+1) faz o papel do número da camada
    para escolher a banda de conteúdo. O Detalhe de cada nó decide o estado do lugar (só
    "Bem Cuidado" e "Coberto de Hera" o deixam inteiro; os demais jazem em ruínas), a torre
    inclinada, o telhado queimado, a cúpula de vidro etc.

    As estufas e estruturas são montadas antes do layout, que precisa dos tamanhos delas
    pra não as sobrepor. `estufa_colossal`: "auto" (as cúpulas de vidro vêm do Detalhe
    "Teto de Vidro"), "sempre" (força a estufa colossal que cobre o nível inteiro, só de alas
    de vidro, com entrada e saída em lados opostos) ou "nunca" (ignora o vidro).

    Devolve um dict pronto para virar JSON: `terreno`, `layout` (com `plots`, `arestas` e, se
    houver, `portas_estufa`), `areas` (o conteúdo narrativo dos nós do tipo "area", cruzado
    por `area_index`) e, se houver, `estufa_colossal`."""
    grafo = pointcrawl.generate_pointcrawl(rng, profundidade_max, max_nos)
    out_dir = plant_output_dir or PLANT_OUTPUT_DIR

    colossal = estufa_colossal == "sempre"
    if colossal:
        for no in grafo["nos"]:
            (nome, subtipo), _ = pointcrawl.roll_tabela(rng, tables.ALAS_VIDRO, no["profundidade"])
            no["tipo"], no["local"], no["ala"] = "estufa", nome, subtipo

    estufas = {}
    for no in grafo["nos"]:
        if no["tipo"] not in ("estufa", "orquidario"):
            continue
        camada = no["profundidade"] + 1
        ruina = _ruina(no["detalhe"]["efeitos"])
        if colossal:
            orquidario = no["ala"] == "orquidario"
            campos = _montar_estufas(rng, camada, no["id"] + 1, out_dir, orquidario=orquidario, ruina=ruina, n_dados=1)
            campos["ala"] = no["ala"]
            if orquidario:
                campos["tipo_ala"] = "orquidario"
        else:
            campos = _montar_estufas(rng, camada, no["id"] + 1, out_dir, orquidario=no["tipo"] == "orquidario", ruina=ruina)
        campos["estado"] = "ruina" if ruina else "intacta"
        estufas[no["id"]] = campos

    pitorescos = {}
    if not colossal:
        for no in grafo["nos"]:
            if no["tipo"] in PITORESCOS:
                pitorescos[no["id"]] = _montar_pitoresco(
                    rng, no["tipo"], no["profundidade"] + 1, no["id"] + 1, out_dir, ruina=_ruina(no["detalhe"]["efeitos"])
                )

    # "Teto de Vidro": o lugar inteiro sob uma estufa gigante (uma cúpula sobre o lote)
    cupulas = {}
    if not colossal and estufa_colossal != "nunca":
        for no in grafo["nos"]:
            if "vidro" in no["detalhe"]["efeitos"]:
                base = max({**estufas, **pitorescos}.get(no["id"], {"raio_ocupado": 6.0})["raio_ocupado"], 6.0)
                cupulas[no["id"]] = _montar_cupula(
                    rng, out_dir, f"camada{no['profundidade'] + 1}_no{no['id'] + 1}", base + 3.0, _ruina(no["detalhe"]["efeitos"])
                )

    raios = {id_: campos["raio_ocupado"] for id_, campos in {**estufas, **pitorescos}.items()}
    for id_, cupula in cupulas.items():
        raios[id_] = cupula["raio"] + 1.0
    plots = pointcrawl.layout_grafo(rng, grafo, field_width, field_depth, raios=raios)
    posicao = {p["no_id"]: p for p in plots}

    def direcao_do_pai(plot):
        pai = grafo["nos"][plot["no_id"]]["pai"]
        alvo = posicao[pai] if pai is not None else None
        return math.atan2(alvo["z"] - plot["z"], alvo["x"] - plot["x"]) if alvo else math.pi / 2

    areas = []
    for i, plot in enumerate(plots, start=1):
        camada = plot["profundidade"] + 1
        efeitos = plot["detalhe"]["efeitos"]
        ruina = _ruina(efeitos)
        plot["estado"] = "ruina" if ruina else "intacta"
        if plot["tipo"] == "area":
            area = generate_area(
                rng,
                camada,
                len(areas) + 1,
                plant_output_dir=plant_output_dir,
                local=plot["local"],
                sem_habitantes="vazio" in efeitos,
                ruina=ruina,
            )
            area["no_id"] = plot["no_id"]
            areas.append(area)
            plot["area_index"] = area["index"]
        elif plot["tipo"] in ("estufa", "orquidario"):
            plot.update(estufas[plot["no_id"]])
            direcao = direcao_do_pai(plot)
            for estufa in plot["estufas"]:
                if "porta_angulo_godot" in estufa:
                    estufa["rotacao_y"] = estufa["porta_angulo_godot"] - direcao
        elif plot["tipo"] in PITORESCOS:
            plot.update(pitorescos[plot["no_id"]])
            if "porta_angulo_godot" in plot:
                plot["rotacao_y"] = plot["porta_angulo_godot"] - direcao_do_pai(plot)
        else:
            _preencher_lote(rng, camada, plot, i, out_dir, efeitos)
        if plot["no_id"] in cupulas:
            cupula = cupulas[plot["no_id"]]
            cupula["rotacao_y"] = cupula["porta_angulo_godot"] - direcao_do_pai(plot)
            plot["cupula_vidro"] = cupula
        if "tesouro" in efeitos:
            band = band_for_layer(camada)
            plot["detalhe"]["prata"] = sum(rng.randint(1, 10) for _ in range(5)) * 1  # 5d10 de prata
            plot["detalhe"]["tesouros"] = [_pick(rng, tables.TREASURE, band) for _ in range(2)]
            plot["detalhe"]["tesouro"] = plot["detalhe"]["tesouros"][0]

    terreno = terrain.generate_terrain_localizado(
        rng,
        [(p["x"], p["z"], p["detalhe"]["tipo_relevo"]) for p in plots],
        resolution=resolution,
        cell_size=cell_size,
    )
    for plot in plots:
        if plot["tipo"] in PITORESCOS or plot["tipo"] in ("estufa", "orquidario") or "cupula_vidro" in plot:
            terrain.achatar_circulo(terreno, plot["x"], plot["z"], plot["raio_ocupado"] if "raio_ocupado" in plot else plot["cupula_vidro"]["raio"], PITORESCO_MARGEM_TERRENO)

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
        ruina_colossal = _ruina(grafo["nos"][0]["detalhe"]["efeitos"])
        colossal = _montar_estufa_colossal(
            rng, out_dir, min(80.0, max(55.0, afastamento + 6.0)), evitar=evitar, ruina=ruina_colossal
        )
        mais_fundo = max(grafo["nos"], key=lambda no: (no["profundidade"], no["id"]))["id"]
        entrada, saida = colossal["portas"]
        entrada["no_id"], saida["no_id"] = 0, mais_fundo
        posicao[mais_fundo]["saida_nivel"] = True
        nivel["layout"]["portas_estufa"] = colossal["portas"]
        nivel["estufa_colossal"] = colossal
    return nivel
