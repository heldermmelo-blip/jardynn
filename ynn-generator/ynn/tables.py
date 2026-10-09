"""Tabelas de conteúdo para o gerador de camadas de jardim.

Cada entrada é `(texto, bandas)`, onde `bandas` é `"all"` (aparece em
qualquer camada) ou uma tupla com as bandas em que pode aparecer:
`"jardim_externo"` (camadas 1-2), `"jardim_profundo"` (camadas 3-4) ou
`"nucleo_selvagem"` (camada 5+).

`DENIZENS` tem um terceiro campo, `classe` (chave de `lotfp-rules` —
`"fighter"`, `"specialist"`, `"magic_user"`, `"cleric"` — para denizens
humanoides, `None` senão) e um quarto campo, `criatura` (chave de
`ynn.creatures.CREATURES` para denizens não-humanoides com ficha de
monstro, `None` senão). No máximo um dos dois é preenchido por entrada;
um punhado (a criança que não é encontrada, a voz sem corpo, o som sem
origem) não tem nenhum dos dois — são deliberadamente só atmosfera, sem
nada para enfrentar.

`VEGETATION` também tem um terceiro campo, `especie`: `None` para
vegetação de cobertura (gramado, musgo, líquens — sem uma "planta" única
para gerar) ou a chave de uma espécie de `gielis.plants` (`"arvore"`,
`"arbusto"`, `"espinheiro"`, `"bambu"`, `"videira"`, `"flor"`,
`"cogumelo"`, `"samambaia"`), que vira uma malha 3D (.obj) real da planta
dominante daquela área.

`LOCALIDADE` descreve o relevo da camada inteira (o "descritor de
localidade" sorteado uma vez por nível) e tem um terceiro campo,
`tipo_relevo`: `"plano"`, `"leve"`, `"acentuado"` ou `"irregular"` — usado
por `ynn.terrain.generate_terrain` para decidir a amplitude do heightmap
gerado para aquela camada.

`TORRE_ANDARES` e `TORRE_TOPO` descrevem o conteúdo de cada andar da torre
do layout (ver `ynn.generator.generate_torre_conteudo`) — `TORRE_ANDARES`
para os andares normais, `TORRE_TOPO` só para o último. Formato `(texto,
bandas, tipo, prop, rotulo)`: `tipo` é `"tesouro"` (sorteia de `TREASURE`),
`"encontro"` (sorteia um denizen de `DENIZENS`) ou `None`; `prop` é o objeto
que o Godot monta no piso do andar (`"bau"`, `"estante"`, `"sino"`...; `None`
= andar vazio) e `rotulo` o texto curto que flutua sobre ele.

`ESTUFA_CONTEUDO` tem uma entrada sorteada por estufa
(`ynn.generator.generate_estufa_conteudo`), com formato `(texto, bandas,
tipo, criatura)`: `tipo` é `"valor"` (rola um valor em ouro, crescente com
a profundidade), `"criatura"` (instancia a ficha `criatura` de
`ynn.creatures.CREATURES`) ou `None` (só atmosfera/regra no próprio texto).

`LOCAIS` e `DETALHES` são as tabelas do modo livro (`ynn.pointcrawl`),
sorteadas por `d20 + profundidade`: `LOCAIS` traz `(nome, tipo_de_lote)` e
`DETALHES` traz `(texto, tipo_relevo, efeito)`. Ambas vão do ameno ao
estranho conforme o índice, então quanto mais fundo, mais estranho.

`TORRE_BROTO` diz o que brotou no topo das torres destelhadas, formato
`(texto, especie, bandas)`.

`GAZEBO_ESTADO` (como o pavilhão está) e `GAZEBO_BIBELOS` (o que ficou
largado dentro) são sorteados por `ynn.generator.generate_gazebo_conteudo`,
formato `(texto, bandas)` como as demais.

Conteúdo original, inspirado apenas na estrutura de geração por tabelas de
The Gardens of Ynn — nenhum texto do livro é reproduzido aqui.
"""

BAND_LABELS = {
    "jardim_externo": "Jardim Externo",
    "jardim_profundo": "Jardim Profundo",
    "nucleo_selvagem": "Núcleo Selvagem",
}

VEGETATION = [
    # (texto, bandas, espécie de gielis.plants se representável como planta única, senão None)
    ("Um gramado alto e escuro, pesado de orvalho, que abafa o som dos passos.", "all", None),
    ("Roseiras selvagens avançam sobre o caminho, os espinhos do tamanho de adagas.", "all", "espinheiro"),
    ("Um caniçal denso sussurra mesmo sem vento.", "all", "bambu"),
    ("Trepadeiras com flores que se fecham lentamente quando alguém se aproxima.", "all", "videira"),
    (
        "Bambus finíssimos, retos como agulhas, batendo uns nos outros com um som de sinos quebrados.",
        "all",
        "bambu",
    ),
    ("Um campo de tulipas em cores que não deveriam existir juntas.", "all", "tulipa"),
    ("Carvalhos enormes, os troncos cobertos de hera velha, as copas fechadas num dossel baixo.", "all", "carvalho"),
    ("Salgueiros chorões de ramos tão longos que varrem o chão, ondulando sem vento.", ("jardim_externo", "jardim_profundo"), "salgueiro"),
    ("Um bosque de pinheiros escuros e retos, o chão forrado de agulhas que abafam os passos.", "all", "pinheiro"),
    ("Uma araucária solitária, os galhos em candelabro, as folhas duras como escamas de lagarto.", ("jardim_profundo", "nucleo_selvagem"), "araucaria"),
    ("Roseiras bem cuidadas demais: cada rosa de uma cor, nenhuma com um só espinho fora do lugar.", "all", "rosa"),
    ("Canteiros de lavanda zumbindo de abelhas, o perfume forte demais para o ar parado.", "all", "lavanda"),
    ("Margaridas até onde a vista alcança, todas viradas para o mesmo lado.", "all", "margarida"),
    ("Dálias do tamanho de pratos, em cores que ninguém lembra de ter plantado.", ("jardim_externo", "jardim_profundo"), "dalia"),
    (
        "Cercas-vivas aparadas em formas que quase lembram animais, e que parecem ter se movido "
        "desde a última vez que alguém olhou.",
        ("jardim_profundo", "nucleo_selvagem"),
        "arbusto",
    ),
    (
        "Fileiras de girassóis voltados para um sol que não está no céu.",
        ("jardim_profundo", "nucleo_selvagem"),
        "girassol",
    ),
    (
        "Musgo espesso cobre tudo, macio demais, como se quisesse ser tocado.",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
    ),
    (
        "Cogumelos do tamanho de guarda-chuvas formam um dossel roxo sobre o caminho.",
        ("nucleo_selvagem",),
        "cogumelo",
    ),
    (
        "Samambaias gigantes, as frondes pingando uma seiva clara e adocicada.",
        ("jardim_profundo", "nucleo_selvagem"),
        "samambaia",
    ),
    ("Líquens luminescentes cobrem as pedras, pulsando devagar como uma respiração.", ("nucleo_selvagem",), None),
    (
        "Um pomar de árvores frutíferas cujos frutos caem já podres, mas ainda perfumados.",
        ("jardim_externo", "jardim_profundo"),
        "arvore",
    ),
    (
        "Um labirinto de buxo, as paredes verdes altas o suficiente para esconder um cavaleiro montado.",
        ("jardim_externo", "jardim_profundo"),
        "arbusto",
    ),
    (
        "Videiras carregadas de uvas negras, brilhantes, nenhuma ave por perto para bicá-las.",
        ("jardim_externo", "jardim_profundo"),
        "videira",
    ),
    ("Grama que range levemente sob os pés, como vidro moído fino.", ("nucleo_selvagem",), None),
    ("Um gramado formal, cortado em padrões geométricos que se perdem na neblina.", ("jardim_externo",), None),
    (
        "Espinheiros entrelaçados formando um arco sobre o caminho, secos por dentro, vivos por fora.",
        ("jardim_profundo", "nucleo_selvagem"),
        "espinheiro",
    ),
    (
        "Um canteiro de ervas cultivado com cuidado meticuloso, mas nenhuma das espécies parece ser conhecida.",
        ("jardim_externo", "jardim_profundo"),
        None,
    ),
    (
        "Um pomar bem cuidado demais, as frutas perfeitamente maduras o ano inteiro, nenhuma jamais cai no chão.",
        ("jardim_externo",),
        "arvore",
    ),
]

CANTEIRO_ESPECIE_POR_LOCAL = {
    # nome do local (`LOCAIS`) -> espécie do canteiro; sem entrada, sorteia
    "Horta de Ervas": "arbusto",
    "Roseiral": "rosa",
    "Canteiros de Cogumelos": "cogumelo",
}

FEATURES = [
    ("uma fonte de pedra, seca há muito tempo, com uma estátua no centro que já não se sabe representar o quê", "all"),
    ("um relógio de sol cujo ponteiro projeta uma sombra que não corresponde a nenhuma hora do dia", "all"),
    ("um caramanchão de ferro forjado, coberto de trepadeiras, com um banco vazio de frente para o nada", "all"),
    ("uma estufa de vidro rachado, o interior denso demais de vegetação para ser visto claramente", "all"),
    (
        "um portão de ferro entre duas colunas, sem cerca nos dois lados — ainda assim, parece errado passar por fora dele",
        "all",
    ),
    (
        "uma fileira de bustos de mármore, os rostos apagados pelo tempo ou por algo menos gentil",
        ("jardim_externo", "jardim_profundo"),
    ),
    ("um banco de pedra com um nome gravado, as letras já quase ilegíveis", ("jardim_externo",)),
    ("um aviário vazio, a porta aberta, ainda balançando de leve", ("jardim_externo", "jardim_profundo")),
    (
        "uma escadaria de pedra que sobe cinco degraus e termina abruptamente, sem parapeito",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um poço coberto por uma grade de ferro enferrujada, de onde sobe um cheiro de terra molhada e algo mais doce",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um pavilhão de treliça branca, a pintura descascando, onde algo se move quando ninguém olha diretamente",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um topiaria em forma humana, os galhos das mãos abertos como se esperando um abraço",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "uma gruta artificial de pedras empilhadas, escura demais para o tamanho que aparenta ter por fora",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    ("um espelho d'água perfeitamente parado, refletindo um céu diferente do que está acima", ("nucleo_selvagem",)),
    (
        "uma escultura de gelo que não deveria existir neste clima e não parece estar derretendo",
        ("nucleo_selvagem",),
    ),
    (
        "um pomar de estufas com o vidro embaçado por dentro, quase todas vazias — uma ainda tem uma luz acesa lá no fundo",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "um canil de pedra com uma dúzia de casinhas idênticas, cada porta entreaberta na mesma medida exata",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "uma pista de gelo perfeitamente lisa, sem uma rachadura sequer, mesmo sob o calor do meio-dia",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um lagar de vinho abandonado, as dornas cheias até a borda de um líquido escuro que ainda borbulha de leve",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "um pequeno povoado de casas em escala real, ruas estreitas e vazias entre elas, portas todas fechadas",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um tabuleiro de xadrez do tamanho de um salão de baile, as peças esculpidas na altura de uma pessoa",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "uma galeria de máscaras penduradas em fileiras perfeitas, todas voltadas para o mesmo ponto vazio",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um pequeno cemitério de bichos de estimação, lápides do tamanho de uma mão, uma delas visivelmente recente",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "uma engrenagem exposta do tamanho de uma carroça, girando devagar, sem ligação visível a nada",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "uma fogueira que arde sem lenha nem fumaça, alta demais, aquecendo um círculo de pedras vazio",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "um teatro de sombras improvisado entre dois lençóis pendurados, uma peça em andamento sem plateia nenhuma",
        ("nucleo_selvagem",),
    ),
    (
        "tanques de vidro emendados por tubos de cobre, um líquido verde-claro circulando devagar entre eles",
        ("nucleo_selvagem",),
    ),
]

DENIZENS = [
    # (texto, bandas, classe LotFP se NPC humanoide, criatura de ynn.creatures se monstro)
    (
        "um jardineiro curvado sobre um canteiro, que não ergue os olhos quando questionado, "
        "apenas continua podando algo que já não tem folhas",
        "all",
        "specialist",
        None,
    ),
    (
        "um bando de pássaros brancos, silenciosos, que pousam todos ao mesmo tempo e observam",
        "all",
        None,
        "passaros_brancos",
    ),
    (
        "uma estátua que os personagens têm certeza de já ter visto em outra pose",
        "all",
        None,
        "estatua_errante",
    ),
    (
        "um enxame de mariposas do tamanho de mãos, pousando em qualquer luz disponível",
        "all",
        None,
        "mariposas_gigantes",
    ),
    (
        "um par de luvas de jardinagem, sozinhas sobre um banco, ainda com o formato de mãos dentro delas",
        "all",
        None,
        "luvas_animadas",
    ),
    (
        "um cervo de galhada excessiva, mais galhos do que deveria ser fisicamente possível, parado imóvel",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "cervo_de_galhos",
    ),
    (
        "uma criança rindo em algum lugar próximo, embora nenhuma criança seja encontrada",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        None,
    ),
    (
        "algo grande se movendo logo abaixo da superfície de um gramado bem cuidado demais",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "algo_sob_a_grama",
    ),
    (
        "uma voz educada vinda de trás de uma cerca-viva, convidando para chá em algum lugar que não existe no mapa",
        ("jardim_externo", "jardim_profundo"),
        None,
        None,
    ),
    (
        "um gato preto sem rosto que anda em círculos perfeitos ao redor de um ponto fixo",
        ("nucleo_selvagem",),
        None,
        "gato_sem_rosto",
    ),
    (
        "um grupo de estátuas de jardim reorganizadas em uma formação que parece deliberada",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "estatua_errante",
    ),
    (
        "um som de tesoura de poda, rítmico, vindo de todas as direções ao mesmo tempo",
        ("nucleo_selvagem",),
        None,
        None,
    ),
    (
        "um viajante exausto, sentado à sombra de uma cerca-viva, que jura estar aqui há poucos minutos",
        ("jardim_externo", "jardim_profundo"),
        "fighter",
        None,
    ),
    (
        "uma clériga solitária de véu rasgado, murmurando orações para uma estátua que não é de nenhum deus conhecido",
        ("jardim_profundo", "nucleo_selvagem"),
        "cleric",
        None,
    ),
    (
        "um estudioso de olhos vidrados, anotando compulsivamente em um caderno encharcado que nunca seca",
        ("jardim_profundo", "nucleo_selvagem"),
        "magic_user",
        None,
    ),
    (
        "um arbusto podado em forma de pessoa que baixa os galhos numa reverência sempre que alguém passa perto",
        ("jardim_externo", "jardim_profundo"),
        None,
        "topiaria_ambulante",
    ),
    (
        "um jogo de xadrez completo avançando pelo caminho em formação perfeita, as trinta e duas peças em passo sincronizado",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "jogo_de_xadrez_animado",
    ),
    (
        "uma podadeira enferrujada que se arrasta sozinha em linha reta, cortando tudo que encontra pela frente",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "podadeira_mecanica",
    ),
    (
        "uma criada de porcelana fria ao toque, servindo chá com educação impecável para cadeiras vazias",
        ("jardim_externo", "jardim_profundo"),
        None,
        "serva_de_porcelana",
    ),
    (
        "uma figura envolta em pétalas de rosa negra, voz baixa e convidativa, espinhos escondidos nas dobras do vestido",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
        "noiva_de_espinhos",
    ),
]

WYRD = [
    (
        "O tempo aqui passa de forma perceptivelmente errada — um personagem descobre que está com "
        "fome ou cansado demais para o tempo que passou, ou de menos.",
        "all",
    ),
    (
        "As cores da vegetação ao redor lentamente se invertem enquanto os personagens observam, "
        "voltando ao normal só quando ninguém mais olha.",
        "all",
    ),
    ("Uma segunda sombra aparece ao lado de cada personagem, na direção errada para a luz disponível.", "all"),
    ("Plantas próximas se inclinam sutilmente na direção de quem fala mais alto.", ("jardim_profundo", "nucleo_selvagem")),
    (
        "Por um instante, todo o som desaparece — passos, respiração, vento — e então volta como se "
        "nada tivesse acontecido.",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "Os personagens percebem que estão andando em fila, na mesma ordem, sem terem decidido isso.",
        ("nucleo_selvagem",),
    ),
    (
        "Uma flor próxima murcha e floresce de novo em ciclo, cada vez mais rápido, até parar de repente.",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    ("O caminho percorrido parece mais curto ao olhar para trás do que pareceu ao andar.", "all"),
    (
        "Um cheiro doce demais permanece no ar por minutos depois que sua fonte já ficou para trás.",
        ("jardim_externo", "jardim_profundo"),
    ),
    (
        "Reflexos em qualquer superfície de água próxima se movem um segundo atrasados em relação aos personagens.",
        ("nucleo_selvagem",),
    ),
    (
        "O céu muda de cor sem nenhuma nuvem passar na frente do sol, e ninguém consegue dizer que horas são só de olhar para ele.",
        "all",
    ),
    (
        "Qualquer bússola carregada para de apontar para um lugar fixo, girando devagar sem nunca parar de vez.",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "Por um instante a gravidade parece puxar um pouco para o lado errado, se corrigindo antes que alguém chegue a cair de verdade.",
        ("nucleo_selvagem",),
    ),
    (
        "Um trecho do caminho já percorrido aparece de novo à frente, idêntico até o último detalhe.",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
]

TREASURE = [
    (
        "um medalhão de bronze verde-oxidado, gravado com um jardim que não é este, preso entre as raízes de uma árvore",
        "all",
    ),
    ("uma tesoura de podar de prata, impecavelmente afiada, esquecida sobre um banco de pedra", "all"),
    ("um pequeno frasco de vidro contendo uma única semente que pulsa levemente de calor", ("jardim_profundo", "nucleo_selvagem")),
    (
        "uma luva de jardinagem de couro fino, bordada com um nome em um alfabeto desconhecido",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    ("moedas antigas espalhadas sob um arbusto, todas do mesmo lado para cima", ("jardim_externo", "jardim_profundo")),
    ("um regador de cobre, meio enterrado, ainda com água que nunca parece acabar", "all"),
    (
        "um livro de capa de couro, as páginas em branco exceto por uma única frase escrita à mão em cada dez páginas",
        ("nucleo_selvagem",),
    ),
    ("uma chave de ferro sem fechadura correspondente à vista, pendurada em um galho baixo", ("jardim_profundo", "nucleo_selvagem")),
    (
        "um par de tesouras de poda em miniatura, do tamanho de um dedo, afiadas o bastante para cortar qualquer coisa que caiba entre as lâminas",
        ("jardim_profundo", "nucleo_selvagem"),
    ),
    (
        "uma caixa de música de latão enferrujado que toca uma melodia que ninguém reconhece, mas que todos juram já ter ouvido",
        "all",
    ),
    (
        "um broche de vidro soprado em forma de inseto, as asas ainda batendo devagar sempre que ninguém olha diretamente",
        ("nucleo_selvagem",),
    ),
]

ATMOSPHERE = [
    ("O ar tem um leve gosto de metal.", "all"),
    ("Uma luz cinzenta e sem fonte clara ilumina tudo igualmente, sem sombras fortes.", ("jardim_profundo", "nucleo_selvagem")),
    ("Longe, algo soa como um sino, mas nenhum sino é visível.", "all"),
    ("O silêncio aqui pesa mais do que deveria.", ("jardim_profundo", "nucleo_selvagem")),
    ("Um vento fraco carrega um cheiro de terra recém-revirada.", "all"),
    ("A luz do dia parece mais fraca aqui do que no resto do jardim, sem que nada bloqueie o céu.", ("nucleo_selvagem",)),
]

LOCALIDADE = [
    # (texto, bandas, tipo_relevo) — tipo_relevo em "plano", "leve", "acentuado" ou "irregular";
    # consumido por `ynn.terrain.generate_terrain` pra decidir a amplitude do heightmap da camada.
    ("Um terreno nivelado, quase artificial de tão uniforme, como se tivesse sido nivelado a régua.", "all", "plano"),
    ("Um gramado plano cortado por trilhas de cascalho, sem um único desnível perceptível.", ("jardim_externo",), "plano"),
    ("O chão ondula suavemente, como respirando devagar.", "all", "leve"),
    ("Pequenos montes de terra revirada quebram a uniformidade do solo em intervalos regulares demais para ser natural.", ("jardim_externo", "jardim_profundo"), "leve"),
    ("Terraços de pedra baixos dividem o terreno em patamares levemente desalinhados entre si.", ("jardim_externo", "jardim_profundo"), "leve"),
    ("Colinas abruptas se erguem sem aviso, como se o chão tivesse sido amassado por uma mão gigante.", ("jardim_profundo", "nucleo_selvagem"), "acentuado"),
    ("O solo sobe e desce em ondas profundas demais para as árvores que crescem nele parecerem naturais.", ("jardim_profundo", "nucleo_selvagem"), "acentuado"),
    ("Uma ravina serpenteia por toda a extensão visível, as bordas cobertas de raízes expostas.", ("jardim_profundo", "nucleo_selvagem"), "acentuado"),
    ("O terreno se dobra em ângulos que não deveriam sustentar o peso da vegetação que carregam.", ("nucleo_selvagem",), "irregular"),
    ("Crateras rasas se sobrepõem umas às outras, formando um relevo que parece ter fervido e endurecido.", ("nucleo_selvagem",), "irregular"),
    ("Cada passo muda a altura do chão sob os pés de um jeito que a vista não consegue acompanhar.", ("nucleo_selvagem",), "irregular"),
    ("Um trecho do chão se curva para cima contra o que deveria ser possível, e a vegetação ali cresce apontando para o lugar errado.", ("nucleo_selvagem",), "irregular"),
    ("Placas inteiras de terra flutuam a pouca altura do resto do solo, presas a ele só por raízes esticadas ao limite.", ("nucleo_selvagem",), "irregular"),
    ("Uma fenda estreita corta o caminho ao meio, funda demais para se enxergar o fundo, sem nenhuma ponte à vista.", ("jardim_profundo", "nucleo_selvagem"), "acentuado"),
    ("Placas de pedra soltas cobrem o chão irregular, cada uma balançando de leve sob o peso de quem pisa.", ("jardim_profundo", "nucleo_selvagem"), "acentuado"),
]

TORRE_ANDARES = [
    # Um d12 por andar, na ordem do livro (índice 1..12). (texto, bandas, tipo,
    # prop, rotulo) — tipo em "tesouro", "encontro" ou None; `prop` é o objeto
    # que o Godot monta no piso do andar (None = só o andar vazio); `rotulo` é
    # o texto curto que flutua sobre ele. Sem filtro de banda: o livro não tem.
    ("O andar está vazio, só poeira e silêncio.", "all", None, None, "Vazio"),
    ("Um pequeno tesouro foi deixado para trás aqui, esquecido entre os destroços.", "all", "tesouro", "bau", "Tesouro"),
    ("Algo mora neste andar e reage à presença de quem entra.", "all", "encontro", "criatura", "Habitante"),
    ("Algo também explora esta torre e está aqui agora, tão surpreso quanto você.", "all", "encontro", "criatura", "Explorador"),
    ("Móveis apodrecidos se desfazem ao toque — uma cadeira, uma mesa, os restos de uma cama.", "all", None, "mobilia", "Móveis podres"),
    ("Uma estante de livros embolorados ainda de pé; a maioria das páginas grudou umas nas outras.", "all", None, "estante", "Estante"),
    ("Ninhos de pássaros nos cantos mais altos, ovos e filhotes piando sem parar.", "all", None, "ninhos", "Ninhos"),
    ("Teias de aranha grossas dificultam a visão e o movimento por aqui.", "all", None, "teias", "Teias"),
    ("Um esqueleto preso à parede por correntes enferrujadas há muito tempo.", "all", None, "esqueleto", "Esqueleto acorrentado"),
    ("Caixotes de rações perfeitamente conservadas: o bastante pra dez pessoas por uma semana.", "all", None, "caixotes", "Rações"),
    ("Retratos emoldurados de rostos alienígenamente belos cobrem a parede.", "all", None, "quadros", "Retratos"),
    ("Um espelho de corpo inteiro que reflete com exatidão, mas só mostra o que é mágico: Ynn e seus nativos aparecem; quem o encara, talvez não.", "all", None, "espelho", "Espelho"),
]

TORRE_TOPO = [
    # Um d12 no andar mais alto — que rola duas vezes, na ordem do livro.
    ("Um sino enorme de bronze, silencioso, pendurado bem no centro do andar.", "all", None, "sino", "Sino de bronze"),
    ("Um telescópio antigo, apontado para um trecho do céu que não parece bater com o de baixo.", "all", None, "telescopio", "Telescópio"),
    ("Uma câmera escura projeta, invertida, uma imagem do jardim lá fora numa parede caiada.", "all", None, "camera_escura", "Câmera escura"),
    ("Um tesouro bem maior que o normal, escondido aqui: três achados de uma vez.", "all", "tesouro", "bau_grande", "Grande tesouro"),
    ("Uma biblioteca arcana, prateleiras cheias de livros sobre magias que ninguém mais lembra de estudar.", "all", None, "biblioteca", "Biblioteca arcana"),
    ("Algo poderoso e perigoso mora neste andar — o mais alto de todos.", "all", "encontro", "criatura", "Criatura poderosa"),
    ("Uma tábua do assoalho é, na verdade, uma placa de pressão: pisar nela solta uma rajada de dardos de metal pelas frestas (1d4 de dano em todos, a menos que passem numa Resistência a Dispositivos).", "all", None, "armadilha", "Armadilha"),
    ("Uma armadura completa, de aparência amaldiçoada, num pedestal: dá a CA de uma armadura de placas e deixa quem a veste dar um último ataque ao ser morto (se matar, ignora o dano que o mataria).", "all", None, "armadura", "Armadura amaldiçoada"),
    ("Uma máquina voadora incompleta, movida a mola de relógio, engrenagens e lona espalhadas em volta dela.", "all", None, "maquina", "Máquina voadora"),
    ("Um espelho gigante, usado pra mandar sinais refletindo luz a longa distância.", "all", None, "espelho_sinal", "Espelho de sinais"),
    ("Um caixão de vidro elegante guarda o esqueleto perfeito e belo de um dos sidhe.", "all", None, "caixao", "Caixão de vidro"),
    ("Uma lâmpada enorme — uma tigela de vidro com água e camarões luminosos — ilumina o local e todos os vizinhos.", "all", None, "lampada", "Lâmpada viva"),
]

TORRE_ESCALADA_REGRA = (
    "Dá pra entrar por qualquer andar escalando até uma janela. Cada andar subido pede um teste de Escalar "
    "(1-em-6, ou os pontos do Especialista); com trepadeiras grossas na parede, soma +2 em 6. Quem falha "
    "cai do andar onde está: 1d6 de dano por andar de queda. Veneziana entreaberta se abre sem esforço; "
    "fechada, só empurrando de dentro ou arrombando."
)

GAZEBO_ESTADO = [
    ("Um pavilhão de madeira de ar festivo, a tinta alegre desbotada e descascando em lascas.", "all"),
    ("Um coreto de madeira branca, as ripas do piso empenadas, o telhado ainda firme.", ("jardim_externo", "jardim_profundo")),
    ("Um pavilhão de treliça coberto de trepadeiras mortas, as cadeiras de vime desfiadas em volta de uma mesinha torta.", "all"),
    ("Um gazebo de madeira escura, a pintura inteira descascada, cortinas apodrecidas ainda presas nos postes.", ("jardim_profundo", "nucleo_selvagem")),
    ("Um pavilhão aberto de ferro e madeira, almofadas mofadas empilhadas nos bancos, teias de aranha de poste a poste.", "all"),
    ("Um coreto que parece recém-varrido, mas a poeira volta a cobrir tudo cada vez que alguém desvia o olhar.", ("nucleo_selvagem",)),
]

GAZEBO_BIBELOS = [
    ("um bule de porcelana lascado e três xícaras que não combinam", "all"),
    ("um baralho incompleto, as cartas gastas pelo manuseio de muitas mãos", "all"),
    ("um cachimbo longo de espuma-do-mar, ainda com resto de fumo perfumado no fornilho", "all"),
    ("uma caixinha de charutos cheia de botões, fitas e bilhetes sem destinatário", ("jardim_externo", "jardim_profundo")),
    ("um leque de renda negra esquecido sobre uma almofada", ("jardim_profundo", "nucleo_selvagem")),
    ("um tabuleiro de damas com as peças dispostas no meio de uma partida interrompida", "all"),
    ("um relógio de bolso parado numa hora que muda toda vez que é olhado", ("nucleo_selvagem",)),
]

ESTUFA_CONTEUDO = [
    # Uma entrada por número do dado jogado (1..12); o 13 ou mais é a estufa
    # lacrada. Na ordem da tabela do livro. (texto, bandas, tipo, criatura) —
    # tipo "valor" (ouro, crescente com a profundidade), "criatura" (a ficha
    # `criatura` de `ynn.creatures.CREATURES`) ou None. Sem filtro de banda.
    ("Vasos de plantas raras, cada um com a plaquinha de um colecionador: valem 1d4 + profundidade de ouro.", "all", "valor", None),
    ("Nada de notável: só vasos vazios e terra seca rachada.", "all", None, None),
    ("Plantas medicinais crescem entre os vasos: 1d6 doses, e cada uma cura 1 PV.", "all", None, None),
    ("Frutos graúdos e maduros pendem dos galhos, seguros de comer.", "all", None, None),
    ("Plantas venenosas e lindas: comer ou se espetar nelas causa 2d6 de dano (1d6 doses colhíveis).", "all", None, None),
    ("Mesas e cadeiras de ferro, enferrujadas e cobertas de musgo, postas como para um chá abandonado.", "all", None, None),
    ("De 2 a 5 jarros carnívoros enormes, enraizados, que não saem do lugar e abrem a boca para quem passa.", "all", "criatura", "jarro_carnivoro"),
    ("Nenhuma planta: prateleiras vazias e vidro limpo demais pra um lugar abandonado.", "all", None, None),
    ("Limo verde digestivo cobre o teto; um barulho súbito faz pingar gotas (1d6 de dano, como um ataque a +0).", "all", None, None),
    ("Gaiolas ornamentais de ouro penduradas do teto, vazias, ainda balançando de leve.", "all", "valor", None),
    ("Esporos densos no ar: respirar causa 1 de dano por turno, e quem falhar numa resistência a veneno continua sofrendo ao sair.", "all", None, None),
    ("Sob a folhagem, esqueletos humanos com trepadeiras nas costelas se levantam quando alguém se aproxima.", "all", "criatura", "esqueleto_vegetal"),
    ("A estufa está lacrada por fora, as portas pregadas; lá dentro, a folhagem empurra o vidro tentando sair, e uma planta solta-se a cada rodada se abrirem.", "all", None, None),
]

LOCAIS = [
    # Os 35 locais, na ordem da tabela do livro (d20 + profundidade; 35 ou mais
    # cai no último): quanto mais fundo, mais estranho. (nome, tipo_de_lote) —
    # `tipo_de_lote` é "area", "canteiro", "estufa", "orquidario", "gazebo",
    # "torre" ou uma estrutura pitoresca de `gielis.pitoresco` ("fonte",
    # "estatuas", "labirinto", "mausoleu", "lago", "lago_gelado", "xadrez",
    # "escadaria" ou "casa_inclinada"). Os textos de cada local são meus.
    ("Gramado Aparado", "area"),
    ("Horta de Ervas", "canteiro"),
    ("Treliça de Videiras", "area"),
    ("Pomar", "area"),
    ("Lagoas", "lago"),
    ("Roseiral", "canteiro"),
    ("Gazebo", "gazebo"),
    ("Estufas", "estufa"),
    ("Orquidários", "orquidario"),
    ("Jardim de Seda", "area"),
    ("Gramado de Xadrez", "xadrez"),
    ("Labirinto de Sebes", "labirinto"),
    ("Canil", "area"),
    ("Estatuária", "estatuas"),
    ("Bosque", "area"),
    ("Mausoléu", "mausoleu"),
    ("Estande de Tiro", "area"),
    ("Pátio da Fonte", "fonte"),
    ("Teatro de Sombras", "area"),
    ("Casa das Engrenagens", "area"),
    ("Torre", "torre"),
    ("Pista de Gelo", "lago_gelado"),
    ("Fogueira", "area"),
    ("Cemitério", "area"),
    ("Tubulações de Vapor", "area"),
    ("Jardim do Penhasco", "escadaria"),
    ("Canteiros de Cogumelos", "canteiro"),
    ("Galeria de Máscaras", "area"),
    ("Assentamentos", "area"),
    ("Cubas de Emenda", "area"),
    ("Berçários", "area"),
    ("Teatro de Vivissecção", "area"),
    ("Moita Eletrodinâmica", "area"),
    ("Vinícola", "area"),
    ("Ruínas de Ynn", "casa_inclinada"),
]

# O que cada local tem de próprio (um texto curto, meu), usado na descrição
# da área: o gerador sorteia vegetação e características, mas o local dá o tom.
LOCAL_TEXTOS = {
    "Gramado Aparado": "Um gramado liso, aparado rente, que se estende como um tapete entre canteiros de bordas retas.",
    "Horta de Ervas": "Canteiros de ervas em fileiras, cada uma com a plaquinha de um nome que já não se lê.",
    "Treliça de Videiras": "Treliças de madeira carregadas de videiras formam um corredor de sombra verde.",
    "Pomar": "Fileiras de árvores frutíferas, os galhos curvados sob frutos de cores demais.",
    "Lagoas": "Lagoas rasas e escuras, ligadas por pontezinhas, com nenúfares do tamanho de pratos.",
    "Roseiral": "Roseiras de todas as variedades, emboladas em espinhos, com rosas de cores impossíveis.",
    "Gazebo": "Um pavilhão aberto de madeira, de tinta desbotada, com cadeiras de vime no meio.",
    "Estufas": "Casas de vidro e ferro, espalhadas como dados jogados num papel, cada uma com a sua planta baixa.",
    "Orquidários": "Casas de vidro mornas e úmidas, cheias de orquídeas raras em vasos de musgo.",
    "Jardim de Seda": "Armações de aço que lembram árvores sem folhas, entremeadas de fios de seda colorida.",
    "Gramado de Xadrez": "Um gramado quadriculado de grama e lajes pretas, com peças enormes de pedra largadas.",
    "Labirinto de Sebes": "Sebes altas e aparadas, dobrando-se em corredores que se repetem.",
    "Canil": "Fileiras de canis de pedra, os portões de ferro entreabertos, o chão cheio de ossos roídos.",
    "Estatuária": "Um terraço de estátuas de mármore sobre pedestais, todas de rostos belos demais.",
    "Bosque": "Árvores altas e antigas, de troncos largos, fechando o céu numa copa só.",
    "Mausoléu": "Um pequeno templo de mármore, de porta escura, onde os mortos do jardim descansam.",
    "Estande de Tiro": "Alvos de palha e madeira em linha, crivados de flechas de épocas diferentes.",
    "Pátio da Fonte": "Um pátio calçado em volta de uma fonte de várias bacias, cercada de bancos.",
    "Teatro de Sombras": "Um palco de tela branca e lanternas, onde sombras sem dono encenam a mesma peça.",
    "Casa das Engrenagens": "Engrenagens enormes giram devagar, soltando ferrugem, ligadas a alguma máquina maior.",
    "Torre": "Um capricho ornamental de tijolo e madeira, que se alça acima das copas, coberto de hera.",
    "Pista de Gelo": "Um lago de gelo liso, fora de estação, onde patinadores sem rosto deixaram marcas.",
    "Fogueira": "Um poço de fogo de pedra, aceso, cercado de bancos e de lenha empilhada.",
    "Cemitério": "Lápides inclinadas sob salgueiros, os nomes gastos pela chuva de outros mundos.",
    "Tubulações de Vapor": "Canos que sobem e descem entre as plantas, chiando vapor quente em jatos curtos.",
    "Jardim do Penhasco": "Terraços de pedra descem em degraus até a beira de um abismo coberto de névoa.",
    "Canteiros de Cogumelos": "Canteiros de cogumelos pálidos, em camas de terra úmida, brilhando de leve.",
    "Galeria de Máscaras": "Uma galeria aberta com máscaras de todos os feitios penduradas, olhando pra dentro.",
    "Assentamentos": "Casebres de gente que vive aqui, amarrados uns nos outros com cordas e trepadeiras.",
    "Cubas de Emenda": "Tanques de vidro e aço, cheios de líquido turvo, onde coisas vivas são costuradas.",
    "Berçários": "Fileiras de camas de terra e vidro onde algo pequeno e vivo é cuidado.",
    "Teatro de Vivissecção": "Um anfiteatro de pedra, de plateia vazia, com uma mesa de mármore no centro.",
    "Moita Eletrodinâmica": "Uma moita de arbustos que faíscam, soltando arcos azuis entre os galhos.",
    "Vinícola": "Fileiras de videiras, prensas de madeira e barris empilhados em adegas de pedra.",
    "Ruínas de Ynn": "Muros caídos, escadas cobertas de musgo e uma casinha torta que a terra engole aos poucos.",
}

ALAS_VIDRO = [
    # (nome, subtipo) — os locais de um nível sob uma estufa colossal: todos
    # são alas de vidro (nada de torre, gazebo ou jardim aberto). Sorteada por
    # d20 + profundidade como LOCAIS (`ynn.pointcrawl.roll_tabela`); `subtipo`
    # é "vidraca" (conteúdo de `ESTUFA_CONTEUDO`) ou "orquidario"
    # (`ORQUIDARIO_TEXTOS`). Do ameno ao estranho.
    ("Vidraça das samambaias de pé de rendas", "vidraca"),
    ("Orquidário de pétalas de cera", "orquidario"),
    ("Galeria das laranjeiras em vasos", "vidraca"),
    ("Vidraça das begônias de veludo", "vidraca"),
    ("Orquidário do chá das cinco", "orquidario"),
    ("Pavilhão das palmeiras-leque", "vidraca"),
    ("Vidraça dos cactos de salão", "vidraca"),
    ("Orquidário de hastes pálidas", "orquidario"),
    ("Galeria das trepadeiras de ferro", "vidraca"),
    ("Vidraça dos bambus que rangem", "vidraca"),
    ("Orquidário dos espelhos de orvalho", "orquidario"),
    ("Pavilhão das figueiras estranguladoras", "vidraca"),
    ("Vidraça dos jarros de seda", "vidraca"),
    ("Orquidário de raízes aéreas", "orquidario"),
    ("Galeria dos nenúfares de vidro", "vidraca"),
    ("Vidraça das plantas que respiram", "vidraca"),
    ("Orquidário das flores de carne", "orquidario"),
    ("Pavilhão das gaiolas enferrujadas", "vidraca"),
    ("Vidraça das raízes sem terra", "vidraca"),
    ("Orquidário do último verão", "orquidario"),
    ("Galeria das folhagens que se lembram de você", "vidraca"),
    ("Vidraça das sementes cantantes", "vidraca"),
    ("Orquidário dos suspiros", "orquidario"),
    ("Pavilhão do coração de vidro", "vidraca"),
]

ORQUIDARIO_TEXTOS = [
    # texto-base de um orquidário: sempre orquídeas raras, que um colecionador
    # compra por 1d10 x profundidade de prata (`generate_orquidario_conteudo`).
    "Fileiras de orquídeas raras em vasos de musgo, cada uma com a etiqueta de um colecionador.",
    "Orquídeas penduradas em cestos de arame, as raízes brancas balançando no ar morno.",
    "Mesas de orquídeas em floração, de cores que não existem lá fora.",
    "Uma coleção de orquídeas minúsculas sob campânulas de vidro, cada uma num pires.",
]

DETALHES = [
    # Os 35 detalhes, na ordem da tabela do livro (d20 + profundidade).
    # (texto, tipo_relevo, efeito) — o texto é meu, a mecânica é a do livro.
    # `tipo_relevo` ("plano", "leve", "acentuado" ou "irregular") dita o quanto o
    # terreno ao redor varia (`ynn.terrain.generate_terrain_localizado`).
    # `efeito` é uma etiqueta que o gerador lê: "vazio", "tesouro",
    # "bem_cuidado" (o único jeito de um lugar estar inteiro; nos demais, jaz em
    # ruínas), "hera" (tudo coberto de hera, estruturas preservadas), "alagado",
    # "queimado", "congelado", "vidro" (o lugar inteiro sob uma estufa gigante),
    # "fertil", "luminoso", "saida" (porta de volta ao mundo real) etc.
    ("Quietude fora do comum: nada canta, nada zumbe, e qualquer encontro que viria simplesmente não vem.", "plano", "vazio"),
    ("Um montinho de moedas e bugigangas brilha no meio do gramado: 5d10 de prata e dois sorteios de tesouro.", "plano", "tesouro"),
    ("Exploradores do mundo real rabiscaram uma parede: o perigo e o valor do lugar estão apontados ali, e três mãos deixaram outros recados.", "plano", "grafite"),
    ("Aqui, ao contrário do resto do jardim, tudo está conservado: metal sem ferrugem, grama aparada, flores em fileiras retas.", "plano", "bem_cuidado"),
    ("Jazem aqui 1d6 exploradores, em estados diferentes de decomposição, cada um com o equipamento do seu ofício.", "plano", "exploradores_mortos"),
    ("Ninhos nos cantos mais altos: ovos, filhotes piando e pais que defendem a prole.", "plano", "ninhos"),
    ("Algo ronca debaixo da terra: o chão vibra em intervalos e as construções estremecem.", "acentuado", "estrondo"),
    ("Um poste de ferro forjado acende toda noite sozinho, iluminando o centro do lugar.", "plano", "poste"),
    ("Volutas de prata nascem entre as plantas, vida mineral que brota das veias da terra: valem 100 de prata por profundidade, se arrancadas.", "plano", "filigrana"),
    ("Tubos escuros serpenteiam entre as plantas, levando um fluido iridescente: na pele exige Resistência a Magia, bebido causa Alteração de Ynn sem teste.", "leve", "tubos"),
    ("Vigas de aço enormes saem do chão, retorcidas como o esqueleto de uma torre que ninguém terminou.", "leve", "armacoes"),
    ("O chão está coberto de pássaros coloridos mortos, as penas quebradas, como se tivessem caído do céu de uma vez.", "plano", "passaros_mortos"),
    ("Há água parada, de joelho à cintura, com plantas e construções emergindo e algas na linha d'água: o movimento cai pela metade.", "plano", "alagado"),
    ("Houve um incêndio: cinza no chão, árvores chamuscadas, estruturas frágeis, com 1 em 6 de desabarem na pior hora.", "plano", "queimado"),
    ("Geada cobre tudo e a água tem gelo grosso; quem se demora sem abrigo ou fogo sofre 1 de dano por turno.", "plano", "congelado"),
    ("Hera cobre absolutamente tudo numa manta emaranhada que suaviza as silhuetas; por baixo, as estruturas estão intactas.", "plano", "hera"),
    ("Uma música baixa vem de tubos de ouro escondidos na folhagem: cada turno ouvindo concede uma pergunta ao Mestre.", "plano", "cantante"),
    ("O lugar inteiro fica dentro de uma estufa gigante, mais quente e abafada, protegida do tempo; 1 em 3 encontros é com os moradores da estufa.", "plano", "vidro"),
    ("Esqueletos de 1d4 sidhe, de alabastro perfeito e simétrico: cada osso vale cerca de 10 de ouro a um colecionador, e são 250.", "plano", "esqueletos_sidhe"),
    ("As construções têm relógios embutidos: engrenagens girando devagar, um tique-taque polirrítmico constante.", "plano", "relojoaria"),
    ("O lugar está de cabeça para baixo, crescendo do teto sobre um abismo sem fundo: cair é um caminho sem volta.", "irregular", "invertido"),
    ("Ilhas de grama e concreto pairam imóveis sobre o abismo, sem pontes entre elas.", "irregular", "flutuante"),
    ("Fendas profundas cortam o lugar em seções, abertas para o nada nebuloso; dá pra pular, se nada der errado.", "irregular", "abismos"),
    ("Ainda há fogo baixo dançando nas superfícies carbonizadas: o ar quente e a fumaça dão 1 de dano por turno.", "plano", "fumegante"),
    ("O chão se move como o convés de um navio, abrindo e fechando a relva; árvores e construções balançam.", "acentuado", "convulso"),
    ("O solo quer comer você: bocas de barro com dentes de marfim se abrem aos pés de quem faz barulho.", "plano", "predador"),
    ("As plantas aqui são de carne, osso e cartilagem; comer qualquer coisa exige rolar Alteração de Ynn.", "plano", "carnudo"),
    ("Um campo mental suave faz o lugar parecer um lar: cada turno cura 1 ponto, mas sair desfaz a cura e custa 1d10 de Carisma.", "plano", "enfeiticante"),
    ("Tudo cresce com força e a vegetação é densa e lustrosa; cada turno aqui cura 1 ponto de dano.", "leve", "fertil"),
    ("As plantas brilham: pétalas e brotos soltam luz suave e nunca fica totalmente escuro.", "plano", "luminoso"),
    ("A gravidade quase não existe: pedras caem devagar e dá pra saltar distâncias enormes.", "plano", "gravidade_zero"),
    ("Ao entrar, as passagens se fecham atrás de você numa realidade-bolha; só se sai desmaiando e acordando do outro lado.", "plano", "hipnotico"),
    ("O lugar está infestado de parasitas: comer, beber, dormir ou se ferir aqui exige Resistência a Veneno.", "plano", "parasitado"),
    ("Numa cerca, uma portinha entreaberta com letras de giz: leva de volta ao mundo real.", "plano", "saida"),
    ("Aqui fora a realidade perde a consistência: causas se embaralham, distâncias e ângulos se deformam.", "irregular", "loucura"),
]

TORRE_BROTO = [
    # (texto, especie, bandas) — o que brotou no topo de uma torre destelhada
    # (`ynn.generator.sortear_extras_torre`); `especie` é de `gielis.plants`.
    ("Uma árvore antiga criou raízes no topo e abriu o que restava do telhado com o tronco.", "arvore", "all"),
    ("Um mato espesso de arbustos tomou o topo, o telhado caído há muito tempo.", "arbusto", "all"),
    ("Um canteiro selvagem de flores brotou no assoalho do topo, aberto ao céu.", "flor", "all"),
    ("Samambaias gigantes pendem das bordas do topo destelhado.", "samambaia", ("jardim_profundo", "nucleo_selvagem")),
    ("Cogumelos enormes cresceram no assoalho apodrecido do topo.", "cogumelo", ("nucleo_selvagem",)),
]
