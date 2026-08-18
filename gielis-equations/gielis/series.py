"""Somas de supershapes (curvas "k-type") e a série super-Fourier.

Referência: Cap. 6, seção "k-Type Curves and a Generalization of Fourier
Series" (Eqs. 6.4-6.5).
"""

import numpy as np

from .superformula import gielis_transform


def k_type_sum(theta, terms):
    """Eq. 6.4 — soma de k supershapes com o mesmo centro (curva "k-type").

    `terms` é uma lista de dicionários, cada um com as chaves aceitas por
    `superformula.gielis_transform` (f, m, A, B, n1, n2, n3), representando
    um termo f_i(theta) / [...]^(1/n_i1) da soma:

        rho(theta) = sum_i f_i(theta) / [ |cos(m_i*theta/4)/A_i|^n_i2 + |sin(m_i*theta/4)/B_i|^n_i3 ]^(1/n_i1)

    Exemplo: `k_type_sum(theta, [dict(f=1.0, m=4, n1=2, n2=2, n3=2), ...])`.
    """
    theta = np.asarray(theta, dtype=float)
    total = np.zeros_like(theta)
    for term in terms:
        total = total + gielis_transform(
            theta,
            term.get("f", 1.0),
            term["m"],
            term.get("A", 1.0),
            term.get("B", 1.0),
            term.get("n1", 1.0),
            term.get("n2", 1.0),
            term.get("n3", 1.0),
        )
    return total


def super_fourier_series(theta, a0, rho0, coefficients, m=4.0):
    """Eq. 6.5 — série "super-Fourier": cada termo de uma série de Fourier
    associado a uma supershape rho_k(theta) em vez de apenas cos/sin.

        rho(theta) = rho0*a0 + sum_k [ a_k*rho_k(theta)*cos(m*k*theta/4)
                                       + b_k*rho_k(theta)*sin(m*k*theta/4) ]

    `coefficients` é uma lista de tuplas `(k, a_k, b_k, rho_k)`, onde
    `rho_k` é um array (mesmo shape de `theta`) ou uma função `rho_k(theta)`.
    """
    theta = np.asarray(theta, dtype=float)
    total = rho0 * a0 * np.ones_like(theta)
    for k, a_k, b_k, rho_k in coefficients:
        rho_k_values = rho_k(theta) if callable(rho_k) else np.asarray(rho_k, dtype=float)
        total = total + rho_k_values * (a_k * np.cos(m * k * theta / 4.0) + b_k * np.sin(m * k * theta / 4.0))
    return total
