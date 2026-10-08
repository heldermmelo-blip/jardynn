# Notas — números conferidos contra o livro

Este módulo implementa a *mecânica* de criação de personagem de nível 1 de
Lamentations of the Flame Princess como código original (nenhum texto do
livro é reproduzido). Os números abaixo foram **conferidos contra o PDF de
regras** (`LotFPRulesMagicFreeNoArt.pdf`, tabelas de cada classe, Pontos de
Vida, Bônus de Ataque, Perícias do Specialist, Dinheiro Inicial e a tabela de
Carga). Onde minha estimativa anterior estava errada, ela foi corrigida.

| Item | Onde | Valor (conferido) |
|---|---|---|
| Dado de vida no nível 1 | `lotfp/classes.py` | Fighter d8, Specialist d6, Magic-User d6, Cleric d6 |
| Mínimo de PV no nível 1 | `lotfp/classes.py` | Fighter 8, Specialist 4, Magic-User 3, Cleric 4 (vale se o dado + Constituição ficar abaixo) |
| Bônus de ataque no nível 1 | `lotfp/classes.py` | Fighter +2, demais +1 |
| Pontos de perícia do Specialist no nível 1 | `lotfp/classes.py` | 4 |
| Perícias | `lotfp/skills.py` | Architecture, Bushcraft, Climb, Languages, Search, Sleight of Hand, Stealth, Tinker (todas 1-em-6 para todos; cada ponto soma 1, teto 6) e Sneak Attack (multiplicador de dano ×1, +1 por ponto, sem teto) |
| Testes de Resistência no nível 1 (Paralisia / Veneno / Sopro / Dispositivos / Magia) | `lotfp/saves.py` | Fighter 14/12/15/13/16, Specialist 14/16/15/14/14, Magic-User 13/13/16/13/14, Cleric 14/11/16/12/15 |
| Modificadores de atributo | `lotfp/abilities.py` | 3 = −3, 4–5 = −2, 6–8 = −1, 9–12 = 0, 13–15 = +1, 16–17 = +2, 18 = +3 |
| Vagas de magia de nível 1 no nível 1 (Magic-User e Cleric) | `lotfp/spells.py` | 1 para cada |
| Dinheiro inicial | `lotfp/equipment.py` | 3d6 × 10 de prata |
| Carga | `lotfp/equipment.py` | por pontos, não por slots: +1 ponto a partir de 6, 11, 16 e 21 itens diferentes; cota de malha +1; placas +2; item de tamanho exagerado +1 cada. 0–1 = movimento de exploração 120', 2 = 90', 3 = 60', 4 = 30', 5+ = parado |

Os feitiços em `lotfp/spells.py` (nomes e descrições) e o kit em
`STARTING_EQUIPMENT` são **conteúdo original**, não uma transcrição das
listas do livro — só a mecânica (preparar/rezar de véspera, gastar a vaga ao
lançar; comprar equipamento com a prata inicial) é a mesma. Se quiser
fidelidade à lista real de LotFP, substitua as entradas de `SPELLS` pelas do
livro.

Ainda não modelado (o livro tem, mas o módulo é só de nível 1): o modificador
de Sabedoria nos testes que não são de magia e o de Inteligência nos de
magias de Magic-User, o modificador de Constituição no deslocamento diário, e
as demais classes (anões, elfos, halflings) e níveis acima do 1.
