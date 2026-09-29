# ynn-generator

Gerador procedural de camadas de jardim para RPG, por tabelas de texto —
estrutura inspirada em *The Gardens of Ynn* (Emmy Verte): um "location
crawl" dividido em camadas que ficam mais estranhas e perigosas conforme se
avança. As tabelas e o texto aqui são inteiramente originais; nenhum
conteúdo do livro é reproduzido.

## Ligação com gielis-equations (plantas em malha 3D)

Um punhado de entradas em `VEGETATION` (`ynn/tables.py`) têm uma espécie
de [`gielis.plants`](../gielis-equations/gielis/plants) associada
(`arvore`, `arbusto`, `espinheiro`, `bambu`, `videira`, `flor`, `cogumelo`
ou `samambaia`). Quando uma dessas é sorteada, o gerador chama
`gielis.plants.generate_plant` de 3 a 6 vezes (`PLANT_VARIANT_RANGE` em
`ynn/generator.py`) — mesma espécie, formas diferentes a cada chamada —
e salva cada malha em `output/plantas/camada{N}_area{i}_{especie}_{n}.obj`;
os caminhos aparecem em `plantas_obj`, junto do texto da área. Um jardim
não teria uma única planta solitária por canteiro. Vegetação de cobertura
(gramado, musgo, líquens) não tem espécie e continua só texto, sem malha.
Veja `camada2_com_plantas_exemplo.md` para um exemplo (nota: gerado antes
dessa mudança, ainda mostra uma malha só por área).

Cerca de 1 em 6 áreas (`FALLEN_BRANCH_CHANCE` em `ynn/generator.py`) também
ganha de 1 a 3 galhos/troncos caídos ou cortados, via
`gielis.plants.generate_fallen_branch` — um detrito de jardim sem cuidado,
não uma espécie viva; os caminhos aparecem em `galhos_caidos_obj`.

## Layout 2D (escala de campo de futebol)

[`ynn/layout.py`](ynn/layout.py) substitui a antiga linha reta de áreas por
um layout espacial de verdade: um campo do tamanho de um campo de futebol
(padrão FIFA, 105m x 68m — `--field-width`/`--field-depth`), dividido numa
grade de lotes de `--plot-size` metros (padrão 12m). Cada área, e cada
estrutura, ocupa um lote sorteado sem repetição (mais um leve jitter).

Três tipos de lote não-narrativos, populados por
`ynn.generator.generate_layout_camada` com malhas de
[`gielis.structures`](../gielis-equations/gielis/structures.py) (reaproveita
o tubo de seção de Lamé e o domo da Superfórmula de `gielis.plants`):

- **torre**: uma mini-masmorra vertical, não só decoração — `--layer`
  decide a banda, `generate_torre_conteudo` sorteia de 3 a 8 andares
  (`N_ANDARES_TORRE_RANGE`), cada um com conteúdo original de
  `tables.TORRE_ANDARES` (o último de `tables.TORRE_TOPO`, mais raro),
  podendo incluir um tesouro (`TREASURE`) ou um encontro (`DENIZENS`,
  igual às áreas). A malha (fuste segmentado, um afunilamento por andar,
  telhado cônico) recebe o mesmo `n_andares`, e ganha "hera" — algumas
  variantes de `videira` (`hera_obj`) pra cobrir a base.
- **estufa**: esqueleto de quatro postes + cumeeira + águas do telhado (sem
  vidro/painéis ainda).
- **canteiro**: um leito denso de uma única espécie (`flor` ou `arbusto`,
  `CANTEIRO_SPECIES`), como as plantas por área mas mais compacto.

A torre reaproveita o sistema de denizens/tesouro das áreas por
simplicidade — o texto de alguns encontros ainda soa como jardim aberto
("um banco de pedra", "um gramado") mesmo dentro da torre; ainda não há
uma tabela de denizens exclusiva pra interiores.

O JSON exportado ganha uma chave `layout` (`field_width`, `field_depth`,
`plot_size`, `plots`); cada lote de área só carrega a posição — o conteúdo
continua vindo de `generate_area`, cruzado pelo `area_index`.

## Ligação com lotfp-rules

Um punhado de entradas em `DENIZENS` (`ynn/tables.py`) são humanoides e
têm uma classe de LotFP associada (`fighter`, `specialist`, `magic_user`
ou `cleric`). Quando uma dessas é sorteada, o gerador chama
[`lotfp-rules`](../lotfp-rules) (`lotfp.character.create_character`) e
anexa uma ficha de nível 1 completa logo abaixo da área no Markdown
gerado — veja `camada3_com_npc_exemplo.md` para um exemplo.

Ambas as ligações (esta e a de plantas) dependem de `lotfp-rules` e
`gielis-equations` estarem nas pastas irmãs (`../lotfp-rules`,
`../gielis-equations`); `ynn/generator.py` ajusta o `sys.path`
automaticamente para achá-las.

## Criaturas de Ynn (bestiário próprio)

Os demais denizens não-humanoides (animais, objetos animados, fenômenos)
podem ter uma ficha de monstro em [`ynn/creatures.py`](ynn/creatures.py)
— um bestiário **original** (CA, Dados de Vida, ataques, Moral, uma
habilidade especial), não uma transcrição de nenhum bestiário
específico. Quando sorteado, `ynn.creatures.instantiate_creature` rola os
pontos de vida e a ficha aparece junto da área — nunca ao mesmo tempo que
um NPC humanoide. Um punhado (a criança que não é encontrada, a voz sem
corpo, o som de tesoura sem origem) não tem ficha nenhuma — são
deliberadamente só atmosfera. Veja `camada5_com_criaturas_exemplo.md`
para um exemplo.

## Relevo (descritor de localidade)

Cada camada sorteia, uma única vez, um "descritor de localidade" em
[`ynn/tables.py`](ynn/tables.py) (`LOCALIDADE`) — texto original que também
carrega um `tipo_relevo` (`plano`, `leve`, `acentuado` ou `irregular`).
[`ynn/terrain.py`](ynn/terrain.py) usa esse tipo pra gerar uma grade
quadrada de pontos com altura (heightmap): `plano` fica toda em zero, os
demais usam o algoritmo diamond-square (determinístico a partir do `rng`,
sem depender de numpy) com amplitude crescente. O resultado (`terreno` no
JSON, com `descricao`, `tipo_relevo`, `resolucao`, `tamanho_celula` e
`alturas`) é consumido pelo `jardynn-game` para montar a malha 3D do chão
e apoiar as plantas na altura certa — veja `--terrain-resolution` e
`--terrain-cell-size` em `python -m ynn.cli --help`.

## Camadas

- **Camadas 1-2 — Jardim Externo**: ainda reconhecível, mas já fora do
  comum.
- **Camadas 3-4 — Jardim Profundo**: a vegetação e a arquitetura ficam mais
  hostis e menos naturais.
- **Camada 5+ — Núcleo Selvagem**: efeitos de corrupção mágica ("Wyrd")
  ficam frequentes e intensos.

Cada área gerada combina: vegetação de base, um elemento notável
(arquitetônico ou natural), opcionalmente um encontro, um efeito de Wyrd e/ou
um achado — com chances que mudam por camada (ver `ynn/generator.py`).

## Uso

```bash
python -m ynn.cli --layer 1 --areas 5 --seed 42
python -m ynn.cli --layer 5 --areas 3 --output camada5.md
```

## Testes

```bash
pytest tests/
```
