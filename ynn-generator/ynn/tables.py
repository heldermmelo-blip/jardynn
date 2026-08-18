"""Tabelas de conteúdo para o gerador de camadas de jardim.

Cada entrada é `(texto, bandas)`, onde `bandas` é `"all"` (aparece em
qualquer camada) ou uma tupla com as bandas em que pode aparecer:
`"jardim_externo"` (camadas 1-2), `"jardim_profundo"` (camadas 3-4) ou
`"nucleo_selvagem"` (camada 5+).

`DENIZENS` tem um terceiro campo, `classe`: `None` para encontros sem
estatísticas (a maioria — animais, objetos, fenômenos), ou a chave de uma
classe de `lotfp-rules` (`"fighter"`, `"specialist"`, `"magic_user"`,
`"cleric"`) para os poucos denizens humanoides que viram um NPC jogável
completo.

`VEGETATION` também tem um terceiro campo, `especie`: `None` para
vegetação de cobertura (gramado, musgo, líquens — sem uma "planta" única
para gerar) ou a chave de uma espécie de `gielis.plants` (`"arvore"`,
`"arbusto"`, `"espinheiro"`, `"bambu"`, `"videira"`, `"flor"`,
`"cogumelo"`, `"samambaia"`), que vira uma malha 3D (.obj) real da planta
dominante daquela área.

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
]

DENIZENS = [
    # (texto, bandas, classe LotFP se for um NPC humanoide jogável — ver lotfp-rules)
    (
        "um jardineiro curvado sobre um canteiro, que não ergue os olhos quando questionado, "
        "apenas continua podando algo que já não tem folhas",
        "all",
        "specialist",
    ),
    ("um bando de pássaros brancos, silenciosos, que pousam todos ao mesmo tempo e observam", "all", None),
    ("uma estátua que os personagens têm certeza de já ter visto em outra pose", "all", None),
    ("um enxame de mariposas do tamanho de mãos, pousando em qualquer luz disponível", "all", None),
    (
        "um par de luvas de jardinagem, sozinhas sobre um banco, ainda com o formato de mãos dentro delas",
        "all",
        None,
    ),
    (
        "um cervo de galhada excessiva, mais galhos do que deveria ser fisicamente possível, parado imóvel",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
    ),
    (
        "uma criança rindo em algum lugar próximo, embora nenhuma criança seja encontrada",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
    ),
    (
        "algo grande se movendo logo abaixo da superfície de um gramado bem cuidado demais",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
    ),
    (
        "uma voz educada vinda de trás de uma cerca-viva, convidando para chá em algum lugar que não existe no mapa",
        ("jardim_externo", "jardim_profundo"),
        None,
    ),
    ("um gato preto sem rosto que anda em círculos perfeitos ao redor de um ponto fixo", ("nucleo_selvagem",), None),
    (
        "um grupo de estátuas de jardim reorganizadas em uma formação que parece deliberada",
        ("jardim_profundo", "nucleo_selvagem"),
        None,
    ),
    ("um som de tesoura de poda, rítmico, vindo de todas as direções ao mesmo tempo", ("nucleo_selvagem",), None),
    (
        "um viajante exausto, sentado à sombra de uma cerca-viva, que jura estar aqui há poucos minutos",
        ("jardim_externo", "jardim_profundo"),
        "fighter",
    ),
    (
        "uma clériga solitária de véu rasgado, murmurando orações para uma estátua que não é de nenhum deus conhecido",
        ("jardim_profundo", "nucleo_selvagem"),
        "cleric",
    ),
    (
        "um estudioso de olhos vidrados, anotando compulsivamente em um caderno encharcado que nunca seca",
        ("jardim_profundo", "nucleo_selvagem"),
        "magic_user",
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
]

ATMOSPHERE = [
    ("O ar tem um leve gosto de metal.", "all"),
    ("Uma luz cinzenta e sem fonte clara ilumina tudo igualmente, sem sombras fortes.", ("jardim_profundo", "nucleo_selvagem")),
    ("Longe, algo soa como um sino, mas nenhum sino é visível.", "all"),
    ("O silêncio aqui pesa mais do que deveria.", ("jardim_profundo", "nucleo_selvagem")),
    ("Um vento fraco carrega um cheiro de terra recém-revirada.", "all"),
    ("A luz do dia parece mais fraca aqui do que no resto do jardim, sem que nada bloqueie o céu.", ("nucleo_selvagem",)),
]
