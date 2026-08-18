"""Modelos aplicados do livro: forma de folhas de bambu e anéis de crescimento.

Referência: Cap. 10 "Bamboo Leaves and Tree Rings" (Eqs. 10.1-10.2).
"""

from .superformula import superformula


def bamboo_leaf_radius(theta, n, l=1.0):
    """Eq. 10.1 — modelo de 2 parâmetros para o contorno de folhas de bambu:

        rho(theta) = l / ( |cos(theta)|^n + |sin(theta)|^n )^(1/n)

    Caso extremamente simplificado da Superfórmula (A=B=1, m=4,
    n1=n2=n3=n): `n` é o único parâmetro de forma (no livro, tipicamente
    entre 0.02 e 0.1 para as 46 espécies de bambu estudadas) e `l` o
    parâmetro de tamanho. Equivale a
    `superformula(theta, m=4, n1=n, n2=n, n3=n) * l`.

    Aviso: o expoente interno da equação ficou ambíguo na extração de texto
    do PDF (poderia ser este `n` compartilhado, como implementado aqui, ou
    um expoente fixo "4" com `n` só no índice da raiz — ver EQUATIONS.md).
    Adotamos a leitura em que `n` aparece nos dois lugares por ser a
    redução mais direta e "de um parâmetro só" da Superfórmula geral, mas
    não foi possível confirmar contra a página original. Para os valores
    de n citados no livro (0.02-0.1), esta curva fica bastante extrema:
    perto de `l` nos ângulos 0° e 90°, e colapsando para muito perto de
    zero entre eles — ou seja, um único "lobo" (theta de 0 a 90 graus) tem
    dois picos com um vinco quase nulo no meio, não uma silhueta lisa de
    folha. Para gerar uma malha de folha utilizável (ex. um asset de jogo),
    veja `examples/rpg_plant.py`, que usa um perfil próprio em vez desta
    equação por esse motivo.
    """
    return l * superformula(theta, m=4.0, A=1.0, B=1.0, n1=n, n2=n, n3=n)


def tree_ring_radius(theta, n, a=1.0, b=1.0):
    """Eq. 10.2 — modelo de anéis de crescimento (superelipse de Lamé):

        rho(theta) = 1 / ( |cos(theta)/a|^n + |sin(theta)/b|^n )^(1/n)

    Caso da Superfórmula com m=4, todos os expoentes iguais a `n`, e
    semi-eixos `a`, `b` independentes. Equivale a
    `superformula(theta, m=4, A=a, B=b, n1=n, n2=n, n3=n)`.
    """
    return superformula(theta, m=4.0, A=a, B=b, n1=n, n2=n, n3=n)
