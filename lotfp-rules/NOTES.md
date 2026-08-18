# Notas — valores a conferir contra o livro

Este módulo implementa a *mecânica* de criação de personagem de nível 1 de
Lamentations of the Flame Princess como código original (nenhum texto do
livro é reproduzido). A estrutura geral (rolagem 3d6, quatro classes,
dado de vida + Constituição, perícias por pontos do Specialist, carga por
slots) reflete o sistema como eu o conheço, mas os números abaixo são
minha melhor estimativa, não uma transcrição — confira contra sua cópia
de LotFP e ajuste os arquivos indicados antes de usar em mesa.

| Item | Onde | Valor atual (estimado) |
|---|---|---|
| Dado de vida por classe | `lotfp/classes.py` | Fighter d8, Specialist d6, Magic-User d4, Cleric d6 |
| Bônus de ataque no nível 1 | `lotfp/classes.py` | Fighter +1, demais +0 |
| Pontos de perícia do Specialist no nível 1 | `lotfp/classes.py` | 4 |
| Lista de perícias do Specialist | `lotfp/skills.py` | Architecture, Bushcraft, Climbing, Concealment, Languages, Search, Sleight of Hand, Sneak Attack, Stealth, Tinkering |
| Valor-base das perícias | `lotfp/skills.py` | 1-em-6 geral, 2-em-6 para o Specialist |
| Equipamento inicial | `lotfp/equipment.py` | lista genérica de itens de aventureiro |
| Fórmula de limite de carga (slots) | `lotfp/equipment.py` | `10 + max(0, Força - 10)` |
| Vagas de magia de nível 1 (Magic-User e Cleric) no nível 1 de personagem | `lotfp/spells.py` | 1 vaga para cada |

Os feitiços em `lotfp/spells.py` (nomes e descrições) são **conteúdo
original**, não uma transcrição da lista de magias do livro — só a
mecânica (preparar/rezar de véspera, gastar a vaga ao lançar) é a mesma.
Se quiser fidelidade à lista real de LotFP, substitua as entradas de
`SPELLS` pelas do livro.

Testes de Resistência (saving throws) e classes/valores de nível >1 ainda
não foram implementados — ficam para quando decidirmos expandir o módulo
além da criação de personagem.
