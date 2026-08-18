"""A Superfórmula de Gielis e suas generalizações (transformações de Gielis).

Referência: Cap. 5 "Gielis Curves, Surfaces and Transformations"
(Eqs. 5.7-5.9, 5.12) e Cap. 6 "Pythagorean-Compact" (Eqs. 6.2, 6.3).
"""

import numpy as np


def superformula(theta, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 5.8 — a Superfórmula (Gielis Superformula, GSF).

    rho(theta) = [ |cos(m*theta/4)/A|^n2 + |sin(m*theta/4)/B|^n3 ]^(-1/n1)

    Parâmetros
    ----------
    theta : escalar ou array, ângulo polar em radianos
    m : parâmetro de simetria rotacional (real; inteiro dá m pontas/vértices)
    A, B : semi-eixos (reais positivos)
    n1, n2, n3 : expoentes de forma (reais; n1 > 0)
    """
    theta = np.asarray(theta, dtype=float)
    term1 = np.abs(np.cos(m * theta / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m * theta / 4.0) / B) ** n3
    return (term1 + term2) ** (-1.0 / n1)


def superformula_asymmetric(theta, m1, m2, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0, sign=1.0):
    """Eq. 5.9 — variante com simetrias independentes m1 (cosseno) e m2 (seno).

    rho(theta) = [ |cos(m1*theta/4)/A|^n2 + sign*|sin(m2*theta/4)/B|^n3 ]^(-1/n1)

    `sign=-1` produz curvas de métrica indefinida (tipo hipérbole), como
    descrito no livro para A=B=1, n1=n2=n3=2 partindo de x^2 - y^2 = 1.
    """
    theta = np.asarray(theta, dtype=float)
    term1 = np.abs(np.cos(m1 * theta / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m2 * theta / 4.0) / B) ** n3
    return (term1 + sign * term2) ** (-1.0 / n1)


def to_cartesian(theta, rho):
    """Converte (theta, rho(theta)) em coordenadas cartesianas (x, y)."""
    theta, rho = np.asarray(theta, dtype=float), np.asarray(rho, dtype=float)
    return rho * np.cos(theta), rho * np.sin(theta)


def gielis_transform(theta, f, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 5.12 — Transformação de Gielis de uma função radial arbitrária.

    Em vez de transformar apenas o círculo unitário (Eq. 5.8), transforma
    qualquer função radial positiva f(theta):

        rho(theta) = f(theta) / [ |cos(m*theta/4)/A|^n2 + |sin(m*theta/4)/B|^n3 ]^(1/n1)

    `f` pode ser um array já avaliado em `theta`, ou uma função chamável
    `f(theta) -> array`. Casos notáveis do livro: f(theta)=R constante
    (círculo/supercírculo), f(theta)=a*theta (espiral de Arquimedes),
    f(theta)=exp(k*theta) (espiral logarítmica, ver Eqs. 9.20-9.21).
    """
    theta = np.asarray(theta, dtype=float)
    f_values = f(theta) if callable(f) else np.asarray(f, dtype=float)
    term1 = np.abs(np.cos(m * theta / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m * theta / 4.0) / B) ** n3
    return f_values / (term1 + term2) ** (1.0 / n1)


def transform_circle(theta, R, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 9.20 — transformação de Gielis aplicada a um círculo de raio R."""
    return gielis_transform(theta, np.full_like(np.asarray(theta, dtype=float), R), m, A, B, n1, n2, n3)


def transform_logarithmic_spiral(theta, k, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 9.21 — transformação de Gielis aplicada à espiral logarítmica r=e^(k*theta)."""
    theta = np.asarray(theta, dtype=float)
    return gielis_transform(theta, np.exp(k * theta), m, A, B, n1, n2, n3)


def transform_archimedean_spiral(theta, a, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Transformação de Gielis aplicada à espiral de Arquimedes r=a*theta (Cap. 5,
    seção "Gielis Transformations")."""
    theta = np.asarray(theta, dtype=float)
    return gielis_transform(theta, a * theta, m, A, B, n1, n2, n3)


def gielis_transform_phase_shifted(theta, f, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0, epsilon=0.0):
    """Eq. 6.2 — Transformação de Gielis com deslocamento de fase `epsilon`.

    rho(theta) = f(theta) / [ |cos(m*(theta+eps)/4)/A|^n2 + |sin(m*(theta+eps)/4)/B|^n3 ]^(1/n1)
    """
    theta = np.asarray(theta, dtype=float)
    shifted = theta + epsilon
    f_values = f(theta) if callable(f) else np.asarray(f, dtype=float)
    term1 = np.abs(np.cos(m * shifted / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m * shifted / 4.0) / B) ** n3
    return f_values / (term1 + term2) ** (1.0 / n1)


def gielis_generalized(theta, f1, f2, c=None, m1=4.0, m2=4.0, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0):
    """Eq. 6.3 — generalização com funções arbitrárias f1(theta), f2(theta) no
    lugar do ângulo puro, e um modulador c(theta) multiplicando o resultado.

    rho(theta) = c(theta) * [ |cos(m1*f1(theta)/4)/A|^n2 + |sin(m2*f2(theta)/4)/B|^n3 ]^(-1/n1)

    `f1`, `f2`, `c` podem ser arrays pré-avaliados ou funções chamáveis;
    `c=None` equivale a c(theta)=1 para todo theta.
    """
    theta = np.asarray(theta, dtype=float)
    f1_values = f1(theta) if callable(f1) else np.asarray(f1, dtype=float)
    f2_values = f2(theta) if callable(f2) else np.asarray(f2, dtype=float)
    c_values = 1.0 if c is None else (c(theta) if callable(c) else np.asarray(c, dtype=float))
    term1 = np.abs(np.cos(m1 * f1_values / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m2 * f2_values / 4.0) / B) ** n3
    return c_values * (term1 + term2) ** (-1.0 / n1)
