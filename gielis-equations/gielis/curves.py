"""Curvas clássicas de 1-termo citadas no livro (cardioide, Rhodonea/Grandi,
lemniscata, espirais) e a filotaxia de Fibonacci/ângulo áureo.

Referência: Cap. 5 (Eqs. 5.5-5.6, seção "Gielis Transformations"), Cap. 6
(seção "k-Type Curves..."), Cap. 7 (Eqs. 7.20-7.21) e Cap. 5
"Polygrams and Generic Symmetries" (razões de Fibonacci e ângulo áureo).
"""

import numpy as np

GOLDEN_RATIO = (1 + np.sqrt(5)) / 2


def cardioid(theta, sign=1.0, trig="cos"):
    """Cardioide, rho(theta) = 1 + sign*cos(theta) ou 1 + sign*sin(theta).

    Citada no Cap. 6 como exemplo de curva de 2 termos (círculo unitário +
    coordenada trigonométrica desse mesmo círculo); base para os modelos de
    folhas por transformação de Gielis (Fig. 6.5-6.6).
    """
    theta = np.asarray(theta, dtype=float)
    base = np.cos(theta) if trig == "cos" else np.sin(theta)
    return 1.0 + sign * base


def rose_curve(theta, m, a=1.0, trig="cos"):
    """Curva de Rhodonea / Grandi (Guido Grandi, 1713): rho(theta) = a*cos(m*theta)
    ou a*sin(m*theta). m ímpar dá m pétalas, m par dá 2m pétalas (Cap. 6)."""
    theta = np.asarray(theta, dtype=float)
    return a * (np.cos(m * theta) if trig == "cos" else np.sin(m * theta))


def grandi_rose(theta, m, A=1.0, B=1.0, n1=1.0, n2=1.0, n3=1.0, trig="cos"):
    """Eq. 7.20 / 7.21 — curva de Grandi generalizada (superrosa): o numerador
    de período completo cos(m*theta) (ou sin(m*theta)) dividido pelo
    denominador da Superfórmula (Eq. 5.8).

        rho(theta) = cos(m*theta) / [ |cos(m*theta/4)/A|^n2 + |sin(m*theta/4)/B|^n3 ]^(1/n1)
    """
    theta = np.asarray(theta, dtype=float)
    numerator = np.cos(m * theta) if trig == "cos" else np.sin(m * theta)
    term1 = np.abs(np.cos(m * theta / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m * theta / 4.0) / B) ** n3
    return numerator / (term1 + term2) ** (1.0 / n1)


def lemniscate(theta, a=1.0):
    """Lemniscata de Bernoulli: rho(theta) = a*sqrt(2*cos(2*theta)) (Cap. 6),
    curva de 1-termo mencionada junto às Rhodonea."""
    theta = np.asarray(theta, dtype=float)
    return a * np.sqrt(2 * np.cos(2 * theta))


def folium_of_descartes(theta, a=1.0):
    """Eq. 5.5/5.6 — Fólio de Descartes como transformação de Gielis
    (n1=1, n2=n3=3, f(theta)=3*a*sin(theta)*cos(theta)):

        rho(theta) = 3*a*sin(theta)*cos(theta) / (cos(theta)^3 + sin(theta)^3)
    """
    theta = np.asarray(theta, dtype=float)
    return 3 * a * np.sin(theta) * np.cos(theta) / (np.cos(theta) ** 3 + np.sin(theta) ** 3)


def archimedean_spiral(theta, a=1.0):
    """Espiral de Arquimedes: rho(theta) = a*theta (Cap. 5, "Gielis
    Transformations")."""
    return a * np.asarray(theta, dtype=float)


def logarithmic_spiral(theta, k=0.1):
    """Espiral logarítmica: rho(theta) = exp(k*theta) (Cap. 5, Fig. 5.8-5.9;
    usada para gerar conchas do tipo Nautilus)."""
    return np.exp(k * np.asarray(theta, dtype=float))


def golden_angle(unit="rad"):
    """Ângulo áureo, o limite de 2*pi*(1 - 1/golden_ratio) ~= 137.5 graus,
    citado no Cap. 5 ("Polygrams and Generic Symmetries") como o limite dos
    ângulos m dados por razões de Fibonacci F(n)/F(n+2)."""
    angle_rad = 2 * np.pi * (1 - 1.0 / GOLDEN_RATIO)
    return angle_rad if unit == "rad" else np.degrees(angle_rad)


def fibonacci_symmetry_ratio(n):
    """Razão F(n+2)/F(n) de números de Fibonacci consecutivos (deslocados de
    2), usada no livro como o parâmetro m de superpolígonos/polygramas
    fibonacci (ex. 5/2, 8/3, ...). Converge para o número áureo ao quadrado
    (phi^2 = phi+1 ~= 2.618), não para phi diretamente, já que
    F(n+2)/F(n) = [F(n+2)/F(n+1)]*[F(n+1)/F(n)] -> phi*phi."""
    a, b = 0, 1
    fib = [a, b]
    for _ in range(n + 2):
        a, b = b, a + b
        fib.append(b)
    return fib[n + 2] / fib[n]


def vogel_phyllotaxis(n_points, c=1.0):
    """Modelo de Vogel para filotaxia (padrão de espirais de girassol/pinha),
    construção padrão associada ao ângulo áureo discutido no Cap. 5. Não é
    uma equação numerada do livro, mas a realização geométrica direta do
    ângulo áureo (golden_angle) que o livro descreve textualmente.

    Retorna (x, y) para n_points sementes, com r_k = c*sqrt(k).
    """
    k = np.arange(n_points)
    angle = k * golden_angle()
    r = c * np.sqrt(k)
    return r * np.cos(angle), r * np.sin(angle)
