import math
import random

import pytest

from ynn import generator, pointcrawl, terrain
from ynn.generator import (
    ESTUFA_COLOSSAL_CHANCE,
    ESTUFA_ESPELHO_CHANCE,
    ESTUFA_MAX_ANDARES,
    ESTUFA_MOLDURAS,
    ESTUFA_RUINA_CHANCE,
    ESTUFA_XADREZ_CHANCE,
    generate_estufa_planta,
)


def test_portes_follow_their_weights_and_limits():
    n = 4000
    contagem = {"minuscula": 0, "normal": 0, "imensa": 0}
    for seed in range(n):
        p = generate_estufa_planta(random.Random(seed))
        contagem[p["porte"]] += 1
        assert 1 <= p["andares"] <= ESTUFA_MAX_ANDARES  # nunca mais de 3 pavimentos
        assert p["moldura"] in ESTUFA_MOLDURAS + ("ferrugem",)
        if p["moldura"] == "ferrugem":
            assert p["estado"] == "lastimavel"
        if p["porte"] == "minuscula":
            assert 1.2 <= p["raio"] <= 1.9 and p["andares"] == 1 and p["alas"] == 0
        elif p["porte"] == "imensa":
            assert p["alas"] >= 2 and p["andares"] >= 2
            assert p["padrao"] in ("palacio", "cruz", "livre")
            if p["padrao"] == "palacio":
                assert 2 <= p["alas"] <= 5
            if p["padrao"] == "cruz":
                assert 4 <= p["alas"] <= 8
        else:
            assert p["alas"] <= 3
            if p["padrao"] == "palacio":
                assert p["alas"] == 2 and p["andares"] >= 2
    assert abs(contagem["minuscula"] / n - 0.2) < 0.04
    assert abs(contagem["normal"] / n - 0.6) < 0.04
    assert abs(contagem["imensa"] / n - 0.2) < 0.04


def test_immense_ones_are_much_bigger_than_tiny_ones():
    tinys = [generate_estufa_planta(random.Random(s), porte="minuscula")["raio"] for s in range(50)]
    imensas = [generate_estufa_planta(random.Random(s), porte="imensa")["raio"] for s in range(50)]
    assert max(tinys) < min(imensas)


def test_ruin_and_checker_floor_follow_their_chances():
    n = 5000
    ruinas = xadrez = 0
    for seed in range(n):
        p = generate_estufa_planta(random.Random(seed))
        ruinas += p["estado"] == "lastimavel"
        xadrez += p["piso_xadrez"]
    assert abs(ruinas / n - ESTUFA_RUINA_CHANCE) < 0.03  # 4 em 10
    assert abs(xadrez / n - ESTUFA_XADREZ_CHANCE) < 0.03


def test_colossal_is_the_rarest_one_in_thirty():
    assert ESTUFA_COLOSSAL_CHANCE == pytest.approx(1 / 30)
    n = 20000
    saiu = sum(generator._sorteou_colossal(random.Random(s), "auto") for s in range(n))
    assert abs(saiu / n - 1 / 30) < 0.006
    assert all(generator._sorteou_colossal(random.Random(s), "sempre") for s in range(20))
    assert not any(generator._sorteou_colossal(random.Random(s), "nunca") for s in range(20))
    # mais rara que qualquer outra característica das estufas
    assert ESTUFA_COLOSSAL_CHANCE < ESTUFA_ESPELHO_CHANCE < min(ESTUFA_XADREZ_CHANCE, ESTUFA_RUINA_CHANCE)


def test_water_mirror_happens_one_in_ten_and_only_for_the_tiny(monkeypatch):
    def fake_mesh(rng, **kw):
        quadrado = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
        return "x.obj", {"n_alas": 0, "pegadas": [quadrado], "raio_ocupado": 2.0, "portas_angulos": [0.5], "malhas": {}}

    monkeypatch.setattr(generator, "_generate_greenhouse_mesh", fake_mesh)
    monkeypatch.setattr(generator, "sortear_flora_interna", lambda *a, **k: {})  # sem gerar malhas nas 4000 estufas
    pequenas = com_espelho = 0
    for seed in range(4000):
        campos = generator._montar_estufa(random.Random(seed), 1, 1, ".")
        if campos["planta"]["porte"] == "minuscula":
            pequenas += 1
            if "espelho_dagua" in campos:
                com_espelho += 1
                assert 2.2 <= campos["planta"]["raio"] <= 2.5  # ainda a menor classe, mas com porta
                assert 5.5 <= campos["espelho_dagua"]["raio"] <= 8.0
                assert campos["raio_ocupado"] >= campos["espelho_dagua"]["raio"] + 1.0
        else:
            assert "espelho_dagua" not in campos
    assert pequenas > 500
    assert abs(com_espelho / pequenas - ESTUFA_ESPELHO_CHANCE) < 0.03


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


def test_level_sized_greenhouse_wraps_the_whole_level_with_entry_and_exit(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
    )
    colossal = nivel["estufa_colossal"]
    raio = colossal["raio"]
    assert 55.0 <= raio <= 80.0
    entrada, saida = colossal["portas"]
    assert (entrada["tipo"], saida["tipo"]) == ("entrada", "saida")
    assert entrada["z"] == pytest.approx(-raio) and saida["z"] == pytest.approx(raio)  # lados opostos
    plots = nivel["layout"]["plots"]
    assert all(math.hypot(p["x"], p["z"]) + p.get("raio_ocupado", 6.0) <= raio for p in plots)  # o nível inteiro cabe sob o vidro
    assert entrada["no_id"] == 0
    mais_fundo = max(plots, key=lambda p: (p["profundidade"], p["no_id"]))
    assert saida["no_id"] == mais_fundo["no_id"] and mais_fundo.get("saida_nivel") is True
    assert colossal["planta"]["andares"] == 3 and colossal["planta"]["lados"] == 32


def test_level_under_the_colossal_greenhouse_holds_only_glass_wings(tmp_path):
    for seed in (1, 2, 3):
        nivel = generator.generate_nivel(
            random.Random(seed), profundidade_max=3, max_nos=10, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
        )
        plots = nivel["layout"]["plots"]
        assert plots and all(p["tipo"] == "estufa" for p in plots)  # nada de torre, gazebo, canteiro ou área aberta
        assert nivel["areas"] == []
        assert all(p["ala"] in ("vidraca", "orquidario") and p["planta"]["porte"] in ("minuscula", "normal") for p in plots)
        assert all("espelho_dagua" not in p and "conteudo" in p and "flora_interna" in p for p in plots)
        for p in plots:
            if p["ala"] == "orquidario":
                assert p["conteudo"]["orquidario"] and p["conteudo"]["valor_prata"] >= 1


def test_orchid_house_is_always_orchids_and_sometimes_something_else():
    n = 400
    so_orquideas = 0
    for seed in range(n):
        c = generator.generate_orquidario_conteudo(random.Random(seed), 3)
        assert 3 <= c["valor_prata"] <= 30 and c["valor_prata"] % 3 == 0  # 1d10 x profundidade
        assert any(c["texto"].startswith(base) for base in generator.tables.ORQUIDARIO_TEXTOS)
        so_orquideas += c["texto"] in generator.tables.ORQUIDARIO_TEXTOS
    assert abs(so_orquideas / n - 0.5) < 0.1


def test_never_mode_has_no_level_sized_greenhouse(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="nunca"
    )
    assert "estufa_colossal" not in nivel and "portas_estufa" not in nivel["layout"]
    assert not any("ala" in p for p in nivel["layout"]["plots"])


# --- flora de dentro das estufas -------------------------------------------------

QUADRADO = [(-4.0, -3.0), (4.0, -3.0), (4.0, 3.0), (-4.0, 3.0)]


@pytest.fixture
def sem_malhas(monkeypatch):
    """Troca a geração de malha de planta por um nome de arquivo falso: os
    testes de sorteio não precisam do .obj."""
    monkeypatch.setattr(generator, "_generate_plant_mesh", lambda rng, especie, out_path=None: (out_path, []))


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


def test_flora_does_not_disturb_the_level_random_stream(sem_malhas, monkeypatch):
    def fake_mesh(rng, **kw):
        return "x.obj", {"n_alas": 0, "pegadas": [QUADRADO], "raio_ocupado": 4.0, "portas_angulos": [0.5], "malhas": {}}

    monkeypatch.setattr(generator, "_generate_greenhouse_mesh", fake_mesh)
    com, sem = random.Random(11), random.Random(11)
    generator._montar_estufa(com, 1, 1, ".")
    monkeypatch.setattr(generator, "sortear_flora_interna", lambda *a, **k: {})
    generator._montar_estufa(sem, 1, 1, ".")
    assert com.random() == sem.random()


def test_colossal_greenhouse_is_a_tropical_garden_that_avoids_the_level_content(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="sempre"
    )
    flora = nivel["estufa_colossal"]["flora_interna"]
    assert flora["tema"] == "tropical" and flora["plantas"]
    assert set(flora["especies"]) <= set(generator.ESTUFA_TEMAS["tropical"])
    raio = nivel["estufa_colossal"]["raio"]
    for p in flora["plantas"]:
        assert math.hypot(p["x"], p["z"]) <= raio
        for plot in nivel["layout"]["plots"]:
            assert math.hypot(p["x"] - plot["x"], p["z"] - plot["z"]) >= plot.get("raio_ocupado", 6.0)
    for plot in nivel["layout"]["plots"]:
        assert "flora_interna" in plot
