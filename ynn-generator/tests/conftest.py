"""Fixtures compartilhadas dos testes do gerador de níveis.

Gerar a malha de cada planta (centenas por nível, entre flora de estufa, áreas e
canteiros) é o que mais demora; a geração das malhas em si já é testada em
`gielis-equations`. Aqui as plantas viram um arquivo .obj mínimo (existe e não
está vazio), o que deixa os testes de nível dezenas de vezes mais rápidos. Quem
precisa da malha de verdade usa a marca `@pytest.mark.malha_real`."""

import os

import pytest

from ynn import generator

OBJ_MINIMO = "o mesh\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"


def _planta_leve(rng, especie, out_path=None, altura=None, **kw):
    if out_path is None:
        out_path = os.path.join(generator.PLANT_OUTPUT_DIR, f"{especie}.obj")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(OBJ_MINIMO)
    return out_path, []


def _galho_leve(rng, out_path=None):
    return _planta_leve(rng, "galho_caido", out_path)


def pytest_configure(config):
    config.addinivalue_line("markers", "malha_real: usa a geração de malha de plantas de verdade (lenta)")


@pytest.fixture(autouse=True)
def plantas_leves(request, monkeypatch):
    if request.node.get_closest_marker("malha_real"):
        return
    monkeypatch.setattr(generator, "_generate_plant_mesh", _planta_leve)
    monkeypatch.setattr(generator, "_generate_fallen_branch_mesh", _galho_leve)
