import os
import random

import numpy as np
import pytest

from gielis.structures import generate_gazebo, generate_tower, generate_tower_vines


def _vertex_count(path):
    with open(path) as f:
        return sum(1 for line in f if line.startswith("v "))


def test_tower_has_one_segment_per_floor(tmp_path):
    for n_floors in (3, 5, 8):
        path, skeleton = generate_tower(random.Random(1), n_floors, out_path=os.path.join(tmp_path, f"t{n_floors}.obj"))
        assert len(skeleton) == n_floors
        assert os.path.getsize(path) > 0


def _vertices(path):
    with open(path) as f:
        return np.array([[float(c) for c in line.split()[1:4]] for line in f if line.startswith("v ")])


def _todas(skeleton):
    """Vértices de todas as malhas da torre (tijolo, madeira...)."""
    return np.vstack([_vertices(p) for p in skeleton[0]["malhas"].values()])


def test_tower_is_hollow_and_wide_enough_to_enter(tmp_path):
    _, skeleton = generate_tower(random.Random(2), 5, out_path=os.path.join(tmp_path, "t.obj"))
    v = _vertices(skeleton[0]["malhas"]["tijolo"])  # .obj é Y-up: o plano horizontal é (x, z)
    madeira = _vertices(skeleton[0]["malhas"]["madeira"])
    assert (np.hypot(madeira[:, 0], madeira[:, 2]) < 1.3).any()  # escada e mastro no vão central
    radii = np.hypot(v[:, 0], v[:, 2])
    assert radii.max() >= 2.5  # ~6 m de largura: cabe um aventureiro com folga
    # Paredes só na borda: não há vértices de parede entre o poço e a parede.
    assert not ((radii > 1.9) & (radii < 2.5) & (v[:, 1] > 0.5) & (v[:, 1] < 2.0)).any()


def _faces_centroids(path):
    with open(path) as f:
        lines = f.read().splitlines()
    verts = np.array([[float(c) for c in line.split()[1:4]] for line in lines if line.startswith("v ")])
    faces = [[int(t) - 1 for t in line.split()[1:4]] for line in lines if line.startswith("f ")]
    return np.array([verts[face].mean(axis=0) for face in faces])


def test_tower_ground_floor_has_exactly_one_door_opening(tmp_path):
    path, _ = generate_tower(random.Random(3), 3, out_path=os.path.join(tmp_path, "t.obj"))
    c = _faces_centroids(path)  # .obj é Y-up: horizontal = (x, z), altura = y
    radii = np.hypot(c[:, 0], c[:, 2])
    angles = np.arctan2(c[:, 2], c[:, 0]) % (2 * np.pi)
    setor = np.floor(angles / (2 * np.pi) * 16).astype(int) % 16
    parede_baixa = (radii > 2.5) & (c[:, 1] < 1.2)  # faces de parede junto ao chão do térreo
    assert len(set(setor[parede_baixa])) == 15  # 16 setores menos o da porta


def test_tower_upper_floors_have_window_openings(tmp_path):
    path, _ = generate_tower(random.Random(4), 4, out_path=os.path.join(tmp_path, "t.obj"))
    c = _faces_centroids(path)
    radii = np.hypot(c[:, 0], c[:, 2])
    angles = np.arctan2(c[:, 2], c[:, 0]) % (2 * np.pi)
    setor = np.floor(angles / (2 * np.pi) * 16).astype(int) % 16
    # No meio do 2º andar (y ~ 3.4 + 1.65), as janelas deixam setores sem parede.
    meio = (radii > 2.5) & (c[:, 1] > 3.4 + 1.2) & (c[:, 1] < 3.4 + 2.2)
    assert len(set(setor[meio])) < 16


def test_taller_tower_has_more_vertices(tmp_path):
    short, _ = generate_tower(random.Random(1), 3, out_path=os.path.join(tmp_path, "short.obj"))
    tall, _ = generate_tower(random.Random(1), 8, out_path=os.path.join(tmp_path, "tall.obj"))
    assert _vertex_count(tall) > _vertex_count(short)


def test_gazebo_builds_and_is_deterministic(tmp_path):
    path_a, skel_a = generate_gazebo(random.Random(5), out_path=os.path.join(tmp_path, "a.obj"))
    path_b, skel_b = generate_gazebo(random.Random(5), out_path=os.path.join(tmp_path, "b.obj"))
    assert os.path.getsize(path_a) > 0
    assert len(skel_a) == len(skel_b)
    with open(path_a) as fa, open(path_b) as fb:
        assert fa.read() == fb.read()


def test_tower_skeleton_exposes_floor_radii_and_door_angle(tmp_path):
    _, skeleton = generate_tower(random.Random(5), 8, out_path=os.path.join(tmp_path, "t.obj"))
    radii = [seg["r0"] for seg in skeleton]
    assert radii == sorted(radii, reverse=True)  # afunila pra cima
    assert all(r - 1.3 >= 1.0 for r in radii)  # sobra >= 1 m de piso em anel até no último andar
    assert 0.0 <= skeleton[0]["porta_angulo"] < 2 * np.pi


def test_tower_without_roof_is_open_on_top_with_a_soil_floor(tmp_path):
    with_roof, _ = generate_tower(random.Random(6), 4, out_path=os.path.join(tmp_path, "a.obj"), roof=True)
    open_top, skeleton = generate_tower(random.Random(6), 4, out_path=os.path.join(tmp_path, "b.obj"), roof=False)
    total = skeleton[0]["altura_total"]
    _, com_telhado = generate_tower(random.Random(6), 4, out_path=os.path.join(tmp_path, "c.obj"), roof=True)
    assert _vertices(com_telhado[0]["malhas"]["telhado"])[:, 1].max() > total + 2.0  # telhado cônico
    assert "telhado" not in skeleton[0]["malhas"]
    assert total <= _todas(skeleton)[:, 1].max() <= total + 1.6  # a cornija e o parapeito (com jarros) passam do topo
    assert skeleton[0]["raio_topo"] > 2.0
    piso_de_terra = np.isclose(_vertices(skeleton[0]["malhas"]["terra"])[:, 1], total - 0.08)
    assert piso_de_terra.sum() > 10


def test_tower_vines_hug_the_outer_wall_and_climb(tmp_path):
    _, skeleton = generate_tower(random.Random(7), 5, out_path=os.path.join(tmp_path, "t.obj"))
    path, hastes = generate_tower_vines(random.Random(8), skeleton, out_path=os.path.join(tmp_path, "v.obj"))
    v = _vertices(path)  # .obj é Y-up
    zs = [float(seg["start"][2]) for seg in skeleton] + [float(skeleton[-1]["end"][2])]
    rs = [float(seg["r0"]) for seg in skeleton] + [float(skeleton[-1]["r1"])]
    raio_parede = np.interp(v[:, 1], zs, rs)
    raio = np.hypot(v[:, 0], v[:, 2])
    assert (raio >= raio_parede - 0.05).all()  # nunca atravessa a parede pra dentro
    assert (raio <= raio_parede + 1.0).all()  # rente à parede
    assert v[:, 1].max() > 0.3 * zs[-1]  # sobe de verdade
    assert 3 <= len(hastes) <= 6


def test_tower_vines_are_deterministic(tmp_path):
    _, skeleton = generate_tower(random.Random(7), 4, out_path=os.path.join(tmp_path, "t.obj"))
    a, _ = generate_tower_vines(random.Random(9), skeleton, out_path=os.path.join(tmp_path, "a.obj"))
    b, _ = generate_tower_vines(random.Random(9), skeleton, out_path=os.path.join(tmp_path, "b.obj"))
    with open(a) as fa, open(b) as fb:
        assert fa.read() == fb.read()


# --- a torre do livro: porta entreaberta, venezianas, poças, tapete mofado ------------


def test_tower_is_split_into_materials_with_walls_in_the_main_file(tmp_path):
    path, skeleton = generate_tower(random.Random(1), 5, out_path=os.path.join(tmp_path, "t.obj"))
    malhas = skeleton[0]["malhas"]
    assert malhas["tijolo"] == path
    assert {"tijolo", "madeira", "telhado", "tapete", "agua", "papel"} <= set(malhas)
    assert all(os.path.getsize(p) > 0 for p in malhas.values())


def test_every_upper_floor_has_shuttered_windows_with_a_state(tmp_path):
    for n_floors in (3, 5, 8):
        _, skeleton = generate_tower(random.Random(n_floors), n_floors, out_path=os.path.join(tmp_path, "t.obj"))
        janelas = skeleton[0]["janelas"]
        assert {j["andar"] for j in janelas} == set(range(2, n_floors + 1))  # todo andar acima do térreo
        assert len([j for j in janelas if j["andar"] == 2]) == 4
        assert {j["estado"] for j in janelas} <= {"fechada", "entreaberta"}
    estados = [j["estado"] for s in range(20) for j in generate_tower(random.Random(s), 4, out_path=os.path.join(tmp_path, "x.obj"))[1][0]["janelas"]]
    assert 0.35 < estados.count("entreaberta") / len(estados) < 0.65  # ~metade entreaberta


def test_shutters_swing_out_when_ajar_and_stay_in_the_wall_when_closed(tmp_path):
    _, skeleton = generate_tower(random.Random(4), 4, out_path=os.path.join(tmp_path, "t.obj"))
    madeira = _vertices(skeleton[0]["malhas"]["madeira"])
    raio_parede = np.hypot(madeira[:, 0], madeira[:, 2])
    # folhas entreabertas passam da parede (raio maior que a torre); nenhuma entra além do raio externo + ~1,6 m
    assert raio_parede.max() > skeleton[0]["r0"] + 0.4 or all(j["estado"] == "fechada" for j in skeleton[0]["janelas"])
    assert raio_parede.max() < skeleton[0]["r0"] + 3.0


def test_ground_door_is_ajar_outside_the_doorway(tmp_path):
    _, skeleton = generate_tower(random.Random(3), 3, out_path=os.path.join(tmp_path, "t.obj"))
    madeira = _vertices(skeleton[0]["malhas"]["madeira"])
    porta = skeleton[0]["porta_angulo"]
    # o .obj é Y-up: ângulo no plano (x, z) é o oposto do de construção
    no_setor = [v for v in madeira if v[1] < 2.3 and abs(np.cos(np.arctan2(-v[2], v[0]) - porta)) > 0.8 and np.hypot(v[0], v[2]) > skeleton[0]["r0"] * 0.95]
    assert no_setor  # a folha da porta está do lado de fora da parede, diante do vão


def test_puddles_and_peeling_wallpaper_and_mouldy_carpet_are_inside(tmp_path):
    _, skeleton = generate_tower(random.Random(5), 5, out_path=os.path.join(tmp_path, "t.obj"))
    raio_externo = skeleton[0]["r0"]
    for grupo in ("agua", "tapete", "papel"):
        v = _vertices(skeleton[0]["malhas"][grupo])
        assert np.hypot(v[:, 0], v[:, 2]).max() <= raio_externo + 0.01  # tudo por dentro das paredes
    agua = _vertices(skeleton[0]["malhas"]["agua"])
    assert agua[:, 1].max() < 17 and len(agua) >= 4 * 13  # uma poça (13 vértices) por janela, 4 andares de janela
    tapete = _vertices(skeleton[0]["malhas"]["tapete"])
    assert len(set(np.round(tapete[:, 1], 2))) >= 5  # um por andar


def test_tower_is_deterministic_across_all_materials(tmp_path):
    _, a = generate_tower(random.Random(8), 4, out_path=os.path.join(tmp_path, "a.obj"))
    _, b = generate_tower(random.Random(8), 4, out_path=os.path.join(tmp_path, "b.obj"))
    for grupo in a[0]["malhas"]:
        assert open(a[0]["malhas"][grupo]).read() == open(b[0]["malhas"][grupo]).read()
