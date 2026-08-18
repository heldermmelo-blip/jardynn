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
`gielis.plants.generate_plant` e salva a malha em
`output/plantas/camada{N}_area{i}_{especie}.obj` — o caminho aparece
junto do texto da área. Vegetação de cobertura (gramado, musgo, líquens)
não tem espécie e continua só texto, sem malha. Veja
`camada2_com_plantas_exemplo.md` para um exemplo.

## Ligação com lotfp-rules

Um punhado de entradas em `DENIZENS` (`ynn/tables.py`) são humanoides e
têm uma classe de LotFP associada (`fighter`, `specialist`, `magic_user`
ou `cleric`). Quando uma dessas é sorteada, o gerador chama
[`lotfp-rules`](../lotfp-rules) (`lotfp.character.create_character`) e
anexa uma ficha de nível 1 completa logo abaixo da área no Markdown
gerado — veja `camada3_com_npc_exemplo.md` para um exemplo. Os demais
denizens (a maioria — animais, objetos, fenômenos) continuam só texto,
sem ficha.

Ambas as ligações dependem de `lotfp-rules` e `gielis-equations` estarem
nas pastas irmãs (`../lotfp-rules`, `../gielis-equations`);
`ynn/generator.py` ajusta o `sys.path` automaticamente para achá-las.

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
