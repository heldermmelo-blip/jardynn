# ynn-generator

Gerador procedural de camadas de jardim para RPG, por tabelas de texto —
estrutura inspirada em *The Gardens of Ynn* (Emmy Verte): um "location
crawl" dividido em camadas que ficam mais estranhas e perigosas conforme se
avança. As tabelas e o texto aqui são inteiramente originais; nenhum
conteúdo do livro é reproduzido.

A ideia é, depois de estabilizar as tabelas, ligar cada área a uma planta
gerada de verdade (malha 3D) usando a biblioteca
[`gielis-equations`](../gielis-equations), generalizando o que já existe em
`examples/rpg_plant.py` para outros tipos de vegetação além de árvores.

## Ligação com lotfp-rules

Um punhado de entradas em `DENIZENS` (`ynn/tables.py`) são humanoides e
têm uma classe de LotFP associada (`fighter`, `specialist`, `magic_user`
ou `cleric`). Quando uma dessas é sorteada, o gerador chama
[`lotfp-rules`](../lotfp-rules) (`lotfp.character.create_character`) e
anexa uma ficha de nível 1 completa logo abaixo da área no Markdown
gerado — veja `camada3_com_npc_exemplo.md` para um exemplo. Os demais
denizens (a maioria — animais, objetos, fenômenos) continuam só texto,
sem ficha.

Isso depende de `lotfp-rules` estar na pasta irmã (`../lotfp-rules`);
`ynn/generator.py` ajusta o `sys.path` automaticamente para achá-la.

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
