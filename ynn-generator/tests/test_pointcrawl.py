import json
import os
import random

from ynn import pointcrawl, tables
from ynn.generator import generate_area, generate_nivel
from ynn.pointcrawl import generate_pointcrawl, layout_grafo, roll_detalhe, roll_tabela

from ynn.generator import PITORESCOS

EFEITOS_DO_LIVRO = {
    "vazio", "tesouro", "grafite", "bem_cuidado", "exploradores_mortos", "ninhos", "estrondo", "poste", "filigrana", "tubos",
    "armacoes", "passaros_mortos", "alagado", "queimado", "congelado", "hera", "cantante", "vidro", "esqueletos_sidhe",
    "relojoaria", "invertido", "flutuante", "abismos", "fumegante", "convulso", "predador", "carnudo", "enfeiticante",
    "fertil", "luminoso", "gravidade_zero", "hipnotico", "parasitado", "saida", "loucura",
}
TIPOS_DE_LOTE = ("area", "canteiro", "estufa", "orquidario", "gazebo", "torre", *PITORESCOS)


def test_tables_are_well_formed():
    assert len(tables.LOCAIS) == 35 and len(tables.DETALHES) == 35
    for nome, tipo in tables.LOCAIS:
        assert nome and tipo in TIPOS_DE_LOTE
    for texto, relevo, efeito in tables.DETALHES:
        assert texto and relevo in pointcrawl.RELEVO_ORDEM
        assert efeito and efeito in EFEITOS_DO_LIVRO


def test_roll_is_d20_plus_depth_and_clamped_to_table():
    rng = random.Random(0)
    for profundidade in (0, 3, 40):
        for _ in range(200):
            entrada, bruto = roll_tabela(rng, tables.LOCAIS, profundidade)
            assert 1 + profundidade <= bruto <= 20 + profundidade
            assert entrada == tables.LOCAIS[min(bruto, 35) - 1]
    # Fundo o bastante, sempre cai na última entrada ("Ruínas").
    assert roll_tabela(random.Random(1), tables.LOCAIS, 40)[0] == tables.LOCAIS[-1]


def test_deeper_means_stranger():
    rng = random.Random(2)
    rasos = [roll_detalhe(rng, 0) for _ in range(500)]
    fundos = [roll_detalhe(rng, 15) for _ in range(500)]
    assert not any(d["tipo_relevo"] == "irregular" for d in rasos)
    assert not any("saida" in d["efeitos"] for d in rasos)
    assert any(d["tipo_relevo"] == "irregular" for d in fundos)
    assert any("saida" in d["efeitos"] for d in fundos)


def test_tables_follow_the_books_order_of_locations_and_details():
    nomes = [n for n, _ in tables.LOCAIS]
    assert nomes[0] == "Gramado Aparado" and nomes[6] == "Gazebo" and nomes[7] == "Estufas" and nomes[8] == "Orquidários"
    assert nomes[11] == "Labirinto de Sebes" and nomes[15] == "Mausoléu" and nomes[20] == "Torre" and nomes[34] == "Ruínas de Ynn"
    efeitos = [e for _, _, e in tables.DETALHES]
    assert efeitos[0] == "vazio" and efeitos[3] == "bem_cuidado" and efeitos[12] == "alagado" and efeitos[13] == "queimado"
    assert efeitos[14] == "congelado" and efeitos[15] == "hera" and efeitos[17] == "vidro" and efeitos[33] == "saida"
    assert len(set(efeitos)) == 35  # cada detalhe tem a sua etiqueta


def test_detail_roll_reports_its_table_index_and_only_two_details_leave_a_place_whole():
    from ynn.generator import DETALHES_INTEIROS

    assert set(DETALHES_INTEIROS) == {"bem_cuidado", "hera"}
    for seed in range(200):
        for profundidade in (0, 5, 40):
            d = roll_detalhe(random.Random(seed), profundidade)
            assert 1 <= d["indice"] <= 35
            assert d["efeitos"] == [tables.DETALHES[d["indice"] - 1][2]]
            assert d["texto"] == tables.DETALHES[d["indice"] - 1][0]
    # "Bem Cuidado" (4) só sai se d20 + profundidade for 4: impossível a partir da profundidade 4
    assert not any("bem_cuidado" in roll_detalhe(random.Random(s), 4)["efeitos"] for s in range(500))
    assert any("bem_cuidado" in roll_detalhe(random.Random(s), 0)["efeitos"] for s in range(500))


def test_graph_has_a_node_in_every_layer_and_is_a_connected_tree_plus_extras():
    for seed in range(40):
        grafo = generate_pointcrawl(random.Random(seed), profundidade_max=4, max_nos=14)
        nos, arestas = grafo["nos"], grafo["arestas"]
        assert [n["id"] for n in nos] == list(range(len(nos)))
        assert len([n for n in nos if n["profundidade"] == 0]) == 1
        for profundidade in range(5):
            assert any(n["profundidade"] == profundidade for n in nos)
        assert len(nos) <= 14 + 4  # o teto pode ser furado só pra garantir uma camada
        trilhas = [a for a in arestas if a["tipo"] == "trilha"]
        assert len(trilhas) == len(nos) - 1
        for a in trilhas:
            assert nos[a["para"]]["profundidade"] == nos[a["de"]]["profundidade"] + 1
            assert nos[a["para"]]["pai"] == a["de"]
        pares = [frozenset((a["de"], a["para"])) for a in arestas]
        assert len(pares) == len(set(pares))  # sem arestas repetidas
        assert all(0 <= a["de"] < len(nos) and 0 <= a["para"] < len(nos) for a in arestas)


def test_extra_links_follow_their_rules():
    vistos = set()
    for seed in range(80):
        grafo = generate_pointcrawl(random.Random(seed), profundidade_max=5, max_nos=16)
        nos = grafo["nos"]
        for a in grafo["arestas"]:
            vistos.add(a["tipo"])
            if a["tipo"] == "atalho":
                assert nos[a["para"]]["profundidade"] < nos[a["de"]]["profundidade"]
            elif a["tipo"] == "descida":
                assert nos[a["para"]]["profundidade"] >= nos[a["de"]]["profundidade"] + 2
    assert vistos == {"trilha", "atalho", "descida"}


def test_nodes_get_location_and_detail_rolled_at_their_depth():
    grafo = generate_pointcrawl(random.Random(3))
    for no in grafo["nos"]:
        assert no["local"] and no["tipo"] in TIPOS_DE_LOTE
        assert no["detalhe"]["texto"]


def test_graph_is_deterministic():
    assert generate_pointcrawl(random.Random(42)) == generate_pointcrawl(random.Random(42))


def test_layout_puts_entrance_on_top_and_deeper_layers_below():
    for seed in range(30):
        rng = random.Random(seed)
        grafo = generate_pointcrawl(rng, profundidade_max=4)
        plots = layout_grafo(rng, grafo, field_width=105.0, field_depth=68.0)
        assert len(plots) == len(grafo["nos"])
        z_medio = {}
        for p in plots:
            z_medio.setdefault(p["profundidade"], []).append(p["z"])
            assert -52.5 <= p["x"] <= 52.5 and -34 <= p["z"] <= 34
        medias = [sum(z) / len(z) for _, z in sorted(z_medio.items())]
        assert medias == sorted(medias) and medias[0] < medias[-1]


def test_layout_keeps_nodes_of_a_layer_apart():
    for seed in range(30):
        rng = random.Random(seed)
        grafo = generate_pointcrawl(rng, profundidade_max=4)
        plots = layout_grafo(rng, grafo)
        por_camada = {}
        for p in plots:
            por_camada.setdefault(p["profundidade"], []).append(p["x"])
        for xs in por_camada.values():
            xs.sort()
            assert all(b - a >= 16.0 - 3.0 - 1e-6 for a, b in zip(xs, xs[1:]))  # folga menos o jitter


def test_area_with_local_and_empty_detail():
    for seed in range(3):
        area = generate_area(random.Random(seed), layer=3, index=1, local="Pérgula de glicínias", sem_habitantes=True)
        assert area["text"].startswith("Pérgula de glicínias.")
        assert "Aqui há" not in area["text"]
        assert area["npc"] is None and area["criatura"] is None and not area["has_denizen"]


def test_generate_nivel_produces_a_consistent_json_ready_level(tmp_path):
    nivel = generate_nivel(random.Random(7), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path))
    json.dumps(nivel)  # serializável

    layout = nivel["layout"]
    ids = [p["no_id"] for p in layout["plots"]]
    assert sorted(ids) == list(range(len(ids)))
    assert all(a["de"] in ids and a["para"] in ids for a in layout["arestas"])

    areas = {a["index"]: a for a in nivel["areas"]}
    for p in layout["plots"]:
        assert p["detalhe"]["texto"] and p["local"]
        if p["tipo"] == "area":
            assert areas[p["area_index"]]["no_id"] == p["no_id"]
            assert areas[p["area_index"]]["text"].startswith(p["local"])
        else:
            assert "area_index" not in p
            assert os.path.exists(p["obj"] if "obj" in p else p["plantas_obj"][0])

    terreno = nivel["terreno"]
    assert terreno["localizado"] is True
    assert len(terreno["alturas"]) == terreno["resolucao"]
