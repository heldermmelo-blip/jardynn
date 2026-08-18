# lotfp-rules

Módulo de regras de criação de personagem de nível 1, inspirado no sistema
de *Lamentations of the Flame Princess*. Implementa a mecânica (rolagens,
dados de vida, perícias, carga, magia vancian, Testes de Resistência)
como código original — nenhum texto do livro é reproduzido aqui. Os
feitiços em `lotfp/spells.py` (nomes e descrições) e as categorias/valores
de `lotfp/saves.py` também são conteúdo original, não uma transcrição do
livro.

Alguns valores numéricos são estimativas — ver [`NOTES.md`](NOTES.md) para
a lista completa do que conferir contra o livro.

## Uso

```bash
python -m lotfp.cli --classe fighter --seed 42
python -m lotfp.cli --classe specialist
```

Classes disponíveis: `fighter`, `specialist`, `magic_user`, `cleric`.

## Testes

```bash
pytest tests/
```

## Próximos passos

- Progressão além do nível 1 (Testes de Resistência, magia, ataque).
- Mais feitiços.
