"""Biblioteca de equações de *The Geometrical Beauty of Plants* (J. Gielis, 2017).

Cada módulo implementa um grupo de equações do livro; ver EQUATIONS.md na
raiz do projeto para a tabela completa de correspondência equação -> função,
com o número de cada equação e o capítulo onde aparece.
"""

from . import lame
from . import superformula
from . import shape_metrics
from . import surfaces
from . import series
from . import curves
from . import rfunctions
from . import curvature
from . import chebyshev
from . import models

__all__ = [
    "lame",
    "superformula",
    "shape_metrics",
    "surfaces",
    "series",
    "curves",
    "rfunctions",
    "curvature",
    "chebyshev",
    "models",
]
