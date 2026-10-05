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
para os andares normais, `TORRE_TOPO` só para o último. Cada entrada tem
um terceiro campo, `tipo`: `"tesouro"` (sorteia de `TREASURE`),
`"encontro"` (sorteia um denizen de `DENIZENS`) ou `None` (só atmosfera).

`ESTUFA_CONTEUDO` tem uma entrada sorteada por estufa
(`ynn.generator.generate_estufa_conteudo`), com formato `(texto, bandas,
tipo, criatura)`: `tipo` é `"valor"` (rola um valor em ouro, crescente com
a profundidade), `"criatura"` (instancia a ficha `criatura` de
`ynn.creatures.CREATURES`) ou `None` (só atmosfera/regra no próprio texto).

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
    ("Um campo de tulipas em cores que não deveriam existir juntas.", "all", "flor"),
    (
        "Cercas-vivas aparadas em formas que quase lembram animais, e que parecem ter se movido "
        "desde a última vez que alguém olhou.",
        ("jardim_profundo", "nucleo_selvagem"),
        "arbusto",
    ),
    (
        "Fileiras de girassóis voltados para um sol que não está no céu.",
        ("jardim_profundo", "nucleo_selvagem"),
        "flor",
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
    # (texto, bandas, tipo) — tipo em "tesouro", "encontro" ou None.
    ("O andar está vazio, só poeira e silêncio.", "all", None),
    ("Um pequeno tesouro foi deixado para trás aqui, esquecido entre os destroços.", "all", "tesouro"),
    ("Algo vive neste andar e reage à presença de quem entra.", "all", "encontro"),
    ("Móveis apodrecidos se desfazem ao toque — uma cadeira, uma mesa, os restos de uma cama.", "all", None),
    ("Uma estante de livros embolorados ainda de pé; a maioria das páginas grudou umas nas outras.", "all", None),
    ("Ninhos de pássaros nos cantos mais altos, ovos e filhotes piando sem parar.", "all", None),
    ("Teias de aranha grossas dificultam a visão e o movimento por aqui.", ("jardim_profundo", "nucleo_selvagem"), None),
    ("Um esqueleto preso à parede por correntes enferrujadas há muito tempo.", ("jardim_profundo", "nucleo_selvagem"), None),
    ("Rações perfeitamente conservadas, o suficiente para alimentar um grupo grande por dias.", "all", None),
    ("Retratos emoldurados de rostos alienígenamente belos cobrem a parede.", ("jardim_profundo", "nucleo_selvagem"), "tesouro"),
    ("Um espelho de corpo inteiro que reflete tudo, menos quem está olhando para ele.", ("nucleo_selvagem",), None),
]

TORRE_TOPO = [
    # Mesmo formato de TORRE_ANDARES, mas só pro último andar — conteúdo
    # mais raro/significativo, reservado pro topo da torre.
    ("Um sino enorme de bronze, silencioso, pendurado bem no centro do andar.", "all", None),
    ("Um telescópio antigo, apontado para um trecho do céu que não parece bater com o de baixo.", "all", None),
    ("Uma câmera escura projeta, invertida, uma imagem do jardim lá fora numa parede caiada.", "all", None),
    ("Um tesouro bem maior que o normal está escondido aqui.", "all", "tesouro"),
    ("Uma biblioteca arcana, prateleiras cheias de livros sobre magias que ninguém mais lembra de estudar.", ("jardim_profundo", "nucleo_selvagem"), None),
    ("Algo poderoso e perigoso vive neste andar — o mais alto de todos.", ("jardim_profundo", "nucleo_selvagem"), "encontro"),
    ("Uma armadilha está escondida no assoalho, pronta pra disparar no primeiro passo em falso.", "all", None),
    ("Uma armadura completa, de aparência amaldiçoada, montada num pedestal, esperando um dono.", ("nucleo_selvagem",), None),
    ("Uma máquina voadora incompleta, engrenagens e lona espalhadas pelo chão em volta dela.", "all", None),
    ("Um espelho gigante, usado pra mandar sinais refletindo luz a longa distância.", "all", None),
    ("Um caixão de vidro guarda um corpo perfeitamente preservado, como se dormisse.", ("nucleo_selvagem",), None),
    ("Uma lâmpada enorme, alimentada por algo vivo e luminoso preso dentro dela, ilumina tudo ao redor.", "all", None),
]

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
    # (texto, bandas, tipo, criatura) — tipo em "valor", "criatura" ou None.
    ("Vasos de plantas raras, cada um com uma plaqueta de colecionador escrita em latim.", "all", "valor", None),
    ("Nada de notável: só vasos vazios e terra seca rachada.", "all", None, None),
    ("Ervas medicinais crescem entre os vasos — 1d4+1 doses, e cada dose cura 1 PV.", "all", None, None),
    ("Frutos graúdos e maduros pendem dos galhos, seguros de comer.", "all", None, None),
    ("Flores lindas e venenosas: comer ou se espetar nelas causa 1d8 de dano (1d4 doses colhíveis).", "all", None, None),
    ("Mesas e cadeiras de ferro, enferrujadas e cobertas de musgo, postas como para um chá abandonado.", "all", None, None),
    ("Nenhuma planta: prateleiras vazias e vidro limpo demais pra um lugar abandonado.", "all", None, None),
    ("Gaiolas ornamentais de ouro penduradas do teto, vazias, ainda balançando de leve.", "all", "valor", None),
    ("Um jarro carnívoro enorme, enraizado perto da porta, abre a boca na direção de quem entra.", ("jardim_profundo", "nucleo_selvagem"), "criatura", "jarro_carnivoro"),
    ("Limo verde digestivo cobre o teto; qualquer barulho súbito faz pingar gotas que queimam (1d6).", ("jardim_profundo", "nucleo_selvagem"), None, None),
    ("Esporos densos no ar: respirar causa 1 de dano por turno, e quem falhar numa resistência a veneno continua sofrendo ao sair.", ("jardim_profundo", "nucleo_selvagem"), None, None),
    ("Sob a folhagem, esqueletos humanos com trepadeiras saindo das costelas se levantam quando alguém se aproxima.", ("jardim_profundo", "nucleo_selvagem"), "criatura", "esqueleto_vegetal"),
    ("A estufa está lacrada por fora, as portas pregadas; lá dentro, a folhagem empurra o vidro tentando sair.", ("nucleo_selvagem",), None, None),
]
