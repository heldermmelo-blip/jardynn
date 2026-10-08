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
    assert 55.0 <= raio <= 64.0
    entrada, saida = colossal["portas"]
    assert (entrada["tipo"], saida["tipo"]) == ("entrada", "saida")
    assert entrada["z"] == pytest.approx(-raio) and saida["z"] == pytest.approx(raio)  # lados opostos
    plots = nivel["layout"]["plots"]
    assert all(math.hypot(p["x"], p["z"]) + 6.0 <= raio for p in plots)  # o nível inteiro cabe sob o vidro
    assert entrada["no_id"] == 0
    mais_fundo = max(plots, key=lambda p: (p["profundidade"], p["no_id"]))
    assert saida["no_id"] == mais_fundo["no_id"] and mais_fundo.get("saida_nivel") is True
    assert any(p.get("colossal") for p in plots)
    assert colossal["planta"]["andares"] == 3 and colossal["planta"]["lados"] == 32


def test_never_mode_has_no_level_sized_greenhouse(tmp_path):
    nivel = generator.generate_nivel(
        random.Random(5), profundidade_max=2, max_nos=6, plant_output_dir=str(tmp_path), estufa_colossal="nunca"
    )
    assert "estufa_colossal" not in nivel and "portas_estufa" not in nivel["layout"]
    assert not any(p.get("colossal") for p in nivel["layout"]["plots"])
