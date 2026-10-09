# jardynn

Um gerador procedural de jardins sobrenaturais para RPG de mesa, inspirado na
estrutura de geração por tabelas de *The Gardens of Ynn*, com um visualizador em
Godot 4.7. Os níveis saem de **tabelas** (o Local e o Detalhe de cada lugar, rolados
em `d20 + profundidade`), as **estruturas** (torres, estufas, labirintos, mausoléus...)
saem de geradores de malha 3D, e as **plantas** saem de equações de Johan Gielis e de
gramáticas L-system.

> Todo o texto das tabelas é original; só a mecânica e a estrutura das tabelas seguem
> o livro. Nenhum texto de livro de regras é reproduzido neste repositório.

## O que tem em cada pasta

| Pasta | O que é |
|---|---|
| [`gielis-equations/`](gielis-equations/README.md) | Biblioteca Python: as equações de *The Geometrical Beauty of Plants* (Superfórmula, curvas de Lamé...) e, em cima delas, os geradores de **malha 3D** — plantas (`gielis.plants`), estufas (`greenhouse`), torre e gazebo (`structures`), estruturas pitorescas (`pitoresco`) e ferragens e parapeitos (`ferragens`). |
| [`ynn-generator/`](ynn-generator/README.md) | O gerador de níveis: o mapa de pontos, as tabelas, o layout, o relevo e a montagem de cada lote. Produz o JSON e os `.obj` que o Godot lê. |
| [`lotfp-rules/`](lotfp-rules/README.md) | Mecânica de personagem de nível 1 de *Lamentations of the Flame Princess* (usada nas fichas de NPCs). Valores conferidos em [`NOTES.md`](lotfp-rules/NOTES.md). |
| [`ose-rules/`](ose-rules/README.md) | A mesma ideia para *Old-School Essentials*. |
| [`jardynn-game/`](jardynn-game/README.md) | O projeto Godot que carrega o JSON e mostra o nível em 3D. |

(`jardynn-game-(4.3)/` é uma cópia de segurança do projeto Godot de uma versão anterior;
`codicea-livros-pela-rede/` e as pastas `_preview_test*` são material à parte, fora do
pipeline.)

O fluxo de dados e o formato do JSON estão em
[`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

## Como rodar

Requisitos: Python 3.10+ com `numpy` (e `pytest` para os testes), e Godot 4.7.

```bash
# 1. gera um nível (JSON + malhas .obj) direto na pasta do projeto Godot
cd ynn-generator
python -m ynn.cli --seed 17 --json \
    --output ../jardynn-game/assets/data/camada1.json \
    --plant-output-dir ../jardynn-game/assets/plants

# 2. reimporta os .obj no Godot (headless) ou abra o projeto no editor
"<caminho>/Godot_v4.7.2-stable_win64_console.exe" --headless --path ../jardynn-game --import
```

Depois é só abrir `jardynn-game` no Godot e rodar a cena `Main` — o texto de cada local
(Detalhe, estado, fichas, conteúdo das estufas e dos andares das torres) sai no console.
A câmera é livre (veja `scripts/FreeLookCamera.gd`).

Sem `--json`, o mesmo comando imprime o nível em Markdown. Opções úteis:

| Opção | Efeito |
|---|---|
| `--seed N` | reprodutível: a mesma semente dá o mesmo nível |
| `--profundidade N`, `--max-nos N` | tamanho do mapa de pontos (padrão 4 e 14) |
| `--estufa-colossal sempre` | o vidro de uma estufa gigante sobre o nível todo, com portal de entrada e de saída |
| `--modo grade` | o layout antigo, de uma camada só |

## Testes

```bash
cd gielis-equations && python -m pytest -q   # equações, plantas, estufas, estruturas
cd ynn-generator    && python -m pytest -q   # tabelas, mapa de pontos, níveis
cd lotfp-rules      && python -m pytest -q
cd ose-rules        && python -m pytest -q
```

Nos testes do gerador de níveis as plantas viram um `.obj` mínimo (`tests/conftest.py`),
porque a geração das malhas já é testada em `gielis-equations`; use
`@pytest.mark.malha_real` para um teste que precise da malha de verdade.

## Convenções

- Código, comentários e docstrings em português.
- Coordenadas de construção: **Z pra cima**; ao escrever o `.obj`, vira **Y pra cima**
  (a convenção do Godot): `(x, y, z) -> (x, z, -y)`.
- Cada estrutura sai em **um `.obj` por material** (moldura, vidro, tijolo, madeira...), que
  o Godot pinta com cores fixas; flores e plantas coloridas trazem **cor de vértice** no
  próprio `.obj`.
- O Godot só importa a malha depois de um `--import`; os `.obj` novos precisam ser
  reimportados.
