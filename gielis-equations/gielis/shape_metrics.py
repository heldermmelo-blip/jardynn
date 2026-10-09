"""Invariantes de forma das supershapes: área, momento polar de inércia e
perímetro.

Referência: Cap. 5, seção "Invariance Properties of Supershapes"
(Eqs. 5.13-5.15). O livro escreve as integrais de forma compacta como
`m * integral(0, 2*pi/m)`, explorando a periodicidade de período `2*pi/m`
das supershapes; aqui isso é feito por integração numérica.
"""

import numpy as np
from scipy import integrate


def area(rho_func, m):
    """Eq. 5.13 — área de uma supershape com raio polar rho_func(theta) e
    periodicidade `m` (a mesma simetria rotacional passada à Superfórmula).

    A = m * integral_0^(2*pi/m) [ rho(theta)^2 / 2 ] dtheta
    """

    def integrand(theta):
        """Integrando da área polar: rho^2 / 2."""
        return 0.5 * rho_func(theta) ** 2

    period_integral, _ = integrate.quad(integrand, 0.0, 2 * np.pi / m)
    return m * period_integral


def polar_moment_of_inertia(rho_func, m):
    """Eq. 5.14 — momento polar de inércia Ip de uma supershape.

    Ip = m * integral_0^(2*pi/m) [ rho(theta)^4 / 4 ] dtheta
    """

    def integrand(theta):
        """Integrando do momento de inércia polar: rho^4 / 4."""
        return 0.25 * rho_func(theta) ** 4

    period_integral, _ = integrate.quad(integrand, 0.0, 2 * np.pi / m)
    return m * period_integral


def circumference(rho_func, m, d_theta=1e-6):
    """Eq. 5.15 — perímetro (circunferência) de uma supershape.

    s = m * integral_0^(2*pi/m) sqrt( rho(theta)^2 + rho'(theta)^2 ) dtheta

    A derivada rho'(theta) é aproximada por diferenças finitas centradas,
    com passo `d_theta`. Vale a mesma ideia de `area`: integra-se um só
    período (0 a 2*pi/m) e multiplica-se por `m`.
    """

    def rho_prime(theta):
        """Derivada de rho em `theta`, por diferença centrada."""
        # Diferença centrada: erro O(d_theta^2), melhor que a unilateral.
        return (rho_func(theta + d_theta) - rho_func(theta - d_theta)) / (2 * d_theta)

    def integrand(theta):
        """Elemento de arco polar: sqrt(rho^2 + rho'^2)."""
        # Elemento de arco em coordenadas polares: ds = sqrt(rho^2 + rho'^2) dtheta.
        return np.sqrt(rho_func(theta) ** 2 + rho_prime(theta) ** 2)

    period_integral, _ = integrate.quad(integrand, 0.0, 2 * np.pi / m, limit=200)
    return m * period_integral
