# jardynn-game

Projeto Godot 4 que visualiza em 3D o conteúdo procedural gerado pelos
pacotes Python deste repositório (`ynn-generator`, `gielis-equations`,
`ose-rules`, `lotfp-rules`). A integração é **offline**: os scripts Python
rodam fora do jogo e escrevem os assets prontos (`.obj` de plantas, `.json`
de camadas/personagens) direto dentro deste projeto; o Godot só importa e
lê o que já foi gerado.

## Estrutura

```
jardynn-game/
  assets/
	plants/   ← malhas .obj geradas por gielis.plants (via ynn-generator)
	data/     ← camadas de jardim exportadas em JSON
  scenes/
	Main.tscn ← cena de exemplo: instancia as plantas de uma camada
  scripts/
	Main.gd   ← lê o JSON e monta a cena (ver comentário no topo do arquivo)
```

## Gerando novos assets

A partir da raiz do repositório (`Claude workspace/`):

```bash
cd ynn-generator
python -m ynn.cli --modo livro --profundidade 4 --seed 42 --json \
	--output ../jardynn-game/assets/data/camada1.json \
	--plant-output-dir ../jardynn-game/assets/plants
```

- `--json` faz o gerador emitir dados estruturados (camada, terreno, áreas,
  NPCs, criaturas, caminho da planta) em vez do Markdown normal.
- `--plant-output-dir` faz as malhas `.obj` das plantas serem salvas direto
  dentro do projeto Godot.
- `--terrain-resolution`/`--terrain-cell-size` ajustam a grade de relevo
  (`terreno.alturas` no JSON) — ver seção **Relevo** abaixo.

Cada área com vegetação de espécie única (`plantas_obj` no JSON) gera de 3
a 6 variantes da malha (mesma espécie, formas diferentes) — `Main.gd`
espalha várias cópias de cada variante ao redor da área (`scatter_radius`,
`min_instances_per_variant`/`max_instances_per_variant` no inspetor), pra
parecer um canteiro de verdade em vez de uma planta isolada.

Cerca de 1 em 6 áreas também ganha galhos ou troncos caídos/cortados
(`galhos_caidos_obj` no JSON, via `gielis.plants.generate_fallen_branch`)
— sinal de um jardim sem cuidado. A malha já vem deitada da própria
geração; `Main.gd` só posiciona e gira em Y.

## Mapa de pontos (modo livro)

O JSON padrão agora é um **mapa de pontos** como o do livro (ver README do
`ynn-generator`): a entrada no topo (profundidade 0), cada camada numa
fileira mais abaixo, locais sorteados por `d20 + profundidade` e ligados
por trilhas. `Main.gd` desenha cada ligação (`layout.arestas`) como uma
fita rente ao terreno: **marrom** = trilha normal entre camadas, **azul** =
atalho para um local já explorado, **vermelho** = descida para um local bem
mais fundo. O console imprime, de cada local, a profundidade, o nome e o
detalhe. O relevo varia só ao redor dos locais cujo detalhe pede.

As **torres são prédios onde os aventureiros entram**: paredes ocas de
~6 m de largura, porta no térreo, janelas nos andares de cima, piso em
cada andar e uma escada em espiral (material de dupla face, já que as
paredes não têm espessura). O **conteúdo sorteado de cada andar** aparece
dentro: `TorreProps.gd` monta o objeto de cada andar com formas simples
(baú, estante, sino, telescópio, caixão...), `Main.gd` o encaixa no piso em
anel (longe da porta, girando a cada andar), com um rótulo flutuante
("Andar 3 · Móveis podres") e uma luz por andar. Tudo vem do JSON *daquela*
torre (`geometria` e `conteudo`): cada uma tem seus andares sorteados.

Nem toda torre é igual: algumas têm **trepadeiras subindo pelas paredes**
(`trepadeiras_obj`), outras **perderam o telhado e algo brotou no topo**
(`topo_obj`) e **uma em cada dez fica inclinada** (`inclinacao`). A torre
inteira (malha, plantas, objetos dos andares, rótulos e luzes) fica num nó
girado em torno da base, então nada se desalinha quando ela pende.

## Layout 2D

Desde a introdução de `layout` no JSON (ver README do `ynn-generator`), o
jardim não é mais uma linha reta: é um campo do tamanho de um campo de
futebol (105m x 68m por padrão) com áreas, torres, estufas e canteiros
espalhados numa grade de lotes. `Main.gd` lê `layout.plots` e instancia
cada um na posição (x, z) do lote (estufa como malha única; canteiro
como cluster denso, igual às plantas de área mas com `canteiro_radius`
menor). JSON gerado antes dessa mudança (sem `layout`) ainda funciona —
cai de volta na linha reta antiga (`area_spacing`).

Estufas (`plot.planta`: porte, lados, andares, alas, estado, piso xadrez)
vêm em várias malhas, uma por material (`plot.malhas`: moldura pintada
conforme `planta.moldura`, vidro translúcido, soco, piso preto/branco e
trepadeiras mortas) e giradas (`rotacao_y`) para a porta olhar o caminho que
leva até ela. Cada uma imprime seu conteúdo (`plot.conteudo`: texto, valor em
ouro ou criatura). Uma minúscula pode estar no meio de um espelho d'água
(disco translúcido + calçada até a porta), e a estufa colossal
(`estufa_colossal`) cobre o nível inteiro, com um aro luminoso verde na
entrada e um âmbar na saída, ligados por trilhas aos nós extremos. As estufas trazem a flora de dentro (`plot.flora_interna`: tema, densidade e
um exemplar por planta, com posição, escala e giro; as mortas ficam marrons).
Sob a estufa
colossal só há alas de vidro (vidraças e orquidários, com o valor das
orquídeas impresso). As estruturas pitorescas (fonte, estátuas, labirinto,
mausoléu, lago, lago congelado e gramado de xadrez) vêm em uma malha por
material (`COR_PITORESCO` em `Main.gd`), sobre o chão aplainado, e imprimem
seus detalhes. Gazebos
imprimem estado, bibelô, tesouro e a regra de abrigo noturno.

A torre é tratada à parte: além da malha, imprime no console o conteúdo
de cada andar (`plot.conteudo`, ver README do `ynn-generator`) e espalha
hera (`hera_obj`) rente à base (`ivy_radius`).

Fichas de personagem avulsas (OSE ou LotFP) também podem ser exportadas em
JSON do mesmo jeito:

```bash
cd ose-rules
python -m ose.cli --classe fighter --seed 7 --json --output ../jardynn-game/assets/data/personagem.json
```

## Relevo

Cada camada tem um `terreno` sorteado uma única vez (o "descritor de
localidade", `ynn.tables.LOCALIDADE`), que decide se o relevo é plano ou
varia — e o quanto — via uma grade de pontos com altura (`terreno.alturas`,
`resolucao` x `resolucao`, espaçados por `tamanho_celula`), gerada com o
algoritmo diamond-square em `ynn.terrain`. `Main.gd` monta essa grade como
uma malha triangulada (`SurfaceTool`) e usa a mesma grade, por interpolação
bilinear, para apoiar cada planta na altura correta do terreno.

O terreno cobre `(resolucao - 1) * tamanho_celula` unidades de lado,
centrado na origem (padrão: 32 × 3.0 = 96 unidades). Isso precisa ser
maior que a extensão da linha de áreas (`area_spacing` × nº de áreas, em
`Main.gd`) — senão as últimas áreas caem fora do chão gerado. Ajuste
`--terrain-cell-size`/`--terrain-resolution` se aumentar `--areas` ou
`area_spacing` muito além do padrão.

## Abrindo no Godot

1. Abra este projeto (`jardynn-game/`) no Godot 4.3+ — na primeira vez, o
   editor vai importar automaticamente os `.obj` gerados (aparece uma barra
   de progresso de import). Isso é necessário antes de rodar a cena, senão
   `Main.gd` não encontra as malhas (`load()` de um `.obj` só funciona
   depois que o editor gerou o `.import` correspondente).
2. Rode a cena `scenes/Main.tscn` (F6). As plantas da camada aparecem
   enfileiradas na cena, e o texto de cada área, além de NPCs e criaturas,
   é impresso no painel **Output**. A câmera é livre (`FreeLookCamera.gd`):
   segure o botão direito do mouse pra olhar em volta, WASD pra mover,
   Q/E pra descer/subir, Shift pra acelerar.
3. Para ver uma camada diferente, gere um novo JSON (seção acima),
   aponte `layer_json_path` no inspetor do nó `Main` para o novo arquivo
   (ou sobrescreva `camada1.json`) e rode de novo.

## Limitações conhecidas / próximos passos

- Sem UI ainda para exibir o texto das áreas dentro do jogo (hoje só vai
  pro console) — dá pra trocar por `Label3D`/`RichTextLabel` por cima de
  cada planta.
- NPCs e criaturas são só impressos, não instanciados como personagens no
  mundo 3D — os dados (atributos, PV, ataques etc.) já vêm prontos do JSON
  para quando isso for implementado.
- `--plant-output-dir` grava o caminho completo do lado Python em cada
  entrada de `plantas_obj` no JSON; `Main.gd` extrai só o nome do arquivo
  e busca em `res://assets/plants/`, então o projeto continua funcionando
  mesmo que o caminho absoluto mude entre máquinas.
