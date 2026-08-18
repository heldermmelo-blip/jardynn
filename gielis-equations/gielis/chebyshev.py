"""Polinômios de Chebyshev e a reescrita da Superfórmula em termos deles.

Referência: Cap. 7, seção "Orthogonial Polynomials and Phyllotaxy in Plants"
(Eqs. 7.16-7.18, 7.22).
"""

import numpy as np


def chebyshev_t(m, x):
    """Eq. 7.16 — polinômio de Chebyshev de 1a espécie: T_m(cos(theta)) = cos(m*theta).

    Implementado via T_m(x) = cos(m*arccos(x)), válido para x em [-1, 1].
    """
    x = np.asarray(x, dtype=float)
    return np.cos(m * np.arccos(np.clip(x, -1.0, 1.0)))


def chebyshev_u(m, x):
    """Eq. 7.17 — polinômio de Chebyshev de 2a espécie: U_m(cos(theta)) = sin((m+1)*theta)/sin(theta).

    Implementado via U_m(x) = sin((m+1)*arccos(x)) / sqrt(1-x^2), válido
    para x em (-1, 1) (em x=+-1 usa-se o limite U_m(1)=m+1, U_m(-1)=(m+1)*(-1)^m).
    """
    x = np.asarray(x, dtype=float)
    x_clipped = np.clip(x, -1.0, 1.0)
    theta = np.arccos(x_clipped)
    sin_theta = np.sin(theta)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.sin((m + 1) * theta) / sin_theta
    limit_value = (m + 1) * np.where(np.isclose(x_clipped, -1.0), (-1.0) ** m, 1.0)
    return np.where(np.isclose(sin_theta, 0.0), limit_value, result)


def gielis_chebyshev(x, m, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 7.18 / 7.22 — Superfórmula (Eq. 5.8, A=B=1) reescrita em termos de
    polinômios de Chebyshev, com x = cos(theta):

        rho(x) = 1 / [ |T_m(x)|^n2 + | sqrt(1-x^2) * U_(m-1)(x) |^n3 ]^(1/n1)

    Note que sqrt(1-x^2)*U_(m-1)(x) = sin(m*arccos(x)) = sin(m*theta), de
    modo que esta é matematicamente a mesma curva de `superformula.superformula`
    com m4=m (sem a divisão por 4) e A=B=1, apenas parametrizada por x em vez
    de theta. O valor absoluto no segundo termo (não totalmente legível na
    extração do PDF) segue a mesma convenção do resto do livro, garantindo
    que a expressão fique bem definida para n3 não inteiro.
    """
    x = np.asarray(x, dtype=float)
    t_term = np.abs(chebyshev_t(m, x)) ** n2
    u_term = np.abs(np.sqrt(1 - np.clip(x, -1.0, 1.0) ** 2) * chebyshev_u(m - 1, x)) ** n3
    return (t_term + u_term) ** (-1.0 / n1)
