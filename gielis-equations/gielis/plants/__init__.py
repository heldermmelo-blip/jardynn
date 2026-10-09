"""Geração procedural de malhas 3D de plantas para uso em jogos (RPG).

Isto NÃO são equações do livro — é uma aplicação construída em cima da
biblioteca `gielis`: seções transversais de tronco/galho usam curvas de
Lamé (Eq. 4.1/5.1), e a flor usa a Superfórmula (Eq. 5.8). Generalização de
`examples/rpg_plant.py` (que ficou como o exemplo original, específico de
árvores) para várias espécies — ver `SPECIES` em `gielis.plants.generator`.
"""

from .flowers import ESPECIES_FLORES, PALETAS
from .lsystem import ESPECIES_L, GRAMATICAS
from .generator import SPECIES, generate_fallen_branch, generate_plant

__all__ = ["SPECIES", "ESPECIES_FLORES", "PALETAS", "ESPECIES_L", "GRAMATICAS", "generate_plant", "generate_fallen_branch"]
