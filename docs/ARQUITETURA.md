# Arquitetura

Este documento explica como as peças do projeto se encaixam: o fluxo de dados, as
regras que mandam em cada sorteio, o formato do JSON que o Godot lê e como estender o
gerador. Para rodar e testar, veja o [README da raiz](../README.md).

## 1. Fluxo de dados

```
  tabelas (ynn.tables)           equações e geradores de malha (gielis)
        │                                      │
        ▼                                      ▼
  ynn.pointcrawl  ──►  ynn.generator  ──►  .obj (uma malha por material)
  (mapa de pontos)     (monta cada lote)   + camada1.json
        │                    ▲                      │
   ynn.layout            lotfp.character            ▼
   ynn.terrain           (fichas de NPCs)      jardynn-game (Godot)
```

1. **`ynn.pointcrawl`** gera o mapa de pontos: nós por camada (0 a `profundidade_max`),
   ligados por trilhas, atalhos e descidas. Cada nó rola o **Local** e o **Detalhe** nas
   tabelas do livro (`d20 + profundidade`, o resultado preso ao tamanho da tabela).
2. **`ynn.layout`** (e `layout_grafo` no `pointcrawl`) dá a cada nó uma posição num campo
   de futebol (105 x 68 m), deixando espaço pro raio de cada estrutura.
3. **`ynn.generator.generate_nivel`** monta cada lote conforme o tipo do Local, chamando
   os geradores de malha de `gielis`, e junta tudo (mais o relevo de `ynn.terrain`) num
   dict pronto pra virar JSON.
4. **O Godot** (`scripts/Main.gd`) lê o JSON, instancia cada lote, pinta as malhas e
   imprime o texto de cada local.

## 2. Os módulos

| Módulo | Responsabilidade |
|---|---|
| `gielis.superformula`, `lame`, `curves`... | As equações do livro de Gielis (catálogo em `EQUATIONS.md`). |
| `gielis.plants` | Plantas: ramificadas (`skeleton`), flores (`flowers`), árvores por L-system (`lsystem`), exóticas (`exoticas`). `generate_plant(rng, espécie, out_path)` é a porta de entrada. |
| `gielis.greenhouse` | Casas de vidro e ferro (núcleo poligonal, alas, cúpulas), uma malha por material. |
| `gielis.structures` | A torre enterável (com porta, venezianas, escada, tapete...) e o gazebo. |
| `gielis.pitoresco` | Fonte, estátuas, labirinto, mausoléu, lagos, gramado de xadrez, escadaria, casa inclinada. |
| `gielis.ferragens` | Grades art nouveau, balaustradas de pedra com jarros, corrimãos rústicos; versão inteira ou em ruína. |
| `ynn.tables` | Todas as tabelas (Locais, Detalhes, conteúdo de estufas e torres, vegetação...). |
| `ynn.pointcrawl` | O mapa de pontos e as rolagens de Local e Detalhe. |
| `ynn.layout`, `ynn.terrain` | Posicionamento dos lotes e relevo (diamond-square localizado). |
| `ynn.generator` | A montagem de cada lote e do nível. |
| `ynn.cli` | A linha de comando: JSON ou Markdown. |
| `lotfp.*` | Fichas de personagem de nível 1 (NPCs). |

## 3. As regras que mandam

O gerador segue as tabelas do livro; as porcentagens de "ocorrência" saem da própria
mecânica das tabelas, não de números inventados:

- **Local** e **Detalhe**: `d20 + profundidade` em `tables.LOCAIS` e `tables.DETALHES` (35
  entradas cada, na ordem do livro). Quanto mais fundo, mais estranho.
- **Estado do lugar**: só o Detalhe "Bem Cuidado" e o "Coberto de Hera" o deixam
  *inteiro*; nos demais ele *jaz em ruínas* (`plot.estado`, `generator.DETALHES_INTEIROS`).
- **Efeitos do Detalhe** viram etiquetas (`plot.detalhe.efeitos`) que o gerador lê:
  `vidro` cobre o lugar com uma cúpula, `queimado`/`fumegante` queimam o telhado da torre,
  `fertil` abre o topo e faz algo brotar, `estrondo`/`convulso`/`abismos`/`invertido`/
  `flutuante` inclinam a torre, `alagado`/`congelado` desenham água e gelo, `vazio`
  tira os habitantes...
- **Estufas** e **Orquidários**: um punhado de dados (`1d4 + 1`) jogados no papel; cada
  dado é uma casa de vidro (a planta baixa é a do dado, o d12 tem 2 andares e o d20, 3) e o
  número tirado diz o conteúdo (`tables.ESTUFA_CONTEUDO`; 13 ou mais é a estufa lacrada).
- **Torre**: `d6 + 2` andares; cada andar rola 1d12 (`TORRE_ANDARES`), o topo rola 1d12
  duas vezes (`TORRE_TOPO`).
- **Profundidade** escala os valores (tesouro, ouro de plantas raras, retratos...) e,
  somada ao número de andares, o monstro do topo da torre.
- A **estufa colossal** é um modo à parte (`--estufa-colossal sempre`): o vidro cobre o
  nível inteiro e sob ela só há alas de vidro.

## 4. O JSON do nível

```
{
  "modo": "livro",
  "profundidade_maxima": 4,
  "terreno": { "resolucao", "tamanho_celula", "alturas": [[...]], "tipo_relevo", ... },
  "layout": {
    "field_width", "field_depth",
    "plots":  [ lote, ... ],
    "arestas": [ {"de", "para", "tipo": "trilha" | "atalho" | "descida"}, ... ],
    "portas_estufa": [ ... ]            // só no modo da estufa colossal
  },
  "areas": [ ... ],                      // o conteúdo narrativo dos lotes tipo "area"
  "estufa_colossal": { ... }            // só no modo da estufa colossal
}
```

Todo **lote** tem `tipo`, `x`, `z`, `no_id`, `profundidade`, `local`, `detalhe`
(`texto`, `tipo_relevo`, `efeitos`, `indice`) e `estado` (`"intacta"` ou `"ruina"`).
O resto depende do `tipo`:

| `tipo` | Campos principais |
|---|---|
| `area` | `area_index` (cruza com `areas[]`: `text`, `npc`, `criatura`, `plantas_obj`, `galhos_caidos_obj`, `especie_vegetacao`) |
| `canteiro` | `especie`, `plantas_obj` |
| `estufa` / `orquidario` | `estufas[]` (uma por dado: `dado`, `resultado`, `x`, `z` locais, `planta`, `malhas`, `conteudo`, `flora_interna`, `rotacao_y`), `raio_ocupado` |
| `torre` | `malhas`, `geometria` (raios dos andares, porta, `janelas`), `conteudo` (`andares[]`, topo duplo), `escalada`, `porta`, `hera_obj`, `trepadeiras_obj`, `inclinacao`, `estilo` |
| `gazebo` | `malhas`, `conteudo`, `estilo` |
| `fonte`, `estatuas`, `labirinto`, `mausoleu`, `lago`, `lago_gelado`, `xadrez`, `escadaria`, `casa_inclinada` | `malhas`, `raio_ocupado`, `rotacao_y`, `pitoresco` (dados da estrutura), `estilo` |

Qualquer lote pode ter `cupula_vidro` (Detalhe "Teto de Vidro"). `malhas` mapeia o
material (`moldura`, `vidro`, `tijolo`, `madeira`, `musgo`...) ao caminho do `.obj`;
o Godot usa só o nome do arquivo.

## 5. Malhas

- Uma estrutura = **vários `.obj`**, um por material; o grupo principal é o próprio
  arquivo do lote, os outros ficam ao lado como `<nome>_<grupo>.obj`.
- O importador de `.obj` do Godot cria uma superfície por objeto (limite de 256), então
  `write_obj` grava tudo num único objeto `o mesh`.
- **Cor de vértice**: `write_obj` aceita partes `(vértices, faces, (r, g, b))` e grava
  `v x y z r g b`. O Godot importa isso; o `Main.gd` liga `vertex_color_use_as_albedo`
  quando a malha tem cor (flores, nepentes, vitória-régia, cica...).
- As paredes da torre e as folhas não têm espessura: o material é de dupla face.

## 6. Como estender

- **Nova planta**: escreva `gerar_x(rng, altura=None)` devolvendo `(partes, segmentos)`,
  registre em `gielis.plants` (flores em `flowers.GERADORES_FLOR`, exóticas em
  `exoticas.EXOTICAS`, L-systems em `lsystem.GRAMATICAS`); depois use-a em
  `tables.VEGETATION`, nos temas de estufa (`generator.ESTUFA_TEMAS`) ou nos canteiros.
- **Nova estrutura pitoresca**: função em `gielis.pitoresco` que devolve `(path, info)` com
  `malhas` e `raio_ocupado`, entrada em `pitoresco.GERADORES`, uma cor por grupo em
  `COR_PITORESCO` (`Main.gd`) e um Local na tabela (`tables.LOCAIS`).
- **Novo efeito de Detalhe**: etiqueta na terceira coluna de `tables.DETALHES`; o gerador a
  lê em `plot.detalhe.efeitos` e o Godot a trata em `_spawn_ambiente`.
- **Novo objeto de andar de torre**: entrada em `TORRE_ANDARES`/`TORRE_TOPO` com um `prop`
  e um construtor `_<prop>` em `TorreProps.gd` (um teste confere que todo `prop` tem
  construtor).

## 7. Testes

Cada pacote tem os seus (`pytest`). O que é lento é gerar malhas de verdade; nos testes do
gerador de níveis elas são trocadas por um `.obj` mínimo (`tests/conftest.py`). Os testes
estatísticos usam muitas sementes e margens folgadas: servem para pegar bugs grosseiros
(uma chance trocada por 1.0, uma tabela que nunca dispara), não para validar uma taxa
exata.
