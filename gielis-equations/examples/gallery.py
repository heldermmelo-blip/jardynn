"""Galeria de exemplos: gera figuras a partir das equações da biblioteca
`gielis`, salvando PNGs em `examples/output/`.

Uso:
    python examples/gallery.py
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - registra a projeção 3D

# Permite rodar `python examples/gallery.py` sem instalar o pacote antes.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gielis import curves, lame, models, rfunctions, superformula, surfaces

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _save(fig, name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo: {path}")


def plot_superformula_gallery():
    """Grade de formas geradas pela Superfórmula (Eq. 5.8) para vários m."""
    theta = np.linspace(0, 2 * np.pi, 1000)
    params = [
        dict(m=3, n1=1, n2=1, n3=1),
        dict(m=5, n1=0.5, n2=0.3, n3=0.3),
        dict(m=6, n1=60, n2=55, n3=30),
        dict(m=16, n1=3, n2=17, n3=10),
        dict(m=7, n1=2.4, n2=6, n3=6),
        dict(m=4, n1=12, n2=15, n3=15),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(10, 7))
    for ax, p in zip(axes.flat, params):
        rho = superformula.superformula(theta, **p)
        x, y = superformula.to_cartesian(theta, rho)
        ax.plot(x, y, color="tab:green")
        ax.set_title(f"m={p['m']}, n=({p['n1']},{p['n2']},{p['n3']})", fontsize=9)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Superfórmula de Gielis (Eq. 5.8)")
    _save(fig, "superformula_gallery.png")


def plot_lame_family():
    """Família de curvas de Lamé (Eq. 4.1) para diferentes expoentes n."""
    theta = np.linspace(0, 2 * np.pi, 1000)
    fig, ax = plt.subplots(figsize=(5, 5))
    for n, color in zip([0.5, 1, 2, 4, 10], plt.cm.viridis(np.linspace(0, 1, 5))):
        rho = lame.lame_polar_radius(theta, A=1.0, B=1.0, n=n)
        x, y = superformula.to_cartesian(theta, rho)
        ax.plot(x, y, color=color, label=f"n={n}")
    ax.set_aspect("equal")
    ax.legend(fontsize=8)
    ax.set_title("Curvas de Lamé / supercírculos (Eq. 4.1)")
    _save(fig, "lame_family.png")


def plot_grandi_roses():
    """Rosáceas de Grandi generalizadas (Eq. 7.20)."""
    theta = np.linspace(0, 2 * np.pi, 2000)
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))
    for ax, m in zip(axes, [3, 5, 7]):
        rho = curves.grandi_rose(theta, m=m, n1=8, n2=8, n3=8)
        x, y = superformula.to_cartesian(theta, rho)
        ax.plot(x, y, color="tab:pink")
        ax.set_title(f"m={m}")
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Curvas de Grandi generalizadas / superrosas (Eq. 7.20)")
    _save(fig, "grandi_roses.png")


def plot_bamboo_leaves():
    """Modelo de 2 parâmetros para folhas de bambu (Eq. 10.1).

    A Eq. 10.1 tem simetria de 4 pontas (período de 90 graus); usamos só um
    lobo (theta de 0 a 90 graus, já bilateralmente simétrico em torno da
    diagonal de 45 graus) como o contorno de uma folha isolada — plotar a
    curva inteira (0 a 360 graus) resultaria numa estrela de 4 pontas, não
    numa folha.

    Nota: o expoente interno da Eq. 10.1 ficou ambíguo na extração do PDF
    (ver EQUATIONS.md e `models.bamboo_leaf_radius`); `bamboo_leaf_radius`
    usa a leitura em que esse expoente é o próprio `n`. Com essa leitura,
    os valores de n citados no livro para bambus reais (0.02-0.1) fazem a
    curva colapsar quase a zero perto da diagonal de 45 graus, em vez de
    uma silhueta lisa de folha. Por isso a demonstração usa valores de n
    bem maiores (que dão formas bem-comportadas, de losango a quase
    circular), só para ilustrar a família de curvas — não os valores reais
    das espécies do livro.
    """
    theta = np.linspace(0, np.pi / 2, 500)
    ca, sa = np.cos(np.pi / 4), np.sin(np.pi / 4)  # gira 45 graus: ponta aponta pra cima
    fig, ax = plt.subplots(figsize=(6, 4))
    for n in [1.0, 2.0, 4.0, 8.0]:
        rho = models.bamboo_leaf_radius(theta, n=n, l=1.0)
        x, y = superformula.to_cartesian(theta, rho)
        xr, yr = x * ca - y * sa, x * sa + y * ca
        xr = np.concatenate([[0.0], xr, [0.0]])  # fecha o contorno na base (origem)
        yr = np.concatenate([[0.0], yr, [0.0]])
        ax.plot(xr, yr, label=f"n={n}")
    ax.set_aspect("equal")
    ax.legend(fontsize=8)
    ax.set_title("Modelo de folhas de bambu, 2 parâmetros (Eq. 10.1)")
    _save(fig, "bamboo_leaves.png")


def plot_rfunctions_union_intersection():
    """Visualiza a função-R R0 (Eq. 6.8-6.9) combinando dois círculos, como
    campo escalar positivo dentro / negativo fora da forma composta."""
    x = np.linspace(-2, 2, 300)
    y = np.linspace(-2, 2, 300)
    X, Y = np.meshgrid(x, y)
    circle1 = 1 - (X + 0.5) ** 2 - Y**2  # >0 dentro do círculo 1
    circle2 = 1 - (X - 0.5) ** 2 - Y**2  # >0 dentro do círculo 2

    union = rfunctions.r0_disjunction(circle1, circle2)
    intersection = rfunctions.r0_conjunction(circle1, circle2)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
    for ax, field, title in zip(axes, [union, intersection], ["União (R0 disjunção)", "Interseção (R0 conjunção)"]):
        ax.contourf(X, Y, field, levels=[-10, 0, 10], colors=["white", "tab:blue"])
        ax.contour(X, Y, field, levels=[0], colors="k")
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=10)
    fig.suptitle("Funções-R de Rvachev (Eqs. 6.6-6.9)")
    _save(fig, "rfunctions_union_intersection.png")


def plot_gielis_surface_3d():
    """Superfície de Gielis 3D via produto esférico (Eq. 5.20)."""
    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)
    phi = np.linspace(-np.pi, np.pi, 200)
    THETA, PHI = np.meshgrid(theta, phi, indexing="ij")

    rho1 = superformula.superformula(THETA * 2, m=6, n1=8, n2=8, n3=8)
    rho2 = superformula.superformula(PHI, m=4, n1=8, n2=8, n3=8)
    x, y, z = surfaces.spherical_product(rho1, rho2, THETA, PHI)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(x, y, z, cmap="viridis", linewidth=0, antialiased=True)
    ax.set_title("Superfície de Gielis 3D, produto esférico (Eq. 5.20)")
    ax.set_box_aspect([1, 1, 1])
    _save(fig, "gielis_surface_3d.png")


def plot_phyllotaxis():
    """Padrão de filotaxia de Vogel com o ângulo áureo (Cap. 5, ângulo áureo)."""
    x, y = curves.vogel_phyllotaxis(500)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(x, y, s=10, c=np.arange(len(x)), cmap="YlGn")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Filotaxia de Vogel, ângulo áureo = {curves.golden_angle('deg'):.3f} graus")
    _save(fig, "phyllotaxis.png")


if __name__ == "__main__":
    plot_superformula_gallery()
    plot_lame_family()
    plot_grandi_roses()
    plot_bamboo_leaves()
    plot_rfunctions_union_intersection()
    plot_gielis_surface_3d()
    plot_phyllotaxis()
