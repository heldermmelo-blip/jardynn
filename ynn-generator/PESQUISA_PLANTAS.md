# Pesquisa: plantas e árvores ornamentais exóticas para o jogo

Levantamento para ampliar as espécies de `gielis.plants` (hoje 23: ver
`gielis-equations/README.md`). Os fatos abaixo vêm das fontes listadas no fim;
o que é conhecimento geral meu, sem fonte conferida, está marcado com **(geral)**.
Conferir tamanhos e datas em fonte botânica antes de usar como regra de jogo — as
fontes da busca são, em boa parte, sites de jardinagem e blogs, e algumas
divergem entre si (altura da araucária, situação de conservação, vida da
*Welwitschia*).

Tudo aqui é pra **forma e ambientação**; textos de tabela continuam originais.

## O que a pesquisa trouxe

### Árvores de silhueta marcante
| Planta | O que a faz boa pro jogo | Forma 3D proposta |
|---|---|---|
| **Araucária / pinheiro-macaco** (*Araucaria araucana*) | Galhos finos e espaçados, saindo na horizontal e arqueando pra cima nas pontas; folhas triangulares, pontudas, em volta do galho. O nome vem de uma piada vitoriana: "faria um macaco desistir de subir". Chamada "fóssil vivo". | Esqueleto em verticilos (galhos a cada nível, ângulo ~90° e curva final pra cima), folhas em cone. Espécie `araucaria`. |
| **Dracena-dragão** (*Dracaena cinnabari*, a de Socotorá) | Copa em guarda-chuva; ramifica sempre em duas (dicotomia); seiva vermelha, o "sangue de dragão". Poucos metros de altura, tronco grosso. | Esqueleto dicotômico (`branches_per_node=2`, ângulo fixo), tufos de folhas rígidas nas pontas, tronco curto e grosso; marca vermelha no tronco. Espécie `dracena_dragao`. |
| **Baobá e árvores-garrafa** (*Adansonia*, *Brachychiton*) | Tronco inchado, que guarda água; apelidos como "árvore de cabeça pra baixo", "garrafa", "urna". Cada espécie de baobá tem fruto de forma própria. | Tronco em tronco-de-cone abaulado, poucos galhos curtos e copa rala; versão menor (garrafa) e uma enorme. Espécie `baoba`. |
| **Samambaia arbórea** (*Dicksonia antarctica*) | Folhagem exuberante sobre um tronco fibroso, bom em clima ameno e úmido. | Tronco fibroso curto + coroa de frondes grandes (reaproveita o gerador de samambaia). Espécie `samambaia_arborea`. |
| **Bananeira ornamental** (*Musa basjoo*) | Folhas enormes, "selvagens", que dão drama. | Já temos `folha_larga`; fazer uma versão alta com pseudotronco. |
| **Palmeiras** | A "exótica padrão" das estufas vitorianas. | Já temos `palmeira`; variar (leque, plumosa, garrafa, de-vinho). |
| **Paulownia** (árvore-foxglove) | Flores em forma de dedaleira, em maio. | Árvore com cachos de flores tubulares; vira variação de `arvore` com flor. |
| **Medronheiro** (*Arbutus unedo*) | Fruto e flor ao mesmo tempo, no fim do ano. | Variação de `arbusto/arvore` com frutos vermelhos. |
| **Ginkgo, cicas** **(geral)** | Folha em leque; cicas parecem palmeiras pré-históricas. | `ginkgo` (folha em leque) e `cica` (tronco baixo + coroa de frondes rígidas). |

### Plantas "estranhas" (ótimas pra Ynn)
| Planta | Detalhe | Ideia de jogo |
|---|---|---|
| **Pedras-vivas** (*Lithops*) | Camufladas como seixos; o nome grego quer dizer "cara de pedra". | Monte de "seixos" no chão da estufa-deserto; um deles é planta (encontro ou tesouro). |
| **Welwitschia** | Só duas folhas, que crescem a vida inteira (séculos a milênios, segundo as fontes). | Planta imóvel, rasteira, de duas fitas enormes; "fóssil vivo". |
| **Flor-cadáver** (*Amorphophallus titanum*) | Inflorescência de ~4,5 m; floresce poucas vezes na vida; cheira a carne podre. | Espata gigante central de uma estufa; regra de cheiro/náusea. |
| **Rafflesia** | Uma das maiores flores do mundo (~1 m); parasita de cipós. | Flor enorme rente ao chão, sem folhas, ligada a uma videira. |
| **Planta-morcego** (*Tacca chantrieri*) | Flores escuras com filamentos de 30 cm; pede umidade e sombra. | Flor escura com "bigodes"; combina com estufa de sombra. |
| **Lírio-vodu** (*Sauromatum venosum*), **planta-camundongo** (*Arisarum proboscideum*) | Aráceas de aspecto bizarro. | Variações do mesmo molde da flor-cadáver, em escala menor. |

### Carnívoras, aquáticas e epífitas
- **Carnívoras** (*Nepenthes*, *Dionaea*, *Drosera*, *Sarracenia*): febre vitoriana, ligada ao gosto pelo gótico e às estufas aquecidas. *Nepenthes* cultivada em Kew desde 1789, com "boom" depois de 1830; a papa-moscas chegou a Londres em 1768. Auge de *Sarracenia* e *Nepenthes* na Inglaterra de 1880 a 1914. → Espécies `nepentes` (jarros pendurados em cipó), `dioneia` (armadilhas dentadas), `drosera` (rosetas com pelos brilhantes), `sarracenia` (trombetas). Já existe a criatura *Jarro Carnívoro*: as plantas decorativas podem anunciar o perigo.
- **Aquáticas**: a **vitória-régia** (*Victoria amazonica*) tem folhas de até ~3 m, que aguentam peso; a casa de nenúfares de Kew (1852) foi feita pra ela, e a tradição diz que a nervura da folha inspirou o Palácio de Cristal de Paxton (tradição, não fato documentado). **Lótus** (*Nelumbo*): quase nada na busca. → `vitoria_regia` (folha gigante, borda erguida) e `lotus` pro lago e pras estufas; o lago já tem nenúfares.
- **Samambaias e epífitas**: a "pteridomania" (1830s até o início do século 20) e a **caixa de Ward** (vitrine de vidro fechada) levaram samambaias e depois orquídeas pra dentro das casas. → vitrines de vidro com samambaias e orquídeas como props, `bromelia`, `tillandsia` e `platycerium` (chifre-de-veado) **(geral: não confirmados na busca)**, e orquídeas-aranha (*Dracula*, **geral**) pro orquidário.

## Proposta de lotes

1. **Lote 1 (barato, alto impacto):** `araucaria`, `dracena_dragao`, `baoba`, `samambaia_arborea`, `nepentes`, `vitoria_regia`, `flor_cadaver`, `cica`.
2. **Lote 2:** `welwitschia`, `lithops`, `tacca`, `bromelia`, `platycerium`, `ginkgo`, `paulownia`, `rafflesia`.
3. **Onde entram:** novos temas de flora de estufa (`aquatico`, `carnivoras`, `desertico-raro`), os topos brotados das torres, canteiros "bizarros" nos níveis mais fundos (por banda: as estranhas só no núcleo selvagem) e um tema para o orquidário.

## Fontes

- Jardim vitoriano e estufas: [Victorian Gardenesque (TCLF)](https://www.tclf.org/category/designed-landscape-style/victorian), [Victorian Garden (Stirling Botanic Garden)](https://www.sbg.org.uk/victorian-garden)
- Plantas bizarras: [Rare and beautiful plants (Jardinería On)](https://en.jardineriaon.com/Rare-and-beautiful-plants-to-have-a-surprising-garden.html), [Bizarre plants (Plant Delights)](https://www.plantdelights.com/blogs/articles/bizarre-plants-only-a-mother-could-love), [Most unbelievable plants (Nature Hills)](https://naturehills.com/blogs/garden-blog/most-unbelievable-plants-that-really-do-exist)
- Plantas arquitetônicas: [Bold, Dramatic Plants (Gardening Know How)](https://www.gardeningknowhow.com/garden-how-to/info/dramatic-plants.htm), [Architectural Foliage](https://www.dimensions.com/collection/architectural-foliage)
- Dracena-dragão: [Toptropicals](https://toptropicals.com/catalog/uid/Dracaena_cinnabari.htm), [LLifle](https://llifle.com/Encyclopedia/TREES/Family/Dracaenaceae/32991/Draco_cinnabari)
- Araucária: [Wolverhampton Council](https://wolverhampton.gov.uk/environment-and-climate/trees-hedges-and-grass/trees/3-monkey-puzzle), [Arnold Zwicky](https://arnoldzwicky.org/2015/09/25/monkey-puzzle-tree/)
- Baobá e árvores-garrafa: [Jardinería On](https://www.jardineriaon.com/en/bottle-shaped-trees.html), [Santa Monica Daily Press](https://smdp.com/the-astounding-baobab/)
- Carnívoras: [Carnivorous Plant Newsletter, história de Nepenthes](https://cpn.carnivorousplants.org/Article.php/CPNv08n1p20-23), [Victorian Gothic e carnivoria](https://www.atmostfear-entertainment.com/literature/books/victorian-gothic-murderous-plants-vegetable-carnivory/)
- Vitória-régia: [Kew Waterlily House](https://www.kew.org/kew-gardens/attractions/waterlily-house), [Bite-sized Britain](https://www.bitesizedbritain.co.uk/kewlilyhouse111/)
- Samambaias e caixa de Ward: [Museums of History NSW](https://mhnsw.au/stories/general/wardian-cases-and-victorian-fern-craze), [Courtauld, "A little world within a world"](https://courtauld.ac.uk/research/research-resources/publications/immeditations-postgraduate-journal/immediations-online/2017-2/molly-k-eckel-a-little-world-within-a-world-the-wardian-case-of-tropical-ferns-in-the-victorian-home/), [Wardian case (Wikipedia)](https://en.wikipedia.org/wiki/Wardian_case)
