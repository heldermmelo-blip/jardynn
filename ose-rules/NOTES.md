# Notas — licença e valores a conferir contra o livro

## Contexto de licença

A Necrotic Gnome afirma publicamente (blog "An Update on Old-School
Essentials and the OGL") que **"quase o Rules Tome completo é definido
como Open Game Content"** sob a OGL 1.0a nas edições **anteriores a
2026** — a declaração exata fica na Section 15, no final do livro, que
eu não tenho em mãos. A partir de 2026 o *Player's Book* usa uma licença
própria da editora, fora da OGL.

Este módulo foi escrito **de memória**, sem o texto-fonte do Rules Tome
à vista — uma aproximação de boa-fé da estrutura clássica de B/X
(Moldvay/Cook 1981), da qual o OSE é um retroclone fiel, não uma
transcrição do livro em si. Se/quando tivermos acesso à Section 15 real
(ou ao texto do livro), os valores abaixo devem ser conferidos e, se
necessário, substituídos — e aí sim poderemos considerar reproduzir
texto real do Rules Tome sob os termos da OGL 1.0a (incluindo o texto da
licença e a atribuição correta no projeto).

## Valores a conferir

| Item | Onde | Valor atual (estimado) |
|---|---|---|
| Dado de vida por classe | `ose/classes.py` | Fighter/Dwarf d8, Cleric/Elf/Halfling d6, Magic-User/Thief d4 |
| Bônus de ataque no nível 1 | `ose/classes.py` | Fighter/Dwarf +1, demais +0 |
| Valores-alvo de Teste de Resistência no nível 1, por classe | `ose/saves.py` | ver `SAVES_LEVEL_1` — categorias clássicas (Morte/Veneno, Varinhas, Paralisia/Petrificação, Sopro, Cajados/Magias) |
| Vagas de magia de nível 1 | `ose/spells.py` | Magic-User e Elf: 1; **Cleric: 0** (só reza a partir do nível 2, estrutura clássica do B/X) |
| Lista de feitiços de nível 1 (nomes) | `ose/spells.py` | nomes clássicos do B/X (Charm Person, Sleep, Read Magic etc.) — descrições são resumo próprio, não transcrição |
| Perícias percentuais do Thief no nível 1 | `ose/skills.py` | ver `THIEF_SKILLS_LEVEL_1` |
| Equipamento inicial e limite de carga | `ose/equipment.py` | mesmo padrão genérico usado em `lotfp-rules` |

Testes de Resistência das 3 classes demi-humanas (Dwarf, Elf, Halfling)
são particularmente incertos — dei valores plausíveis (Dwarf/Halfling
mais resistentes que a média, refletindo a fama clássica de resiliência
dessas raças), mas são a estimativa menos confiável do módulo.

Progressão além do nível 1 ainda não foi implementada.
