# Equações — *The Geometrical Beauty of Plants* (Johan Gielis, Atlantis Press, 2017)

Catálogo de referência das equações do livro, organizado por capítulo. Cada
entrada cita o número da equação no livro (ex. `Eq. 5.8`) e o capítulo/seção
onde aparece, para permitir conferência direta com o PDF original.

Notação geral: `θ` (ou `#` no livro) é o ângulo polar, `ρ(θ)` é o raio polar,
`A, B` são semi-eixos, `m` é o parâmetro de simetria rotacional, `n1, n2, n3`
são os expoentes de forma.

Equações marcadas com **⚠ reconstrução** foram recuperadas de um trecho do
PDF em que a extração de texto corrompeu sobrescritos/frações; a forma
apresentada segue a literatura matemática padrão sobre o mesmo tópico
(citada) e é consistente com o texto ao redor, mas vale conferir a página
original antes de usá-la como citação direta do livro.

---

## Capítulo 3 — Legado aritmético/geométrico

- **Teorema de Pitágoras generalizado (forma "pura")**: `aⁿ + bⁿ = cⁿ`, caso
  particular `x² + y² = R²` para o círculo. Base conceitual de todo o livro
  (não numerada, seção "On Arithmetic and Geometric Means").
- **Binômio de Newton, forma reduzida "modulo médias geométricas"**:
  `xⁿ + yⁿ ≡ (x+y)ⁿ (mod termos com xy)`.

## Capítulo 4 — Curvas e Superfícies de Lamé

- **Eq. 4.1** — Superelipse (equação cartesiana de Lamé, 1818):
  `|x/A|ⁿ + |y/B|ⁿ = 1`, `n` inteiro, `A, B > 0`. Para `A=B` dá o supercírculo.
- **Eq. 4.2** — Família generalizada de cônicas de Lamé (sem valor absoluto),
  todas da forma `|x/A|ⁿ + |y/B|ⁿ = 1` variando `n`:
  - `n = 1`: reta — `x/A + y/B = 1`
  - `n = -1`: hipérbole — `A/x + B/y = 1`
  - `n = 2`: elipse — `(x/A)² + (y/B)² = 1`
  - `n = 1/2`: parábola — `√(x/A) + √(y/B) = 1`
- **Eq. 4.3** — Curva "interscendente" de Euzet/Lamé com expoente irracional:
  `(x/A)^√2 + (y/B)^√2 = 1`.
- Curva geral de Lamé (n-cubo): `xⁿ + yⁿ = zⁿ`.

## Capítulo 5 — Curvas, Superfícies e Transformações de Gielis

- **Eq. 5.1–5.2** — Superelipse em coordenadas polares (substituição
  `x = ρ(θ)cosθ`, `y = ρ(θ)sinθ`):
  `ρ(θ) = 1 / ( |cosθ/A|ⁿ + |sinθ/B|ⁿ )^(1/n)`
- **Eq. 5.3–5.4** — Teorema de Pitágoras generalizado com seno/cosseno de
  Lamé (`ncos`, `nsin`):
  `(ncosθ)ⁿ + (nsinθ)ⁿ = 1`, com
  `ncosθ = cosθ / (|cosθ|ⁿ + |sinθ|ⁿ)^(1/n)`,
  `nsinθ = sinθ / (|cosθ|ⁿ + |sinθ|ⁿ)^(1/n)`.
- **Eq. 5.5–5.6** — Fólio de Descartes como transformação de Gielis
  (`n1=1`, `n2=n3=3`, `f(θ)=3a·sinθ·cosθ`):
  `ρ(θ) = 3a·sinθ·cosθ / (cos³θ + sin³θ)`.
- **Eq. 5.7** — Forma intermediária de Lamé→Gielis (expoentes independentes
  no cosseno/seno, `n2 ≠ n3`):
  `ρ(θ) = 1 / ( |cosθ|^n2 + |sinθ|^n3 )^(1/n1)`
- **Eq. 5.8 — A Superfórmula (Gielis Superformula / GSF)**, a equação central
  do livro:

  `ρ(θ; m, A, B, n1, n2, n3) = [ |cos(mθ/4)/A|^n2 + |sin(mθ/4)/B|^n3 ]^(−1/n1)`

  com `A, B, n1 > 0` reais e `m, n2, n3` reais.
- **Eq. 5.9** — Variante com `m1` no termo cosseno e `m2` no termo seno
  (permite assimetria/hipérboles com sinal negativo):
  `ρ = [ |cos(m1θ/4)/A|^n2 ± |sin(m2θ/4)/B|^n3 ]^(−1/n1)`
- **Eq. 5.10–5.11** ⚠ reconstrução parcial — limite que gera polígonos
  regulares quando `n1, n2, n3 → ∞` com um valor de `n` dependente de `m`
  (`n ∝ 1/log₂cos(π/m)`). No pacote de código isso é oferecido como
  **aproximação prática** (`n` grande, ex. 60–200) em vez da fórmula exata do
  limite, porque a extração do PDF corrompeu o expoente exato — ver página 63
  do livro para a fórmula precisa antes de citar academicamente.
- **Eq. 5.12 — Transformação de Gielis**: generaliza a Superfórmula para
  transformar *qualquer* função radial positiva `f(θ)` (não apenas um
  círculo de raio constante):

  `ρ(θ) = f(θ) / [ |cos(mθ/4)/A|^n2 + |sin(mθ/4)/B|^n3 ]^(1/n1)`

  Casos notáveis usados no livro: `f(θ)=R` (círculo/supercírculo),
  `f(θ)=a·θ` (espiral de Arquimedes), `f(θ)=e^(kθ)` (espiral logarítmica,
  concha do Nautilus).
- **Eq. 5.13** — Área da supershape: `Area = (m/... ) ∫₀^(2π/m) ρ(θ)² dθ`
  (integral numérica no código).
- **Eq. 5.14** — Momento polar de inércia: `Ip = (m/...) ∫₀^(2π/m) ρ(θ)⁴ dθ`.
- **Eq. 5.15** — Perímetro/circunferência: `s = (m/...) ∫₀^(2π/m) √(ρ² + ρ'²) dθ`.
- **Eq. 5.16** — Superelipsoide em coordenadas esféricas (extensão direta de
  `xᵖ/a + yᵖ/b + zᶜᵖ/c = 1`):
  `(r·sinθ·cosφ/a)^p + (r·sinθ·sinφ/b)^p + (r·cosθ/c)^p = 1`
- **Eq. 5.17** — Superfície de Gielis 3D generalizada (parâmetros reais
  independentes em θ e φ, `a(θ,φ)` função de modulação).
- **Eq. 5.18–5.19** — Esfera como "produto esférico" de um círculo completo
  `μ(θ)=(cosθ, sinθ)` (`−π/2<θ<π/2`) e um semicírculo `η(φ)=(cosφ, sinφ)`
  (`−π<φ<π`):
  `x = R·cosθ·cosφ`, `y = R·sinθ·cosφ`, `z = R·sinφ`.
- **Eq. 5.20 — Produto esférico de duas 2D-supershapes** (define qualquer
  superfície 3D de Gielis a partir de duas seções perpendiculares
  `ρ1(θ)`, `ρ2(φ)`):
  `x = ρ1(θ)cosθ · ρ2(φ)cosφ`, `y = ρ1(θ)sinθ · ρ2(φ)cosφ`, `z = ρ2(φ)sinφ`.

## Capítulo 6 — Pythagorean-Compact (generalizações e Funções-R)

- **Eq. 6.1** ⚠ não implementada — variante com funções elípticas de Jacobi
  no argumento de cos/sin (Chacón); os símbolos exatos das "amplitudes"
  `U_{I,II}`, `W_{I,II}` não puderam ser recuperados com confiança do PDF.
  Ver [128] no livro.
- **Eq. 6.2** — Superfórmula com deslocamento de fase `ε`:
  `ρ(θ) = f(θ) / [ |cos(m(θ+ε)/4)/A|^n2 + |sin(m(θ+ε)/4)/B|^n3 ]^(1/n1)`
- **Eq. 6.3** — Generalização com funções arbitrárias `f1(θ), f2(θ)` no lugar
  do ângulo puro e modulador `c(θ)`:
  `ρ(θ) = c(θ) / [ |cos(m1·f1(θ)/4)/A|^n2 + |sin(m2·f2(θ)/4)/B|^n3 ]^(1/n1)`
- **Eq. 6.4** — Curvas "k-type" (soma de k supershapes com o mesmo centro):
  `ρ(θ) = Σᵢ fᵢ(θ) / [ |cos(mi1·θ/4)/Ai|^ni2 + |sin(mi2·θ/4)/Bi|^ni3 ]^(1/ni1)`
- **Eq. 6.5** — Série "super-Fourier" (cada termo de Fourier vira uma
  supershape):
  `ρ(θ) = ρ₀a₀ + Σₖ [ aₖρₖcos(mkθ/4) + bₖρₖsin(mkθ/4) ]`
- **Eq. 6.6** — Funções-R de Rvachev, forma geral `Rα`:
  `Rα(s1,s2) = (1/(1+α))·[ (s1+s2) ± √(s1²+s2²−2α·s1·s2) ]`, `−1<α<1`
  (`+` para disjunção/união, `−` para conjunção/interseção).
- **Eq. 6.7** — Caso `α=1` (reduz a `max`/`min`):
  `R₁(s1,s2) = ½[(s1+s2) ± |s1−s2|] = max(s1,s2)` ou `min(s1,s2)`.
- **Eq. 6.8–6.9** — Caso `α=0`:
  `R₀∧(s1,s2) = s1+s2 − √(s1²+s2²)` (conjunção/interseção),
  `R₀∨(s1,s2) = s1+s2 + √(s1²+s2²)` (disjunção/união).
- **Eq. 6.10** — Sistema `Rm` (garante diferenciabilidade até ordem `m`):
  `Rm₀(s1,s2) = [ (s1+s2) − √(s1²+s2²) ] · (s1²+s2²)^(m/2)`
- **Eq. 6.11–6.13** — Sistema `Rp` (Shapiro/Rvachev):
  `Rp(s1∨s2) = (s1+s2) + (|s1|^p+|s2|^p)^(1/p)` (disjunção)
  `Rp(s1∧s2) = (s1+s2) − (|s1|^p+|s2|^p)^(1/p)` (conjunção)
  `Rp(s1↔s2) = s1·s2 / (|s1|^p+|s2|^p)^(1/p)` (equivalência)
- **Eq. 6.14** — Derivada parcial no sistema `Rp`:
  `∂f/∂xᵢ = 1 ± xᵢ^(p−1) / (x1^p+x2^p)^((p−1)/p)`, `i=1,2`.
- Curvas de 1 termo (`k=1`) citadas: cardioide `ρ=1±cosθ`/`1±sinθ`; curvas
  de Rhodonea/Grandi `ρ=a·cos(mθ)` ou `a·sin(mθ)`; lemniscata de Bernoulli
  `ρ = a√(2cos2θ)`.

## Capítulo 7 — Comprimentos intrínsecos e extrínsecos generalizados

- **Eq. 7.1** — Caso particular da Eq. 5.9 com `B=1, m=4`.
- **Eq. 7.2–7.5** — Integrais elípticas completas (1ª e 2ª espécie) e a
  Média Aritmético-Geométrica de Gauss `M(m,n)`; não centrais ao pacote de
  formas, mas incluídas como utilidades (`agm`, integrais elípticas via
  `scipy.special`).
- **Eq. 7.12** — Métrica de Riemann–Finsler em `ℓp`, dimensão `n`:
  `ds = ( Σᵢ (dxᵢ)^p )^(1/p)`
- **Eq. 7.13** — Caso `p=2`: métrica Euclidiana usual
  `ds = √( Σᵢ (dxᵢ)² )`.
- **Eq. 7.14** — Métrica de curvatura constante `k` (tipo disco de Poincaré /
  espaço hiperbólico-elíptico), dimensão `n`:
  `ds = √(Σᵢ dxᵢ²) / [ 1 + (k/4)·Σᵢxᵢ² ]`
- **Eq. 7.15** — Métrica FLRW (Friedmann–Lemaître–Robertson–Walker),
  cosmologia:
  `ds² = −dt² + a(t)²·(dx²+dy²+dz²) / [1 + (k/4)(x²+y²+z²)]²`
- **Eq. 7.16–7.17** — Polinômios de Chebyshev de 1ª e 2ª espécie:
  `Tm(cosθ) = cos(mθ)`, `Uₘ₋₁(cosθ) = sin(mθ)/sinθ`.
- **Eq. 7.18, 7.22** — Superfórmula reescrita com polinômios de Chebyshev
  (`x = cosθ`):
  `ρ(x) = 1 / [ |Tm(x)|^n2 + | √(1−x²)·Uₘ₋₁(x) |^n3 ]^(1/n1)`
- **Eq. 7.19** ⚠ não implementada com confiança — relação entre números de
  Lucas/Fibonacci e Chebyshev em argumento imaginário
  (`Lₙ = 2·i⁻ⁿ·Tₙ(i)`, `Fₙ₊₁ = i⁻ⁿ·Uₙ(i)`); mantida apenas como referência
  textual, não incluída no código por risco de erro de sinal/índice na
  reconstrução do OCR.
- **Eq. 7.20–7.21** — "Curvas de Grandi" generalizadas (rosáceas via
  transformação de Gielis, numerador de período completo):
  `ρ(θ) = cos(mθ) / [ |cos(mθ/4)/A|^n2 + |sin(mθ/4)/B|^n3 ]^(1/n1)` (e o
  análogo com `sin(mθ)` no numerador).

## Capítulo 9 — Condições de Curvatura Natural

- **Eq. 9.1** — Fórmulas de Frenet–Serret(–Pagani):
  `t' = κn`, `n' = −κt + τb`, `b' = −τn`.
- **Eq. 9.2** — Forma com vetor de Darboux `d = κb + τt`:
  `t' = d×t`, `n' = d×n`, `b' = d×b`.
- **Eq. 9.3** — Curvatura de Casorati: `C = (κ1² + κ2²)/2`.
- **Eq. 9.4** — Índice de forma de Koenderink & van Doorn:
  `r = (2/π)·arctan( (κ1+κ2)/(κ1−κ2) )`.
- **Eq. 9.5–9.7** — Expansões de `H²` (Willmore) em termos de `κ1, κ2`,
  incluindo `H² = (κ1²+κ2²)/2 + (κ1κ2)`... e a forma via média geométrica
  `√((κ1κ2)²) = |K|`.
- **Eq. 9.8** — Teorema de Beltrami (Laplaciano ↔ curvatura média `H` em
  `n` dimensões): `Δx = −n·H`.
- **Eq. 9.9** — Círculo como caso trivial: `√(cos²θ+sin²θ)·ρ(θ) = 1`,
  `κ_C = 1/R`.
- **Eq. 9.10 (Definição 9.1)** — "Curvatura" via curva de Lamé:
  `κ_L(θ) = 1 / [ ρ(θ)·(|cosθ|ⁿ+|sinθ|ⁿ)^(1/n) ]`
- **Eq. 9.11 (Definição 9.2)** — "Curvatura" via curva de Gielis:
  `κ_G(θ) = (|cos(mθ/4)/A|^n2 + |sin(mθ/4)/B|^n3)^(1/n1) / ρ(θ)`
- **Eq. 9.12 (Corolário 9.3)** ⚠ mesma reconstrução incerta de 5.10/5.11.
- **Eq. 9.13–9.15** — Lei generalizada do inverso da potência `n`-ésima:
  `|cosθ|ⁿ + |sinθ|ⁿ = ρ(θ)^(−n)` (Lamé) e o análogo para Gielis com
  `A,B,m,n1,n2,n3`.
- **Eq. 9.16–9.18** — Teorema de Euler da curvatura normal:
  `κn(θ) = κ1cos²θ + κ2sin²θ = (κ1+κ2)/2 + (κ1−κ2)/2·cos(2θ)`
- **Eq. 9.19** — Derivadas: `∂κn/∂θ = −(κ1−κ2)sin(2θ)`.
- **Eq. 9.20–9.21** — Transformação de Gielis aplicada a um círculo e a uma
  espiral logarítmica (casos particulares da Eq. 5.12 com `f(θ)=R` e
  `f(θ)=e^(kθ)`).

## Capítulo 10 — Folhas de Bambu e Anéis de Crescimento

- **Eq. 10.1 — Modelo de 2 parâmetros para folhas de bambu** (caso
  extremamente simplificado da Superfórmula: `A=B=1`, `m=4`,
  `n1=n2=n3=n`, escala `l`):
  `ρ(θ) = l / [ |cosθ|ⁿ + |sinθ|ⁿ ]^(1/n)` — 1 parâmetro de forma `n`
  (tipicamente entre 0.02 e 0.1 para bambus) e 1 de tamanho `l`.
  ⚠ **incerteza de reconstrução**: a extração do PDF deixou ambíguo se o
  expoente interno é este `n` (adotado no código, por ser a redução mais
  natural de "um parâmetro só" da Superfórmula) ou um `4` fixo com `n` só
  no índice da raiz. Com a leitura adotada, os valores de `n` citados no
  livro (0.02–0.1) geram uma curva bem extrema — próxima de `l` em 0° e
  90°, colapsando quase a zero entre esses ângulos — em vez de uma
  silhueta lisa de folha. Ver a nota em `gielis/models.py:bamboo_leaf_radius`
  e `examples/rpg_plant.py` (que evita essa equação para gerar malhas de
  folha, usando um perfil próprio).
- **Eq. 10.2 — Modelo de anéis de crescimento (Lamé/superelipse)**:
  `ρ(θ) = 1 / [ |cosθ/a|ⁿ + |sinθ/b|ⁿ ]^(1/n)`, todos os expoentes iguais
  a `n`, com semi-eixos `a, b` independentes.

## Capítulo 11 — Flocos de Neve e Asclepiadáceas

- **Eq. 11.1** — Curvatura média anisotrópica (CAMC, D'Arcy
  Thompson/Koiso–Palmer):
  `K = T1/R1 + T2/R2 = T1·κ1 + T2·κ2 = constante`

## Capítulo 12 — Conclusão

Sem novas equações numeradas; é uma síntese filosófica/programática do livro.

---

## Correspondência equação → código

| Equação(ões) | Módulo Python | Função |
|---|---|---|
| 4.1, 4.2, 4.3 | `gielis/lame.py` | `superellipse_implicit`, `generalized_conic`, `interscendent_curve` |
| 5.1–5.4 | `gielis/lame.py` | `lame_polar_radius`, `lame_cos`, `lame_sin`, `generalized_pythagorean_residual` |
| 5.7–5.9 | `gielis/superformula.py` | `superformula`, `superformula_asymmetric` |
| 5.12, 6.2, 6.3, 9.20, 9.21 | `gielis/superformula.py` | `gielis_transform` |
| 5.13–5.15 | `gielis/shape_metrics.py` | `area`, `polar_moment_of_inertia`, `circumference` |
| 5.16–5.20 | `gielis/surfaces.py` | `superellipsoid`, `spherical_product`, `gielis_surface` |
| 6.4 | `gielis/series.py` | `k_type_sum` |
| 6.5 | `gielis/series.py` | `super_fourier_series` |
| 6.6–6.14 | `gielis/rfunctions.py` | `r_alpha`, `r_conjunction_p`, `r_disjunction_p`, `r_equivalence_p`, `r0_conjunction`, `r0_disjunction`, `rm_conjunction` |
| 7.12–7.15 | `gielis/curvature.py` | `lp_metric`, `constant_curvature_metric`, `flrw_metric_factor` |
| 7.16–7.18, 7.22 | `gielis/chebyshev.py` | `chebyshev_t`, `chebyshev_u`, `gielis_chebyshev` |
| 7.20, 7.21 | `gielis/curves.py` | `grandi_rose` |
| 9.1–9.2 | `gielis/curvature.py` | `frenet_serret` |
| 9.3–9.8 | `gielis/curvature.py` | `casorati_curvature`, `shape_index`, `willmore_h2`, `beltrami_mean_curvature` |
| 9.9–9.15 | `gielis/curvature.py` | `circle_curvature_measure`, `lame_curvature_measure`, `gielis_curvature_measure` |
| 9.16–9.19 | `gielis/curvature.py` | `euler_normal_curvature` |
| 11.1 | `gielis/curvature.py` | `anisotropic_mean_curvature` |
| 10.1 | `gielis/models.py` | `bamboo_leaf_radius` |
| 10.2 | `gielis/models.py` | `tree_ring_radius` |
| curvas de 1 termo (cardioide, Rhodonea, lemniscata), ouro/Fibonacci | `gielis/curves.py` | `cardioid`, `rose_curve`, `lemniscate`, `archimedean_spiral`, `logarithmic_spiral`, `golden_angle`, `vogel_phyllotaxis` |
