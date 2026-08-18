# gielis-equations

Biblioteca com as equações de **_The Geometrical Beauty of Plants_** (Johan
Gielis, Atlantis Press, 2017) — a Superfórmula de Gielis, curvas de Lamé,
funções-R de Rvachev, curvaturas generalizadas e os modelos aplicados a
folhas de bambu e anéis de crescimento discutidos no livro.

Duas partes:

- **[`EQUATIONS.md`](EQUATIONS.md)** — catálogo de referência de todas as
  equações relevantes, organizado por capítulo, com o número de cada
  equação no livro e a correspondência com as funções do código.
- **`gielis/`** — pacote Python que implementa essas equações como funções
  utilizáveis (com NumPy/SciPy).

## Instalação

```bash
pip install -e .
pip install -r requirements.txt   # inclui matplotlib, para os exemplos
```

## Uso rápido

```python
import numpy as np
from gielis import superformula, lame

theta = np.linspace(0, 2 * np.pi, 1000)

# A Superfórmula (Eq. 5.8) — ex. um pentágono suavizado
rho = superformula.superformula(theta, m=5, n1=8, n2=8, n3=8)
x, y = superformula.to_cartesian(theta, rho)

# Uma superelipse de Lamé (Eq. 4.1 / 5.1)
rho_lame = lame.lame_polar_radius(theta, A=2.0, B=1.0, n=3.0)
```

Para uma galeria de exemplos com gráficos (2D e 3D), veja
[`examples/gallery.py`](examples/gallery.py):

```bash
python examples/gallery.py
```

As figuras são salvas em `examples/output/`.

## Módulos

| Módulo | Conteúdo | Equações do livro |
|---|---|---|
| `gielis.lame` | Curvas de Lamé, cônicas generalizadas, seno/cosseno de Lamé | 4.1-4.3, 5.1-5.4 |
| `gielis.superformula` | A Superfórmula e a Transformação de Gielis | 5.7-5.9, 5.12, 6.2-6.3, 9.20-9.21 |
| `gielis.shape_metrics` | Área, momento polar de inércia, perímetro | 5.13-5.15 |
| `gielis.surfaces` | Superelipsoides e superfícies de Gielis 3D | 5.16-5.20 |
| `gielis.series` | Somas de supershapes ("k-type"), série super-Fourier | 6.4-6.5 |
| `gielis.curves` | Cardioide, rosáceas de Grandi, lemniscata, espirais, ângulo áureo | 5.5-5.6, 7.20-7.21, Cap. 5/6 |
| `gielis.rfunctions` | Funções-R de Rvachev (união/interseção com diferenciabilidade) | 6.6-6.14 |
| `gielis.curvature` | Frenet-Serret, curvaturas de Casorati/Willmore, curvatura de Lamé/Gielis, métricas de curvatura constante | 7.12-7.15, 9.1-9.19, 11.1 |
| `gielis.chebyshev` | Superfórmula via polinômios de Chebyshev | 7.16-7.18, 7.22 |
| `gielis.models` | Modelo de folhas de bambu e de anéis de crescimento | 10.1-10.2 |

Ver [`EQUATIONS.md`](EQUATIONS.md) para a tabela completa e o texto de cada
equação.

## Testes

```bash
pytest tests/
```

Os testes conferem identidades matemáticas conhecidas das equações (ex.:
`(ncos θ)ⁿ + (nsin θ)ⁿ = 1`; a Superfórmula reduz a um círculo para
`n1=n2=n3=2` independente de `m`; a área de um círculo unitário é `π`).

## Notas sobre a fonte

As equações foram extraídas do PDF do livro (extração de texto via
`pdftotext`) e conferidas contra a literatura matemática padrão sobre os
mesmos tópicos (curvas de Lamé, funções-R de Rvachev, polinômios de
Chebyshev) sempre que a extração corrompeu sobrescritos/frações. Duas
equações (6.1, com funções elípticas de Jacobi; 7.19, relação
Fibonacci/Lucas-Chebyshev) não foram implementadas por não ter sido
possível reconstruí-las com confiança suficiente a partir do texto extraído
— ver as notas com ⚠ em `EQUATIONS.md`.
