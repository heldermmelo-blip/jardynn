# lotfp-rules

Módulo de regras de criação de personagem de nível 1, inspirado no sistema
de *Lamentations of the Flame Princess*. Implementa a mecânica (rolagens,
dados de vida, perícias, carga, magia vancian) como código original —
nenhum texto do livro é reproduzido aqui. Os feitiços em `lotfp/spells.py`
(nomes e descrições) também são conteúdo original, não a lista real do
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

- Testes de Resistência (saving throws) e progressão além do nível 1.
- Mais feitiços e vagas de magia em níveis além do 1.
