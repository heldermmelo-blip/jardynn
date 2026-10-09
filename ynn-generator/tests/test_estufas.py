import math
import random

import pytest

from ynn import generator, pointcrawl, tables, terrain
from ynn.generator import ESTUFA_DADOS, ESTUFA_LACRADA_A_PARTIR_DE, generate_estufa_conteudo, sortear_dados_estufa


# --- estufas como no livro: dados jogados no papel ----------------------------------------


def test_the_handful_of_dice_is_1d4_plus_1_and_each_result_fits_its_die():
    quantidades = set()
    for seed in range(400):
        dados = sortear_dados_estufa(random.Random(seed))
        quantidades.add(len(dados))
        for d in dados:
            assert d["dado"] in ESTUFA_DADOS and 1 <= d["resultado"] <= d["dado"]
    assert quantidades == {2, 3, 4, 5}
    assert len(sortear_dados_estufa(random.Random(1), n=1)) == 1


def test_dice_give_the_floorplan_and_the_d12_and_d20_have_more_floors():
    assert {d: info["andares"] for d, info in ESTUFA_DADOS.items()} == {4: 1, 6: 1, 8: 1, 10: 1, 12: 2, 20: 3}
    assert ESTUFA_DADOS[4]["lados"] == ESTUFA_DADOS[8]["lados"] == ESTUFA_DADOS[20]["lados"] == 3
    assert ESTUFA_DADOS[6]["lados"] == ESTUFA_DADOS[10]["lados"] == 4
    assert ESTUFA_DADOS[12]["lados"] == 5
    raios = [ESTUFA_DADOS[d]["raio"] for d in (4, 6, 8, 10, 12, 20)]
    assert raios == sorted(raios)  # dado maior, casa maior


def test_greenhouse_content_follows_the_number_rolled_in_the_books_order():
    for resultado in range(1, 14):
        c = generate_estufa_conteudo(random.Random(resultado), 3, resultado)
        assert c["texto"] == tables.ESTUFA_CONTEUDO[resultado - 1][0] and c["resultado"] == resultado
    assert generate_estufa_conteudo(random.Random(1), 3, 19)["texto"] == tables.ESTUFA_CONTEUDO[12][0]  # lacrada
    assert ESTUFA_LACRADA_A_PARTIR_DE == 13 and max(ESTUFA_DADOS) == 20
    assert len(tables.ESTUFA_CONTEUDO) == 13
    raras = {generate_estufa_conteudo(random.Random(s), 3, 1)["valor_ouro"] for s in range(200)}
    gaiolas = {generate_estufa_conteudo(random.Random(s), 3, 10)["valor_ouro"] for s in range(300)}
    assert raras == set(range(4, 8)) and gaiolas == set(range(4, 14))  # 1d4 + 3 e 1d10 + 3
    jarros = {generate_estufa_conteudo(random.Random(s), 3, 7)["quantidade"] for s in range(200)}
    assert jarros == {2, 3, 4, 5}  # 1d4 + 1
    assert generate_estufa_conteudo(random.Random(1), 3, 7)["criatura"]["nome"] == "Jarro Carnívoro"


def test_rolling_d12_without_a_result_gives_a_valid_entry():
    for seed in range(60):
        c = generate_estufa_conteudo(random.Random(seed), 2)
        assert 1 <= c["resultado"] <= 12 and c["texto"]


def _orquidario(resultado):
    return generator.generate_orquidario_conteudo(random.Random(resultado), 3, resultado)


def test_orchid_house_is_always_orchids_and_even_results_are_just_orchids():
    for resultado in range(1, 13):
        c = _orquidario(resultado)
        assert c["orquidario"] and 3 <= c["valor_prata"] <= 30 and c["valor_prata"] % 3 == 0  # 1d10 x profundidade
        assert any(c["texto"].startswith(base) for base in tables.ORQUIDARIO_TEXTOS)
        assert (c["texto"] in tables.ORQUIDARIO_TEXTOS) == (resultado % 2 == 0)


def test_a_cluster_of_greenhouses_is_built_from_the_dice(tmp_path):
    for seed in range(1, 6):
        campos = generator._montar_estufas(random.Random(seed), 2, seed, str(tmp_path))
        casas = campos["estufas"]
        assert 2 <= len(casas) <= 5 and campos["obj"] == casas[0]["obj"]
        for c in casas:
            p = c["planta"]
            assert p["dado"] in ESTUFA_DADOS and 1 <= p["resultado"] <= p["dado"]
            assert p["lados"] == ESTUFA_DADOS[p["dado"]]["lados"] and p["andares"] == ESTUFA_DADOS[p["dado"]]["andares"]
            assert p["lacrada"] == (c["resultado"] >= 13)
            assert p["piso_xadrez"] == (min(c["resultado"], 13) in generator.ESTUFA_PISO_XADREZ_COM)
            assert c["conteudo"]["resultado"] == c["resultado"]
            assert math.hypot(c["x"], c["z"]) + c["raio_ocupado"] <= campos["raio_ocupado"]
        for i, a in enumerate(casas):
            for b in casas[i + 1 :]:
                assert math.hypot(a["x"] - b["x"], a["z"] - b["z"]) >= a["planta"]["raio"] + b["planta"]["raio"]


def test_the_state_of_a_greenhouse_follows_the_places_detail(tmp_path):
    de_pe = generator._montar_estufas(random.Random(2), 2, 1, str(tmp_path), ruina=False)["estufas"]
    ruina = generator._montar_estufas(random.Random(2), 2, 1, str(tmp_path), ruina=True)["estufas"]
    assert all(c["planta"]["estado"] == "conservada" and c["planta"]["moldura"] != "ferrugem" for c in de_pe)
    assert all(c["planta"]["estado"] == "lastimavel" and c["planta"]["moldura"] == "ferrugem" for c in ruina)
    assert all("morto" in c["malhas"] for c in ruina) and all("morto" not in c["malhas"] for c in de_pe)


def test_what_a_greenhouse_grows_follows_what_it_holds(tmp_path):
    for seed in range(1, 6):
        c = generator._montar_estufas(random.Random(seed), 2, seed, str(tmp_path), n_dados=1)["estufas"][0]
        tema, densidade = generator.ESTUFA_FLORA_POR_RESULTADO[min(c["resultado"], 13)]
        assert c["flora_interna"]["densidade"] == densidade
        if densidade == "vazia":
            assert c["flora_interna"]["plantas"] == []
    orq = generator._montar_estufas(random.Random(3), 2, 3, str(tmp_path), n_dados=1, orquidario=True)["estufas"][0]
    assert orq["flora_interna"]["tema"] == "orquidario" and orq["flora_interna"]["densidade"] != "vazia"


def _grafo(seed=3):
    rng = random.Random(seed)
    return rng, pointcrawl.generate_pointcrawl(rng, profundidade_max=4, max_nos=14)


def test_layout_keeps_same_group_nodes_far_apart():
    for seed in range(20):
        rng, grafo = _grafo(seed)
        ids = [n["id"] for n in grafo["nos"]]
        grupos = {i: "minuscula" for i in ids[:3]}
        plots = {p["no_id"]: p for p in pointcrawl.layout_grafo(rng, grafo, grupos=grupos)}
        for a in grupos:
            for b in grupos:
                if a < b:
                    dist = math.hypot(plots[a]["x"] - plots[b]["x"], plots[a]["z"] - plots[b]["z"])
                    assert dist >= pointcrawl.DISTANCIA_MESMO_GRUPO - 0.5


def test_layout_makes_room_for_big_footprints():
    for seed in range(20):
        rng, grafo = _grafo(seed)
        raios = {grafo["nos"][1]["id"]: 14.0} if len(grafo["nos"]) > 1 else {}
        plots = pointcrawl.layout_grafo(rng, grafo, raios=raios)
        for i, p in enumerate(plots):
            for q in plots[i + 1 :]:
                r = raios.get(p["no_id"], 6.0) + raios.get(q["no_id"], 6.0)
                dist = math.hypot(p["x"] - q["x"], p["z"] - q["z"])
                if p["no_id"] in raios or q["no_id"] in raios:
                    assert dist >= r + 2.0 - 1.0


def test_flatten_circle_flattens_inside_and_keeps_far_terrain():
    terreno = {"resolucao": 17, "tamanho_celula": 2.0, "alturas": [[1.0] * 17 for _ in range(17)]}
    terrain.achatar_circulo(terreno, 0.0, 0.0, raio=6.0, margem=4.0)
    meia = 8
    for j in range(17):
        for i in range(17):
            d = math.hypot((i - meia) * 2.0, (j - meia) * 2.0)
            h = terreno["alturas"][j][i]
            if d <= 6.0:
                assert h == 0.0
            elif d >= 10.0:
                assert h == 1.0
            else:
                assert 0.0 < h < 1.0



# --- flora de dentro das estufas -------------------------------------------------

QUADRADO = [(-4.0, -3.0), (4.0, -3.0), (4.0, 3.0), (-4.0, 3.0)]


@pytest.fixture
def sem_malhas(monkeypatch):
    """Troca a geração de malha de planta por um nome de arquivo falso: os
    testes de sorteio não precisam do .obj."""
    monkeypatch.setattr(generator, "_generate_plant_mesh", lambda rng, especie, out_path=None, altura=None: (out_path, []))


def _flora(seed, **kw):
    argumentos = dict(poligonos=[QUADRADO], raio=4.0, ruina=False, out_dir=".", prefixo="t")
    argumentos.update(kw)
    return generator.sortear_flora_interna(random.Random(seed), **argumentos)


def test_flora_densities_vary_from_empty_to_jungle(sem_malhas):
    contagem = {}
    for seed in range(600):
        f = _flora(seed)
        contagem[f["densidade"]] = contagem.get(f["densidade"], 0) + 1
        if f["densidade"] == "vazia":
            assert f["plantas"] == []
    assert set(contagem) == set(generator.ESTUFA_DENSIDADES)  # de vazia a selva
    assert contagem["selva"] > 40 and contagem["vazia"] > 15


def test_ruined_greenhouses_are_sparser_and_have_dead_plants(sem_malhas):
    vivas = [_flora(s, ruina=False) for s in range(300)]
    ruinas = [_flora(s, ruina=True) for s in range(300)]
    assert all(f["mortas"] == 0.0 and not any(p["morta"] for p in f["plantas"]) for f in vivas)
    assert all(0.4 <= f["mortas"] <= 0.9 for f in ruinas)
    assert not any(f["densidade"] == "selva" for f in ruinas)
    media = lambda fs: sum(len(f["plantas"]) for f in fs) / len(fs)
    assert media(ruinas) < media(vivas)
    com_plantas = [f for f in ruinas if len(f["plantas"]) >= 8]
    assert com_plantas and any(p["morta"] for f in com_plantas for p in f["plantas"])


def test_every_greenhouse_gets_its_own_mix_of_species(sem_malhas):
    combinacoes = {tuple(sorted(_flora(s)["especies"])) for s in range(200)}
    assert len(combinacoes) >= 25  # "variam loucamente"
    f = _flora(3, tema="deserto")
    assert set(f["especies"]) <= set(generator.ESTUFA_TEMAS["deserto"]) and f["tema"] == "deserto"


def test_small_greenhouses_get_no_tall_species_and_smaller_plants(sem_malhas):
    for seed in range(120):
        f = _flora(seed, raio=1.6, poligonos=[[(-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)]], densidade="selva")
        assert not set(f["especies"]) & set(generator.ESTUFA_ESPECIES_ALTAS)
        assert all(p["escala"] <= 0.4 * 1.3 + 1e-6 for p in f["plantas"])


def test_plants_stay_inside_the_footprint_and_away_from_avoided_spots(sem_malhas):
    evitar = [(0.0, 0.0, 1.5)]
    for seed in range(40):
        f = _flora(seed, densidade="selva", evitar=evitar)
        assert f["plantas"]
        for p in f["plantas"]:
            assert abs(p["x"]) <= 4.0 - generator.ESTUFA_FLORA_MARGEM + 1e-6
            assert abs(p["z"]) <= 3.0 - generator.ESTUFA_FLORA_MARGEM + 1e-6
            assert math.hypot(p["x"], p["z"]) >= 1.5


def test_flora_count_is_capped_and_deterministic(sem_malhas):
    grande = [[(-60.0, -60.0), (60.0, -60.0), (60.0, 60.0), (-60.0, 60.0)]]
    f = _flora(1, poligonos=grande, raio=30.0, densidade="selva")
    assert len(f["plantas"]) == generator.ESTUFA_FLORA_MAX_PLANTAS
    assert _flora(7) == _flora(7)


def test_flora_does_not_disturb_the_level_random_stream_of_the_dice(sem_malhas, monkeypatch):
    def fake_mesh(rng, **kw):
        quadrado = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
        return "x.obj", {"n_alas": 0, "pegadas": [quadrado], "raio_ocupado": 2.0, "portas_angulos": [0.5], "malhas": {}}

    monkeypatch.setattr(generator, "_generate_greenhouse_mesh", fake_mesh)
    a = generator._montar_estufas(random.Random(11), 1, 1, ".", n_dados=2)
    b = generator._montar_estufas(random.Random(11), 1, 1, ".", n_dados=2)
    assert a == b
    com, sem = random.Random(11), random.Random(11)
    generator._montar_estufas(com, 1, 1, ".", n_dados=2)
    monkeypatch.setattr(generator, "sortear_flora_interna", lambda *a, **k: {"plantas": []})
    generator._montar_estufas(sem, 1, 1, ".", n_dados=2)
    assert com.random() == sem.random()  # a flora tem um rng só dela


# --- o Detalhe "Teto de Vidro" e a estufa colossal -------------------------------------------


def _nivel(seed, **kw):
    return generator.generate_nivel(random.Random(seed), profundidade_max=4, max_nos=14, **kw)


def test_glass_roofed_detail_puts_a_glass_dome_over_that_place_and_only_it(tmp_path):
    achados = 0
    for seed in range(1, 60):
        nivel = _nivel(seed, plant_output_dir=str(tmp_path))
        for plot in nivel["layout"]["plots"]:
            tem_vidro = "vidro" in plot["detalhe"]["efeitos"]
            assert ("cupula_vidro" in plot) == tem_vidro
            if tem_vidro:
                achados += 1
                c = plot["cupula_vidro"]
                assert c["raio"] >= plot.get("raio_ocupado", 6.0) and c["andares"] in (2, 3)
                assert {"moldura", "vidro"} <= set(c["malhas"])
        if achados >= 3:
            break
    assert achados >= 3


def test_never_mode_ignores_the_glass_roof_and_auto_has_no_level_wide_greenhouse(tmp_path):
    for seed in range(1, 25):
        nivel = _nivel(seed, plant_output_dir=str(tmp_path), estufa_colossal="nunca")
        assert not any("cupula_vidro" in p for p in nivel["layout"]["plots"]) and "estufa_colossal" not in nivel
        auto = _nivel(seed, plant_output_dir=str(tmp_path))
        assert "estufa_colossal" not in auto and "portas_estufa" not in auto["layout"]


def test_level_sized_greenhouse_wraps_the_whole_level_with_entry_and_exit(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
    )
    colossal = nivel["estufa_colossal"]
    raio = colossal["raio"]
    assert 55.0 <= raio <= 80.0
    entrada, saida = colossal["portas"]
    assert (entrada["tipo"], saida["tipo"]) == ("entrada", "saida")
    assert entrada["z"] == pytest.approx(-raio) and saida["z"] == pytest.approx(raio)
    plots = nivel["layout"]["plots"]
    assert all(math.hypot(p["x"], p["z"]) + p.get("raio_ocupado", 6.0) <= raio for p in plots)
    assert entrada["no_id"] == 0
    mais_fundo = max(plots, key=lambda p: (p["profundidade"], p["no_id"]))
    assert saida["no_id"] == mais_fundo["no_id"] and mais_fundo.get("saida_nivel") is True
    assert colossal["planta"]["andares"] == 3 and colossal["planta"]["lados"] == 32


def test_level_under_the_colossal_greenhouse_holds_only_glass_wings_with_one_die_each(tmp_path):
    for seed in (1, 2, 3):
        nivel = generator.generate_nivel(
            random.Random(seed), profundidade_max=3, max_nos=10, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
        )
        plots = nivel["layout"]["plots"]
        assert plots and all(p["tipo"] in ("estufa", "orquidario") for p in plots)
        assert nivel["areas"] == []
        assert all(p["ala"] in ("vidraca", "orquidario") and len(p["estufas"]) == 1 for p in plots)
        assert all("cupula_vidro" not in p for p in plots)


def test_colossal_greenhouse_is_a_tropical_garden_that_avoids_the_level_content(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
    )
    flora = nivel["estufa_colossal"]["flora_interna"]
    assert flora["tema"] == "tropical" and flora["plantas"]
    raio = nivel["estufa_colossal"]["raio"]
    for p in flora["plantas"]:
        assert math.hypot(p["x"], p["z"]) <= raio
        for plot in nivel["layout"]["plots"]:
            assert math.hypot(p["x"] - plot["x"], p["z"] - plot["z"]) >= plot.get("raio_ocupado", 6.0)


def test_places_are_whole_only_with_the_well_kept_or_ivy_details(tmp_path):
    inteiros = ruinas = 0
    for seed in range(1, 12):
        nivel = _nivel(seed, plant_output_dir=str(tmp_path))
        for plot in nivel["layout"]["plots"]:
            efeitos = plot["detalhe"]["efeitos"]
            inteiro = any(e in efeitos for e in generator.DETALHES_INTEIROS)
            assert plot["estado"] == ("intacta" if inteiro else "ruina")
            inteiros += inteiro
            ruinas += not inteiro
    assert ruinas > inteiros * 4  # a maioria jaz em ruínas, como no livro
