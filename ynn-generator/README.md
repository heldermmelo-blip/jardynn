# ynn-generator

Gerador procedural de camadas de jardim para RPG, por tabelas de texto —
estrutura inspirada em *The Gardens of Ynn* (Emmy Verte): um "location
crawl" dividido em camadas que ficam mais estranhas e perigosas conforme se
avança. As tabelas e o texto aqui são inteiramente originais; nenhum
conteúdo do livro é reproduzido.

Por ora só gera texto. A ideia é, depois de estabilizar as tabelas, ligar
cada área a uma planta gerada de verdade (malha 3D) usando a biblioteca
[`gielis-equations`](../gielis-equations), generalizando o que já existe em
`examples/rpg_plant.py` para outros tipos de vegetação além de árvores.

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
