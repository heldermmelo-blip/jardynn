# lotfp-rules

Módulo de regras de criação de personagem de nível 1, inspirado no sistema
de *Lamentations of the Flame Princess*. Implementa a mecânica (rolagens,
dados de vida, perícias, carga) como código original — nenhum texto do
livro é reproduzido aqui.

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
- Sistema de magia (Magic-User e Cleric).
- Ligar personagens gerados aqui aos encontros do
  [`ynn-generator`](../ynn-generator).
