# ynn-generator

Gerador procedural de camadas de jardim para RPG, por tabelas de texto —
estrutura inspirada em *The Gardens of Ynn* (Emmy Verte): um "location
crawl" dividido em camadas que ficam mais estranhas e perigosas conforme se
avança. As tabelas e o texto aqui são inteiramente originais; nenhum
conteúdo do livro é reproduzido.

## Ligação com gielis-equations (plantas em malha 3D)

Um punhado de entradas em `VEGETATION` (`ynn/tables.py`) têm uma espécie
de [`gielis.plants`](../gielis-equations/gielis/plants) associada
(`arvore`, `arbusto`, `espinheiro`, `bambu`, `videira`, `cogumelo`,
`samambaia` ou uma das flores: `flor`, `rosa`, `dalia`, `margarida`,
`girassol`, `tulipa`, `lavanda`; as áreas guardam a espécie em
`especie_vegetacao`). Quando uma dessas é sorteada, o gerador chama
`gielis.plants.generate_plant` de 3 a 6 vezes (`PLANT_VARIANT_RANGE` em
`ynn/generator.py`) — mesma espécie, formas diferentes a cada chamada —
e salva cada malha em `output/plantas/camada{N}_area{i}_{especie}_{n}.obj`;
os caminhos aparecem em `plantas_obj`, junto do texto da área. Um jardim
não teria uma única planta solitária por canteiro. Vegetação de cobertura
(gramado, musgo, líquens) não tem espécie e continua só texto, sem malha.
Veja `camada2_com_plantas_exemplo.md` para um exemplo (nota: gerado antes
dessa mudança, ainda mostra uma malha só por área).

Uma área em ruína (o estado vem do Detalhe do local) ganha de 1 a 3 galhos/troncos caídos ou cortados, via
`gielis.plants.generate_fallen_branch` — um detrito de jardim sem cuidado, não uma espécie viva; os caminhos
aparecem em `galhos_caidos_obj`.

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
  Outros efeitos vêm do **Detalhe** do local (`sortear_extras_torre`): a torre é **sempre**
  coberta de hera (hastes de folhas subindo pela parede, `trepadeiras_obj`, via
  `gielis.structures.generate_tower_vines`, como no livro); com "Fértil" ela perde o telhado e algo brota lá
  em cima (`TORRE_BROTO`: árvore, mato, flores, samambaias, cogumelos; `topo_obj` e `conteudo.topo_brotado`),
  com "Queimado" ou "Fumegante" o telhado queima e o topo fica aberto e enegrecido
  (`conteudo.topo_queimado`), ambos com a malha destelhada (piso de terra, cornija e parapeito no topo); e
  quando o chão se mexe ("Estrondo", "Convulso", "Abismos", "Invertido", "Flutuante") a torre fica
  inclinada (`inclinacao`: 4 a 12 graus, azimute sorteado).
- **torre** (`gielis.structures.generate_tower`, conteúdo em `generate_torre_conteudo`),
  como a do livro: um *folly* de tijolo e madeira de ~6 m de largura, com a **porta
  térrea entreaberta** (a folha gira pra fora), **janelas de veneziana** em quatro setores
  de cada andar de cima (metade entreaberta, metade fechada: `geometria.janelas`), escada
  de madeira em espiral, tapete mofado, poças d'água junto às janelas e papel de parede
  descascando — uma malha por material (`plot.malhas`). **Dá pra entrar por qualquer
  andar escalando até uma janela** (`plot.escalada`: andares com janela, se há trepadeiras
  e a regra de escalada, `tables.TORRE_ESCALADA_REGRA`). São `d6+2` andares; **cada andar
  rola 1d12** em `tables.TORRE_ANDARES` (nada, tesouro, algo mora aqui, algo também
  explora, móveis, estante, ninhos, teias, esqueleto, rações, retratos, espelho) e o
  **topo rola 1d12 duas vezes** em `tables.TORRE_TOPO` (por isso `andares` tem uma entrada a
  mais, com `extra: true`). Mecânicas do livro: a estante esconde um livro de magias de
  1º nível em 1 de 6; os retratos são 1d4 e cada um vale 100 de ouro × profundidade; o
  grande tesouro do topo são 3 achados e o monstro poderoso soma os andares à
  profundidade; a biblioteca tem 1d12 magias de 1º nível, 1d10 de 2º, 1d8 de 3º, 1d6 de
  4º, 1d4 de 5º e uma de 6º ou mais.
- **ruína e estilo**: o estado de um lugar vem do **Detalhe** sorteado (tabela do livro, `d20 +
  profundidade`): só "Bem Cuidado" e "Coberto de Hera" o deixam inteiro; nos demais **o lugar jaz em
  ruínas** (`plot.estado`, `generator.DETALHES_INTEIROS`) — por isso, quanto mais fundo, mais ruínas, e
  "Bem Cuidado" só sai nas profundidades 0 a 3. Cada estrutura tem o seu "esquema" de ferragens
  (`plot.estilo`, de `gielis.ferragens`): **art nouveau** (grades de ferro forjado em curvas de chicote,
  gavinhas e botões, simétricas, como as portas de Ernest Blerot), **rústico** (corrimão e treliça de
  ripas de madeira) ou **clássico** (balaustrada de pedra com jarros). Isso vale para as grades das
  **janelas e da porta** da torre e para o **parapeito** do topo destelhado da torre, do gazebo, do
  terraço das estátuas e da escadaria. Em ruína, a torre perde pedaços de parede, a porta cai da
  dobradiça, as venezianas pendem ou somem, balaústres e painéis caem, **jarros tombam**, trechos de
  corrimão desaparecem e o **musgo** cobre a base; uma área em ruína espalha 1d3 galhos caídos. Duas
  estruturas vêm de uma foto de jardim abandonado: a **escadaria curva** (`escadaria`, o Jardim do
  Penhasco: degraus de pedra em anfiteatro em volta de um gramado redondo, muro de arrimo, parapeito
  com jarros e musgo) e a **casa inclinada** (`casa_inclinada`, as Ruínas de Ynn: casa de dois andares
  de janelas vazias, torta, com um canto afundado no chão).
- **o que o Detalhe faz**: "Teto de Vidro" cobre o lugar com uma cúpula de vidro (`plot.cupula_vidro`: o
  lugar inteiro dentro de uma estufa gigante); "Queimado" e "Fumegante" queimam o telhado da torre;
  "Fértil" abre o topo e deixa algo brotar; "Estrondo", "Convulso", "Abismos", "Invertido" e "Flutuante"
  (o chão se mexe) inclinam a torre; "Alagado", "Congelado" e "Queimado" dão ao lugar um disco de água,
  gelo ou cinza no Godot; "Luminoso" e "Poste de Luz" acendem luzes. A torre é **sempre** coberta de
  hera, como a do livro.
- **estufas** (locais "Estufas" e "Orquidários"), como no livro: **um punhado de dados jogados no
  papel** (`1d4 + 1`, `sortear_dados_estufa`), cada dado uma casa de vidro e ferro (módulo
  `gielis.greenhouse`, uma malha por material). **A planta baixa é a do dado** (d4, d8 e d20 triângulo; d6 e d10
  retângulo; d12 pentágono; cada canto, uma porta), **o d12 tem 2 andares e o d20, 3**, e dado maior dá casa
  maior. **O número tirado diz o que há dentro** (`tables.ESTUFA_CONTEUDO`, na ordem do livro: plantas
  raras, nada, ervas medicinais, frutas, plantas venenosas, mesas e cadeiras, 1d4+1 jarros carnívoros,
  sem plantas, limo digestivo, gaiolas de ouro, esporos, esqueletos vegetais; **13 ou mais é a estufa
  lacrada**, só possível no d20). A flora de cada casa segue o conteúdo (`ESTUFA_FLORA_POR_RESULTADO`:
  tema e densidade, de vazia a selva), e as de salão (chá, gaiolas) têm piso em xadrez. No **Orquidário**
  sempre há orquídeas (`1d10 × profundidade` de prata) e os resultados pares são só orquídeas. O estado
  (inteira ou em ruínas, com painéis faltando, ferrugem e trepadeiras mortas) vem do Detalhe do lugar.
  Cada conjunto vira `plot.estufas` (uma entrada por dado, com `x`/`z` locais, planta, conteúdo e flora).
  A **estufa colossal** é o modo `--estufa-colossal sempre`: o vidro cobre o nível inteiro (`estufa_colossal`,
  raio 55–80 m, 32 lados, 3 andares), entra-se por um portal num lado (`layout.portas_estufa`, tipo
  `entrada`, junto ao nó 0) e só se sai pelo portal do lado oposto (tipo `saida`, junto ao local mais
  fundo), e **sob ela só há alas de vidro** (`tables.ALAS_VIDRO`, `plot.ala`: vidraças e orquidários, um dado
  cada), nada de torre, gazebo ou jardim aberto.
- **gazebo**: pavilhão aberto (plataforma, 6 ou 8 postes, grade baixa com
  uma abertura de entrada, telhado em cúpula e pináculo). Em
  `plot.conteudo`: estado do pavilhão (`GAZEBO_ESTADO`), um bibelô largado
  (`GAZEBO_BIBELOS`), um tesouro (`TREASURE`) e a regra de abrigo noturno
  (`REFUGIO_GAZEBO`: com uma chama acesa lá dentro, as criaturas não
  atacam).
- **canteiro**: um leito denso de uma única espécie (uma das flores ou
  `arbusto`, `CANTEIRO_SPECIES`), como as plantas por área mas mais compacto;
  um canteiro com nome de flor cultiva essa flor (`tables.CANTEIRO_ESPECIE_POR_LOCAL`:
  lavanda, dálias...). As flores têm cor própria (cor de vértice no `.obj`).
  O lago ganha flores de nenúfar, e as alas de orquidário sob a estufa colossal
  têm o tema de flora `orquidario` (orquídeas, samambaias, folhas largas).

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
