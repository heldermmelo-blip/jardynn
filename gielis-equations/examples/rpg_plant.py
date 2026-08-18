"""Gerador procedural de árvore para uso em jogos (ex. RPG), exportada como
malha 3D em .obj.

Este era o exemplo original (específico de árvores) e ficou como um atalho
fino sobre `gielis.plants`, que generaliza o mesmo motor (esqueleto de
galhos + tubo com seção de Lamé + folhas) para várias espécies — árvore,
arbusto, espinheiro, bambu, videira, flor, cogumelo, samambaia. Veja
`examples/plant_species_gallery.py` para gerar uma de cada.

Uso:
    python examples/rpg_plant.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gielis.plants import generate_plant as _generate_plant

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def generate_plant(seed=0, max_depth=4, out_path=None):
    """Gera uma árvore completa (tronco + galhos + folhas nas pontas) e
    salva em `out_path` (padrão: examples/output/plant.obj)."""
    rng = random.Random(seed)
    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, "plant.obj")
    return _generate_plant(rng, "arvore", out_path=out_path, max_depth=max_depth)


def plot_skeleton_preview(skeleton, out_name="plant_skeleton_preview.png"):
    """Pré-visualização rápida (wireframe) do esqueleto de galhos, útil pra
    conferir a estrutura antes de abrir o .obj num programa 3D."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    for seg in skeleton:
        s, e = seg["start"], seg["end"]
        ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color="tab:green", linewidth=max(0.5, 4 * seg["r0"]))
    ax.set_title("Pré-visualização do esqueleto da planta")
    ax.set_box_aspect([1, 1, 1.4])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUTPUT_DIR, out_name), dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    path, skeleton = generate_plant(seed=42, max_depth=4)
    print(f"planta gerada: {path} ({len(skeleton)} segmentos)")
    plot_skeleton_preview(skeleton)
    print(f"pré-visualização salva em: {os.path.join(OUTPUT_DIR, 'plant_skeleton_preview.png')}")
