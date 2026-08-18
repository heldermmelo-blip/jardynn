"""Curvas de Lamé e a família generalizada de cônicas.

Referência: Cap. 4 "Lamé Curves and Surfaces" e início do Cap. 5
("Lamé Curves in Polar Coordinates") de *The Geometrical Beauty of Plants*.
"""

import numpy as np

from scipy import integrate


def superellipse_implicit(x, y, A=1.0, B=1.0, n=2.0):
    """Eq. 4.1 (Cap. 4): |x/A|^n + |y/B|^n.

    Vale 1 exatamente sobre a superelipse/supercírculo de Lamé.
    Para A=B a curva é um supercírculo; n=2 dá a elipse/círculo clássicos.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return np.abs(x / A) ** n + np.abs(y / B) ** n


def is_on_superellipse(x, y, A=1.0, B=1.0, n=2.0, tol=1e-9):
    """Testa se (x, y) satisfaz a Eq. 4.1 dentro de uma tolerância."""
    return np.abs(superellipse_implicit(x, y, A, B, n) - 1.0) < tol


# Família generalizada de cônicas de Lamé/Euzet (Eq. 4.2): |x/A|^n + |y/B|^n = 1
# sem valores absolutos, cada conica correspondendo a um expoente n distinto.
CONIC_EXPONENT_LINE = 1.0
CONIC_EXPONENT_HYPERBOLA = -1.0
CONIC_EXPONENT_ELLIPSE = 2.0
CONIC_EXPONENT_PARABOLA = 0.5


def line_conic(x, y, A=1.0, B=1.0):
    """Eq. 4.2, caso n=1: reta x/A + y/B = 1."""
    return x / A + y / B


def hyperbola_conic(x, y, A=1.0, B=1.0):
    """Eq. 4.2, caso n=-1: hipérbole A/x + B/y = 1 (x, y != 0)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return A / x + B / y


def ellipse_conic(x, y, A=1.0, B=1.0):
    """Eq. 4.2, caso n=2: elipse (x/A)^2 + (y/B)^2 = 1."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return (x / A) ** 2 + (y / B) ** 2


def parabola_conic(x, y, A=1.0, B=1.0):
    """Eq. 4.2, caso n=1/2: parábola sqrt(x/A) + sqrt(y/B) = 1 (x, y >= 0)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return np.sqrt(x / A) + np.sqrt(y / B)


def interscendent_curve(x, y, A=1.0, B=1.0):
    """Eq. 4.3: curva "interscendente" de Lamé/Euzet com expoente irracional.

    (x/A)^sqrt(2) + (y/B)^sqrt(2) = 1, definida para x, y >= 0.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return (x / A) ** np.sqrt(2) + (y / B) ** np.sqrt(2)


def lame_polar_radius(theta, A=1.0, B=1.0, n=2.0):
    """Eq. 5.1/5.2: raio polar da superelipse de Lamé.

    rho(theta) = 1 / (|cos(theta)/A|^n + |sin(theta)/B|^n)^(1/n)

    Caso particular da Superfórmula (gielis.superformula.superformula) com
    m=4, n1=n2=n3=n.
    """
    theta = np.asarray(theta, dtype=float)
    denom = np.abs(np.cos(theta) / A) ** n + np.abs(np.sin(theta) / B) ** n
    return denom ** (-1.0 / n)


def lame_cos(theta, n=2.0):
    """Eq. 5.4: cosseno de Lamé (ncos), generalização de cos sobre supercírculos."""
    theta = np.asarray(theta, dtype=float)
    norm = (np.abs(np.cos(theta)) ** n + np.abs(np.sin(theta)) ** n) ** (1.0 / n)
    return np.cos(theta) / norm


def lame_sin(theta, n=2.0):
    """Eq. 5.4: seno de Lamé (nsin), generalização de sin sobre supercírculos."""
    theta = np.asarray(theta, dtype=float)
    norm = (np.abs(np.cos(theta)) ** n + np.abs(np.sin(theta)) ** n) ** (1.0 / n)
    return np.sin(theta) / norm


def generalized_pythagorean_residual(theta, n=2.0):
    """Eq. 5.3: (ncos theta)^n + (nsin theta)^n, que vale identicamente 1.

    Útil como teste de consistência: deve retornar ~1 para qualquer theta e n.
    """
    return np.abs(lame_cos(theta, n)) ** n + np.abs(lame_sin(theta, n)) ** n


def lame_half_length(n=2.0, A=1.0, B=1.0, num_points=2000):
    """Comprimento de um quarto da curva de Lamé (o "p_n" mencionado no Cap. 5).

    Para n=2 (círculo), lame_half_length(2) == pi (o "p_2 = pi" citado no
    livro). Calculado por integração numérica do comprimento de arco entre
    theta=0 e theta=pi/2, dobrado (a curva completa tem 4 desses quartos e o
    livro define p_n como a meia-extensão, i.e. 2 quartos).
    """

    def integrand(theta):
        rho = lame_polar_radius(theta, A, B, n)
        d_theta = 1e-6
        d_rho = (
            lame_polar_radius(theta + d_theta, A, B, n)
            - lame_polar_radius(theta - d_theta, A, B, n)
        ) / (2 * d_theta)
        return np.sqrt(rho**2 + d_rho**2)

    quarter, _ = integrate.quad(integrand, 0.0, np.pi / 2, limit=num_points)
    return 2 * quarter
