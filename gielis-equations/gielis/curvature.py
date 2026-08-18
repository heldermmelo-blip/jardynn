"""Curvatura: de Frenet-Serret a curvaturas "generalizadas" definidas a
partir de curvas de Lamé e de Gielis, e métricas de curvatura constante.

Referência: Cap. 7 (Eqs. 7.12-7.15) e Cap. 9 "Natural Curvature Conditions"
(Eqs. 9.1-9.21), Cap. 11 (Eq. 11.1).
"""

import numpy as np


# ---------------------------------------------------------------------------
# Cap. 7 — métricas (Eqs. 7.12-7.15)
# ---------------------------------------------------------------------------


def lp_metric(dx, p=2.0):
    """Eq. 7.12 — métrica de Riemann-Finsler em norma l^p:

    ds = ( sum_i |dx_i|^p )^(1/p)

    `dx` é um array/sequência de diferenciais (dx_1, ..., dx_n).
    """
    dx = np.asarray(dx, dtype=float)
    return np.sum(np.abs(dx) ** p, axis=-1) ** (1.0 / p)


def euclidean_metric(dx):
    """Eq. 7.13 — caso p=2 da métrica l^p: a métrica Euclidiana usual."""
    return lp_metric(dx, p=2.0)


def constant_curvature_line_element(dx_euclidean, x, k):
    """Eq. 7.14 — elemento de linha de uma métrica de curvatura constante `k`
    (tipo disco de Poincaré / geometria elíptica, dependendo do sinal de k):

        ds = sqrt(sum_i dx_i^2) / [ 1 + (k/4) * sum_i x_i^2 ]

    `dx_euclidean` é sqrt(sum dx_i^2) (o numerador já calculado), `x` é a
    posição (x_1, ..., x_n) onde a métrica é avaliada.
    """
    x = np.asarray(x, dtype=float)
    denom = 1.0 + (k / 4.0) * np.sum(x**2, axis=-1)
    return dx_euclidean / denom


def flrw_spatial_factor(x, k):
    """Eq. 7.15 — fator espacial da métrica FLRW: 1 / [1 + (k/4)*sum(x_i^2)]^2,
    que multiplica (dx^2+dy^2+dz^2) na métrica espaço-tempo
    ds^2 = -dt^2 + a(t)^2 * fator_espacial * (dx^2+dy^2+dz^2)."""
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + (k / 4.0) * np.sum(x**2, axis=-1)) ** 2


def flrw_line_element_squared(dt, dx_euclidean_squared, x, k, scale_factor):
    """Eq. 7.15 completa: ds^2 = -dt^2 + a(t)^2 * flrw_spatial_factor(x, k) * dx_euclidean_squared."""
    return -(dt**2) + scale_factor**2 * flrw_spatial_factor(x, k) * dx_euclidean_squared


# ---------------------------------------------------------------------------
# Cap. 9 — curvatura de curvas e superfícies (Eqs. 9.1-9.21)
# ---------------------------------------------------------------------------


def frenet_serret_derivatives(kappa, tau, t, n, b):
    """Eq. 9.1 — fórmulas de Frenet-Serret(-Pagani):

        t' = kappa*n
        n' = -kappa*t + tau*b
        b' = -tau*n

    `t`, `n`, `b` são os vetores tangente, normal e binormal (arrays 3D) em
    um ponto da curva; `kappa`, `tau` são a curvatura e a torção nesse ponto.
    Retorna (t', n', b').
    """
    t, n, b = np.asarray(t, dtype=float), np.asarray(n, dtype=float), np.asarray(b, dtype=float)
    t_prime = kappa * n
    n_prime = -kappa * t + tau * b
    b_prime = -tau * n
    return t_prime, n_prime, b_prime


def darboux_vector(kappa, tau, b, t):
    """Vetor de Darboux d = kappa*b + tau*t, usado na forma alternativa de
    Frenet-Serret (Eq. 9.2). Seu comprimento sqrt(kappa^2+tau^2) é a
    velocidade angular do referencial móvel."""
    b, t = np.asarray(b, dtype=float), np.asarray(t, dtype=float)
    return kappa * b + tau * t


def frenet_serret_via_darboux(d, t, n, b):
    """Eq. 9.2 — forma via vetor de Darboux: t'=d×t, n'=d×n, b'=d×b."""
    d, t, n, b = (np.asarray(v, dtype=float) for v in (d, t, n, b))
    return np.cross(d, t), np.cross(d, n), np.cross(d, b)


def casorati_curvature(kappa1, kappa2):
    """Eq. 9.3 — curvatura de Casorati: C = (kappa1^2 + kappa2^2) / 2."""
    return (kappa1**2 + kappa2**2) / 2.0


def shape_index(kappa1, kappa2):
    """Eq. 9.4 — Índice de Forma de Koenderink & van Doorn:

        r = (2/pi) * arctan( (kappa1+kappa2) / (kappa1-kappa2) )

    Convém que kappa1 >= kappa2 (curvaturas principais ordenadas). O fator
    2/pi normaliza o índice para o intervalo [-1, 1], como na definição
    original de Koenderink & van Doorn (1992) citada pelo livro.
    """
    return (2.0 / np.pi) * np.arctan((kappa1 + kappa2) / (kappa1 - kappa2))


def mean_curvature(kappa1, kappa2):
    """H = (kappa1+kappa2)/2, a curvatura média clássica usada nas Eqs. 9.5-9.8."""
    return (kappa1 + kappa2) / 2.0


def gaussian_curvature(kappa1, kappa2):
    """K = kappa1*kappa2, usada implicitamente na Eq. 9.7 (|K| = sqrt((k1*k2)^2))."""
    return kappa1 * kappa2


def willmore_h2(kappa1, kappa2):
    """Eqs. 9.5-9.7 — H^2 (energia de Willmore, densidade), com as formas
    equivalentes mostradas no livro:

        H^2 = ((kappa1+kappa2)/2)^2
            = (kappa1^2+kappa2^2)/4 + (kappa1*kappa2)/2
    """
    return mean_curvature(kappa1, kappa2) ** 2


def beltrami_mean_curvature(laplacian_x, n):
    """Eq. 9.8 — Teorema de Beltrami: Delta(x) = -n*H, isolando H:

        H = -Delta(x) / n

    `laplacian_x` é o Laplaciano do vetor posição da superfície, `n` a
    dimensão do espaço ambiente.
    """
    return -np.asarray(laplacian_x, dtype=float) / n


def circle_curvature_measure(rho):
    """Eq. 9.9 — curvatura "trivial" do círculo: kappa_C = 1/rho (rho=R constante)."""
    return 1.0 / np.asarray(rho, dtype=float)


def lame_curvature_measure(theta, rho, n):
    """Eq. 9.10 (Definição 9.1) — medida de curvatura via curva de Lamé:

        kappa_L(theta) = 1 / [ rho(theta) * (|cos(theta)|^n + |sin(theta)|^n)^(1/n) ]

    `rho` é o valor de rho(theta) (escalar/array), não a Superfórmula em si;
    combine com `lame.lame_polar_radius` se rho(theta) também for de Lamé.
    """
    theta = np.asarray(theta, dtype=float)
    rho = np.asarray(rho, dtype=float)
    norm = (np.abs(np.cos(theta)) ** n + np.abs(np.sin(theta)) ** n) ** (1.0 / n)
    return 1.0 / (rho * norm)


def gielis_curvature_measure(theta, rho, A, B, m, n1, n2, n3):
    """Eq. 9.11 (Definição 9.2) — medida de curvatura via curva de Gielis:

        kappa_G(theta) = [ |cos(m*theta/4)/A|^n2 + |sin(m*theta/4)/B|^n3 ]^(1/n1) / rho(theta)
    """
    theta = np.asarray(theta, dtype=float)
    rho = np.asarray(rho, dtype=float)
    term1 = np.abs(np.cos(m * theta / 4.0) / A) ** n2
    term2 = np.abs(np.sin(m * theta / 4.0) / B) ** n3
    return (term1 + term2) ** (1.0 / n1) / rho


def lame_inverse_power_residual(theta, n):
    """Eq. 9.13 — lei generalizada do inverso da n-ésima potência (Lamé):

        |cos(theta)|^n + |sin(theta)|^n  (deve igualar rho(theta)^(-n) sobre a curva)
    """
    theta = np.asarray(theta, dtype=float)
    return np.abs(np.cos(theta)) ** n + np.abs(np.sin(theta)) ** n


def gielis_inverse_power_residual(theta, A, B, m, n2, n3):
    """Eq. 9.14 — análogo de Gielis da lei do inverso da potência n1-ésima:

        |cos(m*theta/4)/A|^n2 + |sin(m*theta/4)/B|^n3  (deve igualar rho(theta)^(-n1))
    """
    theta = np.asarray(theta, dtype=float)
    return np.abs(np.cos(m * theta / 4.0) / A) ** n2 + np.abs(np.sin(m * theta / 4.0) / B) ** n3


def euler_normal_curvature(theta, kappa1, kappa2):
    """Eqs. 9.16-9.18 — Teorema de Euler da curvatura normal:

        kappa_n(theta) = kappa1*cos(theta)^2 + kappa2*sin(theta)^2
                        = (kappa1+kappa2)/2 + (kappa1-kappa2)/2 * cos(2*theta)
    """
    theta = np.asarray(theta, dtype=float)
    return (kappa1 + kappa2) / 2.0 + (kappa1 - kappa2) / 2.0 * np.cos(2 * theta)


def euler_normal_curvature_derivative(theta, kappa1, kappa2):
    """Eq. 9.19 — derivada de kappa_n em relação a theta:

        d(kappa_n)/d(theta) = -(kappa1-kappa2) * sin(2*theta)
    """
    theta = np.asarray(theta, dtype=float)
    return -(kappa1 - kappa2) * np.sin(2 * theta)


# ---------------------------------------------------------------------------
# Cap. 11 — curvatura média anisotrópica (Eq. 11.1)
# ---------------------------------------------------------------------------


def anisotropic_mean_curvature(T1, R1, T2, R2):
    """Eq. 11.1 — curvatura média anisotrópica (CAMC, D'Arcy Thompson /
    Koiso-Palmer), tipo equação de Laplace-Young generalizada:

        K = T1/R1 + T2/R2 = T1*kappa1 + T2*kappa2

    onde T1, T2 são tensões ortogonais e R1=1/kappa1, R2=1/kappa2 os raios
    de curvatura principais. K constante caracteriza uma superfície CAMC.
    """
    return T1 / R1 + T2 / R2
