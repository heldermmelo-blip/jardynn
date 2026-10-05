"""Criaturas de Ynn: bestiário original para os denizens não-humanoides do
gerador de camadas.

Formato de ficha ("monstro" clássico do gênero OSR — CA, Dados de Vida,
ataques, Moral) é mecânica genérica do gênero, não uma transcrição de
nenhum bestiário específico. Nomes, valores e habilidades especiais são
originais, pensados para o tom de *The Gardens of Ynn*.
"""

import re

_DICE_RE = re.compile(r"(\d+)d(\d+)([+-]\d+)?")


def roll_dice(rng, notation):
    """Rola uma notação de dado tipo `"2d6+1"` e retorna o total."""
    match = _DICE_RE.fullmatch(notation.strip())
    if not match:
        raise ValueError(f"notação de dado inválida: {notation!r}")
    n, sides, bonus = match.groups()
    total = sum(rng.randint(1, int(sides)) for _ in range(int(n)))
    return total + (int(bonus) if bonus else 0)


CREATURES = {
    "passaros_brancos": {
        "nome": "Bando de Pássaros Brancos",
        "ca": 13,
        "dv": "1d4",
        "movimento": "curto no chão, voo errático",
        "ataques": [("bicadas em enxame", "1d2")],
        "resistencia": 15,
        "moral": 6,
        "especial": (
            "Não recuam de verdade — se dispersam e voltam a pousar juntos a poucos "
            "metros de distância, observando de novo."
        ),
    },
    "mariposas_gigantes": {
        "nome": "Enxame de Mariposas Gigantes",
        "ca": 12,
        "dv": "2d6",
        "movimento": "voo lento e silencioso",
        "ataques": [("pó das asas (ofusca)", "1d3")],
        "resistencia": 14,
        "moral": 5,
        "especial": "O pó das asas pode ofuscar temporariamente quem for atingido de perto.",
    },
    "luvas_animadas": {
        "nome": "Par de Luvas Animadas",
        "ca": 14,
        "dv": "1d6",
        "movimento": "rastejante, rápido em curtas distâncias",
        "ataques": [("estrangulamento", "1d4")],
        "resistencia": 13,
        "moral": 9,
        "especial": "Preferem agarrar o pescoço por trás; soltam-se se atingidas duas vezes seguidas.",
    },
    "cervo_de_galhos": {
        "nome": "Cervo de Galhos Excessivos",
        "ca": 12,
        "dv": "3d8",
        "movimento": "normal, surpreendentemente ágil para o tamanho",
        "ataques": [("chifrada", "1d8"), ("coice", "1d6")],
        "resistencia": 12,
        "moral": 7,
        "especial": "Os galhos em excesso se movem por conta própria, prendendo armas e roupas em combate corpo a corpo.",
    },
    "algo_sob_a_grama": {
        "nome": "Algo Sob a Grama",
        "ca": 15,
        "dv": "4d8",
        "movimento": "lento na superfície, rápido logo abaixo dela",
        "ataques": [("puxão surpresa", "2d6")],
        "resistencia": 13,
        "moral": 8,
        "especial": (
            "Nunca é visto diretamente — só o movimento da grama sobre ele. Ataca e "
            "volta a submergir no mesmo turno."
        ),
    },
    "gato_sem_rosto": {
        "nome": "Gato Preto Sem Rosto",
        "ca": 15,
        "dv": "2d4",
        "movimento": "rápido e silencioso",
        "ataques": [("arranhão", "1d3")],
        "resistencia": 14,
        "moral": 4,
        "especial": (
            "Some de vista com facilidade; reaparece andando em círculos ao redor do "
            "mesmo ponto, como se nada tivesse acontecido."
        ),
    },
    "estatua_errante": {
        "nome": "Estátua Errante",
        "ca": 16,
        "dv": "5d8",
        "movimento": "muito lento; só se move quando não observada",
        "ataques": [("golpe de pedra", "2d8")],
        "resistencia": 16,
        "moral": 12,
        "especial": "Fica imóvel enquanto observada diretamente por qualquer personagem; só avança quando todos desviam o olhar.",
    },
    "topiaria_ambulante": {
        "nome": "Topiária Ambulante",
        "ca": 14,
        "dv": "3d8",
        "movimento": "lento, mas constante",
        "ataques": [("chicotada de galhos", "1d6")],
        "resistencia": 13,
        "moral": 10,
        "especial": "Perde galhos a cada acerto sofrido; se não for destruída, eles crescem de volta por completo até o fim do dia.",
    },
    "jogo_de_xadrez_animado": {
        "nome": "Jogo de Xadrez Animado",
        "ca": 12,
        "dv": "2d6",
        "movimento": "lento, sempre em formação",
        "ataques": [("investida de peões", "1d4"), ("golpe de torre", "1d8")],
        "resistencia": 14,
        "moral": 8,
        "especial": "Ataca com d4 peças por rodada; rei e rainha só entram em combate depois que todas as outras peças caírem.",
    },
    "podadeira_mecanica": {
        "nome": "Podadeira Mecânica",
        "ca": 15,
        "dv": "2d8",
        "movimento": "rápido em linha reta; não consegue virar sozinha",
        "ataques": [("lâminas giratórias", "2d4")],
        "resistencia": 14,
        "moral": 11,
        "especial": "Move-se e ataca apenas em linha reta, mudando de direção só ao colidir com algo sólido.",
    },
    "serva_de_porcelana": {
        "nome": "Serva de Porcelana",
        "ca": 13,
        "dv": "1d8",
        "movimento": "normal, passos silenciosos",
        "ataques": [("bandeja na cabeça", "1d4")],
        "resistencia": 15,
        "moral": 6,
        "especial": "Racha em vez de sangrar; ao cair a 0 PV, estilhaça-se, causando 1d4 a quem estiver adjacente.",
    },
    "jarro_carnivoro": {
        "nome": "Jarro Carnívoro",
        "ca": 13,
        "dv": "3d8",
        "movimento": "nenhum — enraizado no lugar",
        "ataques": [("bote de gavinhas", "1d6"), ("jato de suco ácido", "1d4")],
        "resistencia": 12,
        "moral": 12,
        "especial": "Não sai do lugar, mas ataca tudo ao alcance das gavinhas. Imune a veneno e a qualquer efeito que dependa de ver ou ouvir.",
    },
    "esqueleto_vegetal": {
        "nome": "Esqueleto Vegetal",
        "ca": 12,
        "dv": "1d8",
        "movimento": "normal, com estalos de galhos secos",
        "ataques": [("garras de raiz", "1d6")],
        "resistencia": 14,
        "moral": 12,
        "especial": "Morto-vivo atravessado por trepadeiras. Ao ser destruído, as trepadeiras tentam religar os ossos: role 1d6 por rodada, e com 6 ele volta a lutar com 1 PV.",
    },
    "noiva_de_espinhos": {
        "nome": "Noiva de Espinhos",
        "ca": 13,
        "dv": "3d8",
        "movimento": "normal, andar deliberadamente lento",
        "ataques": [("abraço de espinhos", "2d6")],
        "resistencia": 12,
        "moral": 9,
        "especial": "Quem se aproxima para conversar e falha em resistir ao seu convite fica hipnotizado, parado, até sofrer dano.",
    },
}


def instantiate_creature(rng, creature_key):
    """Retorna uma cópia da ficha de `creature_key` com os pontos de vida
    já rolados a partir de `dv`."""
    template = CREATURES[creature_key]
    creature = dict(template)
    creature["pontos_de_vida"] = max(1, roll_dice(rng, template["dv"]))
    return creature
