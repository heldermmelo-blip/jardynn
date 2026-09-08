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
python -m ynn.cli --layer 1 --areas 5 --seed 42 --json \
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
