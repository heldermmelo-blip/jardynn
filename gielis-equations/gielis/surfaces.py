"""Superfícies de Gielis em 3D (superelipsoides, superquádricas, produto
esférico).

Referência: Cap. 5, seção "Gielis Surfaces and Volumes" (Eqs. 5.16-5.20).
"""

import numpy as np


def superellipsoid_radius(theta, phi, a=1.0, b=1.0, c=1.0, p=2.0):
    """Eq. 5.16 — raio r(theta, phi) do superelipsoide, resolvendo

        |r*sin(theta)*cos(phi)/a|^p + |r*sin(theta)*sin(phi)/b|^p + |r*cos(theta)/c|^p = 1

    para r (theta = colatitude, phi = azimute).
    """
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    t1 = np.abs(np.sin(theta) * np.cos(phi) / a) ** p
    t2 = np.abs(np.sin(theta) * np.sin(phi) / b) ** p
    t3 = np.abs(np.cos(theta) / c) ** p
    return (t1 + t2 + t3) ** (-1.0 / p)


def superellipsoid(theta, phi, a=1.0, b=1.0, c=1.0, p=2.0):
    """Eq. 5.16 — pontos (x, y, z) do superelipsoide em coordenadas esféricas."""
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    r = superellipsoid_radius(theta, phi, a, b, c, p)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z


def gielis_radius_3d(theta, phi, a=1.0, b=1.0, c=1.0, m1=4.0, m2=4.0, n1=1.0, n2=1.0, n3=1.0, n4=1.0):
    """Eq. 5.17 — raio r(theta, phi) da superfície de Gielis 3D generalizada.

    r(theta, phi) = [ |sin(m1*theta/4)*cos(m2*phi/4)/a|^n2
                     + |sin(m1*theta/4)*sin(m2*phi/4)/b|^n3
                     + |cos(m1*theta/4)/c|^n4 ]^(-1/n1)

    Com a(theta, phi) = 1 (esfera unitária) como caso de referência; para
    outras funções de modulação, ver `superformula.gielis_transform`
    aplicada em cada seção perpendicular.
    """
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    t1 = np.abs(np.sin(m1 * theta / 4.0) * np.cos(m2 * phi / 4.0) / a) ** n2
    t2 = np.abs(np.sin(m1 * theta / 4.0) * np.sin(m2 * phi / 4.0) / b) ** n3
    t3 = np.abs(np.cos(m1 * theta / 4.0) / c) ** n4
    return (t1 + t2 + t3) ** (-1.0 / n1)


def gielis_surface(theta, phi, a=1.0, b=1.0, c=1.0, m1=4.0, m2=4.0, n1=1.0, n2=1.0, n3=1.0, n4=1.0):
    """Eq. 5.17 — pontos (x, y, z) da superfície de Gielis 3D generalizada.

    Usa `gielis_radius_3d` para o raio e converte para cartesianas.
    """
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    r = gielis_radius_3d(theta, phi, a, b, c, m1, m2, n1, n2, n3, n4)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z


def sphere_spherical_product(theta, phi, R=1.0):
    """Eq. 5.18-5.19 — esfera de raio R como produto esférico de um círculo
    completo mu(theta) = (cos theta, sin theta), -pi/2 < theta < pi/2, e um
    semicírculo eta(phi) = (cos phi, sin phi), -pi < phi < pi.

    x = R*cos(theta)*cos(phi); y = R*sin(theta)*cos(phi); z = R*sin(phi)
    """
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    x = R * np.cos(theta) * np.cos(phi)
    y = R * np.sin(theta) * np.cos(phi)
    z = R * np.sin(phi)
    return x, y, z


def spherical_product(rho1, rho2, theta, phi):
    """Eq. 5.20 — produto esférico de duas 2D-supershapes rho1(theta), rho2(phi).

    Constrói qualquer superfície de Gielis 3D a partir de duas seções
    perpendiculares: rho1 (a seção "objeto", plano XY) e rho2 (a seção
    "trajetória" de rotação em torno do eixo Z).

        x = rho1(theta)*cos(theta) * rho2(phi)*cos(phi)
        y = rho1(theta)*sin(theta) * rho2(phi)*cos(phi)
        z = rho2(phi)*sin(phi)

    `rho1`, `rho2` podem ser arrays já avaliados ou funções chamáveis.
    """
    theta, phi = np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)
    rho1_values = rho1(theta) if callable(rho1) else np.asarray(rho1, dtype=float)
    rho2_values = rho2(phi) if callable(rho2) else np.asarray(rho2, dtype=float)
    x = rho1_values * np.cos(theta) * rho2_values * np.cos(phi)
    y = rho1_values * np.sin(theta) * rho2_values * np.cos(phi)
    z = rho2_values * np.sin(phi)
    return x, y, z


def surface_grid(theta_range=(-np.pi / 2, np.pi / 2), phi_range=(-np.pi, np.pi), n_theta=80, n_phi=160):
    """Malha (theta, phi) conveniente para avaliar as funções acima e plotar
    com matplotlib (ver examples/gallery.py). Não corresponde a nenhuma
    equação do livro; é apenas um utilitário de visualização.
    """
    theta = np.linspace(theta_range[0], theta_range[1], n_theta)
    phi = np.linspace(phi_range[0], phi_range[1], n_phi)
    return np.meshgrid(theta, phi, indexing="ij")
