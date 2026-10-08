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

## Modo livro: o mapa de pontos (padrão)

`python -m ynn.cli --seed 42` (ou `--modo livro`) produz um nível como o
livro descreve: um **mapa de pontos** (point-crawl) montado do zero a cada
visita, em [`ynn/pointcrawl.py`](ynn/pointcrawl.py).

- A **entrada** é a camada 0. A cada passo "mais fundo" o mapa ganha um
  novo local na camada seguinte, ligado ao anterior, e cada local pode se
  ramificar (`--profundidade`, padrão 4 camadas; `--max-nos`, padrão 14).
- Cada local é um sorteio de **`d20 + profundidade`** em duas tabelas
  originais: o **Local** (`tables.LOCAIS`, o núcleo: uma pérgula, uma
  torre, uma estufa, um gazebo...) e o **Detalhe** (`tables.DETALHES`, o
  modificador). Passou do fim da tabela, cai na última entrada. Por isso o
  fundo do mapa é mais estranho que a entrada.
- Eventos do livro que ligam lugares distantes viram arestas extras: o
  **atalho** (para um local já explorado, mais raso) e a **descida** (para
  um local bem mais fundo).
- O **Detalhe** tem efeito mecânico: `vazio` (sem habitantes), `tesouro`
  (achado extra), `saida` (uma porta de volta ao mundo real) e `duplo`
  ("emaranhado": dois detalhes ao mesmo tempo). E dita o **relevo**: o
  terreno varia só ao redor dos locais cujo detalhe pede
  (`terrain.generate_terrain_localizado`), e o chão fica plano no resto.
- A **profundidade** do nó (+1) faz o papel do número da camada: escolhe a
  banda de conteúdo (jardim externo, profundo, núcleo selvagem).
- O mapa é posicionado no campo como o desenho em papel do livro: entrada
  no topo, cada camada numa fileira mais abaixo (`layout_grafo`).

O modo antigo (`--modo grade`, `--layer`/`--areas`) continua disponível.

## Layout 2D em grade (`--modo grade`; escala de campo de futebol)

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
  igual às áreas). A malha é um **prédio oco onde os aventureiros
  entram**: paredes de ~6 m de largura (como os andares do livro), porta
  no térreo, janelas nos andares de cima, piso em cada andar (em anel, com
  um vão no centro) e uma escada em espiral em volta de um mastro central.
  Recebe o mesmo `n_andares` do conteúdo e ganha "hera" — algumas variantes
  de `videira` (`hera_obj`) em coroa ao redor da base.
  **O conteúdo de cada andar fica visível dentro da torre**: cada entrada
  de `TORRE_ANDARES`/`TORRE_TOPO` traz um `prop` (o objeto no piso: baú,
  estante, móveis, ninhos, teias, esqueleto, retratos, espelho; e no topo
  sino, telescópio, câmera escura, biblioteca, armadilha, armadura,
  máquina voadora, caixão, lâmpada viva...) e um `rotulo`. `plot.geometria`
  leva as medidas *dessa* torre (altura do andar, raio do vão da escada,
  raio de cada piso, ângulo da porta) pro Godot encaixar os objetos no
  piso em anel sem bloquear a entrada. Como cada torre sorteia seu número
  de andares (3 a 8, o `d6+2` do livro) e o conteúdo de cada um, duas
  torres nunca são iguais.
  Outros efeitos, sorteados por torre (`sortear_extras_torre`): **nem toda
  torre tem trepadeiras** (60%: hastes de folhas subindo pela parede em
  manchas, `trepadeiras_obj`, via `gielis.structures.generate_tower_vines`);
  **40% perdem o telhado** e algo brota lá em cima (`TORRE_BROTO`: árvore,
  mato, flores, samambaias, cogumelos; `topo_obj` e `conteudo.topo_brotado`),
  com a malha destelhada (piso de terra e cornija no topo); e **uma em cada
  dez fica inclinada** (`inclinacao`: 4 a 12 graus, azimute sorteado).
- **estufa**: de ferro pintado e vidro, com soco de pedra e portas em arco
  (módulo `gielis.greenhouse`; uma malha `.obj` por material em
  `plot.malhas`: moldura, vidro, soco, piso xadrez, trepadeiras mortas).
  Tem **porte** (`generate_estufa_planta`): minúscula (20%, raio ~1,5 m,
  sem porta), normal (60%) ou imensa (20%, várias alas). Telhado de domo
  (planta poligonal, até 3 pavimentos com galeria e, às vezes, tambor e
  pináculo), de abóbada ou de duas águas. As alas seguem um padrão:
  *palácio* (2), *cruz* (4) ou *muitas alas* (alas saindo de alas); nunca
  mais de 3 andares. **4 em 10 estão em estado lastimável** (vidros
  faltando, ferrugem, trepadeiras mortas) e **3 em 10 têm o piso em xadrez
  preto-e-branco**. Cada estufa sorteia um conteúdo em `ESTUFA_CONTEUDO`
  (`generate_estufa_conteudo`, em `plot.conteudo`): plantas raras ou gaiolas
  de ouro, ervas, frutos, flores venenosas, esporos, limo no teto, ou uma
  criatura — `Jarro Carnívoro` e `Esqueleto Vegetal` (`ynn/creatures.py`),
  só do jardim profundo em diante, assim como a estufa lacrada.
  **A flora de dentro varia loucamente** (`sortear_flora_interna`, em
  `plot.flora_interna`): cada estufa sorteia um tema (`deserto`, `tropical`,
  `formal`, `sombra` ou `misto`) e de 2 a 5 espécies dele, e uma densidade de
  `vazia` a `selva` (plantas por m²); as pequenas não recebem espécies altas e
  as em ruína têm menos plantas, 40–90% delas mortas. As espécies novas, em
  `gielis.plants`, são cacto-coluna, cacto-barril, agave, palmeira,
  folha-larga, cipreste e topiaria. A colossal vira um jardim tropical
  (plantas maiores, desviando dos locais do nível). O sorteio usa um `rng`
  próprio, então não muda o resto do nível.
  Duas estufas minúsculas nunca ficam coladas (`DISTANCIA_MESMO_GRUPO`), e
  **1 minúscula em 10** fica no meio de um **espelho d'água**
  (`plot.espelho_dagua`: raio e `caminho_angulo`; o relevo é aplainado sob
  a água e há uma calçada até a porta). A **estufa colossal** é a mais rara
  de todas (1 em 30 por estufa, `--estufa-colossal auto|sempre|nunca`): o
  vidro dela cobre o nível inteiro (`estufa_colossal`, raio 55–64 m, 32
  lados, 3 andares); entra-se por um portal num lado (`layout.portas_estufa`,
  tipo `entrada`, junto ao nó 0) e só se sai pelo portal do lado oposto
  (tipo `saida`, junto ao local mais fundo).
- **gazebo**: pavilhão aberto (plataforma, 6 ou 8 postes, grade baixa com
  uma abertura de entrada, telhado em cúpula e pináculo). Em
  `plot.conteudo`: estado do pavilhão (`GAZEBO_ESTADO`), um bibelô largado
  (`GAZEBO_BIBELOS`), um tesouro (`TREASURE`) e a regra de abrigo noturno
  (`REFUGIO_GAZEBO`: com uma chama acesa lá dentro, as criaturas não
  atacam).
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
