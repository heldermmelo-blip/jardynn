"""Funções-R de Rvachev: tradução geométrica de operações booleanas
(conjunção/interseção, disjunção/união) usadas para compor supershapes com
diferenciabilidade garantida.

Referência: Cap. 6, seções "R-Functions and Supershapes" (Eqs. 6.6-6.14).
As formas com o sinal +/- explícito seguem a teoria padrão de R-functions de
Rvachev/Shapiro (o mesmo formalismo citado pelo livro), usada aqui para
resolver a ambiguidade de sinal perdida na extração de texto do PDF.
"""

import numpy as np


def r_alpha(s1, s2, alpha, disjunction=True):
    """Eq. 6.6 — função-R geral R_alpha(s1, s2), com -1 < alpha < 1.

    R_alpha(s1, s2) = (1/(1+alpha)) * [ (s1+s2) +/- sqrt(s1^2+s2^2-2*alpha*s1*s2) ]

    `disjunction=True` (sinal +) corresponde à união A ∪ B; `False` (sinal -)
    à interseção A ∩ B.
    """
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    if not (-1.0 < alpha < 1.0):
        raise ValueError("alpha deve satisfazer -1 < alpha < 1 (Eq. 6.6)")
    root = np.sqrt(s1**2 + s2**2 - 2 * alpha * s1 * s2)
    sign = 1.0 if disjunction else -1.0
    return ((s1 + s2) + sign * root) / (1.0 + alpha)


def r1_max(s1, s2):
    """Eq. 6.7, alpha=1: R_1 disjunção reduz a max(s1, s2)."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return 0.5 * ((s1 + s2) + np.abs(s1 - s2))


def r1_min(s1, s2):
    """Eq. 6.7, alpha=1: R_1 conjunção reduz a min(s1, s2)."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return 0.5 * ((s1 + s2) - np.abs(s1 - s2))


def r0_disjunction(s1, s2):
    """Eq. 6.9, alpha=0: R_0 união/disjunção. s1 + s2 + sqrt(s1^2+s2^2)."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return (s1 + s2) + np.sqrt(s1**2 + s2**2)


def r0_conjunction(s1, s2):
    """Eq. 6.8, alpha=0: R_0 interseção/conjunção. s1 + s2 - sqrt(s1^2+s2^2)."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return (s1 + s2) - np.sqrt(s1**2 + s2**2)


def rm_disjunction(s1, s2, m):
    """Eq. 6.10 — sistema R^m: união com diferenciabilidade garantida até
    ordem m. Rm_0(s1,s2) = [ (s1+s2) + sqrt(s1^2+s2^2) ] * (s1^2+s2^2)^(m/2)."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return ((s1 + s2) + np.sqrt(s1**2 + s2**2)) * (s1**2 + s2**2) ** (m / 2.0)


def rm_conjunction(s1, s2, m):
    """Eq. 6.10 — sistema R^m, versão de interseção/conjunção."""
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return ((s1 + s2) - np.sqrt(s1**2 + s2**2)) * (s1**2 + s2**2) ** (m / 2.0)


def rp_disjunction(s1, s2, p):
    """Eq. 6.11 — sistema R_p, disjunção/união:

    Rp(s1 ∨ s2) = (s1+s2) + (|s1|^p + |s2|^p)^(1/p)
    """
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return (s1 + s2) + (np.abs(s1) ** p + np.abs(s2) ** p) ** (1.0 / p)


def rp_conjunction(s1, s2, p):
    """Eq. 6.12 — sistema R_p, conjunção/interseção:

    Rp(s1 ∧ s2) = (s1+s2) - (|s1|^p + |s2|^p)^(1/p)
    """
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return (s1 + s2) - (np.abs(s1) ** p + np.abs(s2) ** p) ** (1.0 / p)


def rp_equivalence(s1, s2, p):
    """Eq. 6.13 — sistema R_p, equivalência:

    Rp(s1 <-> s2) = (s1*s2) / (|s1|^p + |s2|^p)^(1/p)
    """
    s1, s2 = np.asarray(s1, dtype=float), np.asarray(s2, dtype=float)
    return (s1 * s2) / (np.abs(s1) ** p + np.abs(s2) ** p) ** (1.0 / p)


def rp_partial_derivative(x1, x2, p, wrt="x1", disjunction=True):
    """Eq. 6.14 — derivada parcial no sistema R_p em relação a x1 ou x2:

    df/dxi = 1 +/- sign(xi)*|xi|^(p-1) / (|x1|^p + |x2|^p)^((p-1)/p)

    `disjunction=True` usa o sinal + (união), `False` usa o sinal - (interseção).
    Usa sign(xi)*|xi|^(p-1) em vez de xi^(p-1) "cru" para que a expressão
    fique bem definida também para xi negativo e p não inteiro (o livro
    assume implicitamente xi como uma quantidade não negativa).
    """
    x1, x2 = np.asarray(x1, dtype=float), np.asarray(x2, dtype=float)
    xi = x1 if wrt == "x1" else x2
    sign = 1.0 if disjunction else -1.0
    xi_term = np.sign(xi) * np.abs(xi) ** (p - 1)
    return 1.0 + sign * xi_term / (np.abs(x1) ** p + np.abs(x2) ** p) ** ((p - 1) / p)
