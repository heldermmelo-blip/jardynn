"""Testes de sanidade: cada teste confere uma identidade matemática conhecida
das equações do livro (ex. casos particulares que devem reduzir a um
círculo, invariâncias citadas no texto, ou consistência entre duas
implementações da mesma equação).

Rode com `pytest` (descoberta automática de `test_*`) ou diretamente com
`python tests/test_gielis.py`.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gielis import chebyshev, curvature, curves, lame, models, rfunctions, shape_metrics, superformula

THETA = np.linspace(0, 2 * np.pi, 400, endpoint=False)


def test_generalized_pythagorean_identity():
    # Eq. 5.3: (ncos)^n + (nsin)^n == 1 identicamente, para qualquer n.
    for n in (1.5, 2.0, 3.0, 4.7):
        residual = lame.generalized_pythagorean_residual(THETA, n)
        assert np.allclose(residual, 1.0, atol=1e-8), f"falhou para n={n}"


def test_lame_matches_superformula_special_case():
    # lame_polar_radius(theta, A, B, n) deve coincidir com o caso particular
    # m=4, n1=n2=n3=n da Superfórmula (Eq. 5.8 reduzindo à Eq. 5.1).
    A, B, n = 2.0, 0.7, 3.3
    rho_lame = lame.lame_polar_radius(THETA, A, B, n)
    rho_super = superformula.superformula(THETA, m=4.0, A=A, B=B, n1=n, n2=n, n3=n)
    assert np.allclose(rho_lame, rho_super)


def test_superformula_circle_invariant_for_any_m():
    # Cap. 5, "Invariance Properties": para A=B=1, n2=n3=2, o denominador da
    # Superfórmula vale 1 para QUALQUER m (o círculo é "todos os polígonos
    # regulares ao mesmo tempo").
    for m in (3.0, 4.0, 5.0, 7.5):
        rho = superformula.superformula(THETA, m=m, A=1.0, B=1.0, n1=2.0, n2=2.0, n3=2.0)
        assert np.allclose(rho, 1.0, atol=1e-8), f"falhou para m={m}"


def test_superellipse_implicit_on_curve():
    # Pontos gerados por lame_polar_radius devem satisfazer a Eq. 4.1 exatamente.
    A, B, n = 1.5, 0.8, 2.5
    rho = lame.lame_polar_radius(THETA, A, B, n)
    x, y = superformula.to_cartesian(THETA, rho)
    assert np.allclose(lame.superellipse_implicit(x, y, A, B, n), 1.0, atol=1e-6)


def test_bamboo_leaf_matches_superformula():
    n, l = 0.05, 3.0
    rho_model = models.bamboo_leaf_radius(THETA, n=n, l=l)
    rho_super = l * superformula.superformula(THETA, m=4.0, A=1.0, B=1.0, n1=n, n2=n, n3=n)
    assert np.allclose(rho_model, rho_super)


def test_tree_ring_matches_superformula():
    n, a, b = 4.0, 2.0, 1.3
    rho_model = models.tree_ring_radius(THETA, n=n, a=a, b=b)
    rho_super = superformula.superformula(THETA, m=4.0, A=a, B=b, n1=n, n2=n, n3=n)
    assert np.allclose(rho_model, rho_super)


def test_rfunctions_r1_reduces_to_max_min():
    s1, s2 = np.array([1.0, -2.0, 3.0]), np.array([2.0, -1.0, 3.0])
    assert np.allclose(rfunctions.r1_max(s1, s2), np.maximum(s1, s2))
    assert np.allclose(rfunctions.r1_min(s1, s2), np.minimum(s1, s2))


def test_rfunctions_alpha_one_matches_r1():
    s1, s2 = 1.7, -0.4
    assert math.isclose(rfunctions.r_alpha(s1, s2, alpha=1 - 1e-9, disjunction=True), rfunctions.r1_max(s1, s2), rel_tol=1e-5)
    assert math.isclose(rfunctions.r_alpha(s1, s2, alpha=1 - 1e-9, disjunction=False), rfunctions.r1_min(s1, s2), rel_tol=1e-5)


def test_rfunctions_disjunction_ge_conjunction():
    s1, s2 = 0.6, 0.9
    assert rfunctions.r0_disjunction(s1, s2) >= rfunctions.r0_conjunction(s1, s2)
    assert rfunctions.rp_disjunction(s1, s2, p=3.0) >= rfunctions.rp_conjunction(s1, s2, p=3.0)


def test_area_and_circumference_of_unit_circle():
    unit_circle = lambda theta: np.ones_like(np.asarray(theta, dtype=float))
    assert math.isclose(shape_metrics.area(unit_circle, m=1.0), np.pi, rel_tol=1e-6)
    assert math.isclose(shape_metrics.circumference(unit_circle, m=1.0), 2 * np.pi, rel_tol=1e-4)


def test_chebyshev_t_matches_cosine():
    theta = np.linspace(0, np.pi, 50)
    x = np.cos(theta)
    for m in (1, 2, 5):
        assert np.allclose(chebyshev.chebyshev_t(m, x), np.cos(m * theta), atol=1e-8)


def test_chebyshev_u_matches_sine_identity():
    theta = np.linspace(0.05, np.pi - 0.05, 50)  # evita sin(theta)=0
    x = np.cos(theta)
    for m in (1, 2, 5):
        assert np.allclose(chebyshev.chebyshev_u(m, x), np.sin((m + 1) * theta) / np.sin(theta), atol=1e-6)


def test_gielis_chebyshev_matches_trig_form():
    theta = np.linspace(0.05, np.pi - 0.05, 60)
    x = np.cos(theta)
    m, n1, n2, n3 = 5, 1.3, 2.0, 2.0
    lhs = chebyshev.gielis_chebyshev(x, m, n1, n2, n3)
    rhs = (np.abs(np.cos(m * theta)) ** n2 + np.abs(np.sin(m * theta)) ** n3) ** (-1.0 / n1)
    assert np.allclose(lhs, rhs, atol=1e-6)


def test_golden_angle_value_degrees():
    assert math.isclose(curves.golden_angle(unit="deg"), 137.50776405003785, rel_tol=1e-9)


def test_fibonacci_symmetry_ratio_converges_to_golden_ratio_squared():
    # F(n+2)/F(n) -> phi^2 (não phi), já que F(n+2)/F(n) = [F(n+2)/F(n+1)] * [F(n+1)/F(n)] -> phi*phi.
    ratio_10 = curves.fibonacci_symmetry_ratio(10)
    assert math.isclose(ratio_10, curves.GOLDEN_RATIO**2, rel_tol=1e-3)


def test_euler_normal_curvature_at_principal_directions():
    kappa1, kappa2 = 3.0, -1.5
    assert math.isclose(curvature.euler_normal_curvature(0.0, kappa1, kappa2), kappa1, rel_tol=1e-9)
    assert math.isclose(curvature.euler_normal_curvature(np.pi / 2, kappa1, kappa2), kappa2, rel_tol=1e-9, abs_tol=1e-9)


def test_anisotropic_mean_curvature_reduces_to_isotropic_case():
    kappa1, kappa2 = 2.0, 5.0
    K = curvature.anisotropic_mean_curvature(T1=1.0, R1=1.0 / kappa1, T2=1.0, R2=1.0 / kappa2)
    assert math.isclose(K, kappa1 + kappa2, rel_tol=1e-9)


def test_gielis_transform_constant_f_matches_superformula():
    m, A, B, n1, n2, n3, R = 5.0, 1.2, 0.9, 1.7, 2.0, 2.0, 2.5
    rho_transform = superformula.transform_circle(THETA, R, m, A, B, n1, n2, n3)
    rho_direct = R * superformula.superformula(THETA, m, A, B, n1, n2, n3)
    assert np.allclose(rho_transform, rho_direct)


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_") and callable(obj)]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"OK   {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} testes passaram.")
    raise SystemExit(1 if failures else 0)
