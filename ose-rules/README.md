# ose-rules

Módulo de regras de criação de personagem de nível 1, inspirado no
sistema clássico de B/X D&D (Moldvay/Cook, 1981), do qual *Old-School
Essentials* (Necrotic Gnome) é um retroclone fiel. Implementa a mecânica
(rolagens, CA descendente, Testes de Resistência, magia vancian,
perícias percentuais do Thief) como código escrito de memória — ver
[`NOTES.md`](NOTES.md) para o contexto de licença (OGL nas edições
pré-2026 do OSE) e a lista completa de valores a conferir contra o Rules
Tome real.

Diferenças estruturais em relação a [`lotfp-rules`](../lotfp-rules):

- **7 classes** (raça-como-classe): Fighter, Cleric, Magic-User, Thief,
  Dwarf, Elf, Halfling.
- **CA descendente** (9 = sem armadura, menor é melhor) em vez de
  ascendente.
- **5 categorias clássicas** de Teste de Resistência, não as 5 que
  inventamos pro LotFP.
- **Cleric não tem magia no nível 1** (só reza a partir do nível 2);
  **Elf conjura como Magic-User** além de lutar.
- **Thief tem perícias percentuais** (d100), não o d6-igual-ou-abaixo do
  Specialist.

## Uso

```bash
python -m ose.cli --classe fighter --seed 42
python -m ose.cli --classe elf --seed 7
```

Classes disponíveis: `fighter`, `cleric`, `magic_user`, `thief`, `dwarf`,
`elf`, `halfling`.

## Testes

```bash
pytest tests/
```

## Próximos passos

- Conferir os valores estimados contra o Rules Tome real (ver
  `NOTES.md`) e, se a licença permitir, substituir por texto/valores
  reais sob a OGL 1.0a.
- Progressão além do nível 1.
- Ligar personagens gerados aqui ao [`ynn-generator`](../ynn-generator),
  como alternativa ao `lotfp-rules`.
