extends RefCounted

## Biblioteca de props 3D da torre: monta, só com formas primitivas (caixas,
## cilindros, esferas, uma cápsula), os objetos que o gerador sorteia pro piso
## de cada andar (`prop` em `ynn.tables.TORRE_ANDARES` / `TORRE_TOPO`).
##
## Convenção de espaço: tudo é criado como filho de um `Node3D` (`root`) em
## coordenadas locais. O chão é y = 0, +X acompanha a parede (tangente) e +Z
## aponta pro centro da torre (a "frente" do objeto). Cada construtor devolve a
## altura aproximada do objeto em metros, usada pra posicionar o rótulo acima.
##
## Despacho: `build(prop, root)` faz um `match` pelo nome. Cada nome chama
## `_<nome>`, exceto: "bau" -> `_bau(root, 1.0)`; "estante" ->
## `_estante(root, 0.0, 1.0)`; "biblioteca" -> `_biblioteca` (três estantes
## lado a lado). Nome desconhecido não monta nada e devolve 0.0 (talvez o
## `prop` seja tratado no Main.gd).
##
## Cores e materiais: as constantes (MADEIRA, OURO, METAL, ...) são a paleta
## base; cores avulsas são `Color` literais nos construtores. `_mat` cria o
## `StandardMaterial3D` (sem culling; alfa < 1 liga transparência; emissão > 0
## faz brilhar). `_box`, `_cyl` e `_sphere` criam o mesh primitivo e o prendem
## ao `root` com esse material via `_add`.
##
## Pra incluir um objeto novo: adicione um braço em `build` e uma função
## `_<nome>` aqui, e use o mesmo nome em `prop` nas tabelas (há um teste que
## confere que todo `prop` das tabelas aparece neste arquivo ou no Main.gd).

const MADEIRA := Color(0.42, 0.27, 0.14)
const MADEIRA_ESCURA := Color(0.28, 0.18, 0.1)
const OURO := Color(0.95, 0.78, 0.2)
const METAL := Color(0.62, 0.64, 0.68)
const BRONZE := Color(0.72, 0.48, 0.2)
const OSSO := Color(0.9, 0.88, 0.8)


## Ponto de entrada: monta o prop de nome `prop` sob `root` chamando o
## construtor correspondente (ver tabela de despacho no topo do arquivo).
## Retorna a altura aproximada do objeto em metros; 0.0 se o nome é desconhecido.
static func build(prop: String, root: Node3D) -> float:
	match prop:
		"bau":
			return _bau(root, 1.0)
		"bau_grande":
			return _bau_grande(root)
		"criatura":
			return _criatura(root)
		"mobilia":
			return _mobilia(root)
		"estante":
			return _estante(root, 0.0, 1.0)
		"ninhos":
			return _ninhos(root)
		"teias":
			return _teias(root)
		"esqueleto":
			return _esqueleto(root)
		"caixotes":
			return _caixotes(root)
		"quadros":
			return _quadros(root)
		"espelho":
			return _espelho(root)
		"sino":
			return _sino(root)
		"telescopio":
			return _telescopio(root)
		"camera_escura":
			return _camera_escura(root)
		"biblioteca":
			return _biblioteca(root)
		"armadilha":
			return _armadilha(root)
		"armadura":
			return _armadura(root)
		"maquina":
			return _maquina(root)
		"espelho_sinal":
			return _espelho_sinal(root)
		"caixao":
			return _caixao(root)
		"lampada":
			return _lampada(root)
	return 0.0


# --- primitivas ---------------------------------------------------------

## Cria o material básico: `color` com `alpha` (< 1.0 liga transparência) e,
## se `emissao` > 0, o objeto brilha com a própria cor nessa intensidade.
static func _mat(color: Color, alpha: float = 1.0, emissao: float = 0.0) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = Color(color.r, color.g, color.b, alpha)
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if alpha < 1.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	if emissao > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emissao
	return m


## Cria um `MeshInstance3D` com `mesh` e `mat`, na posição/rotação (radianos)
## locais `pos`/`rot`, adiciona a `parent` e o devolve.
static func _add(parent: Node3D, mesh: Mesh, pos: Vector3, mat: Material, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var inst = MeshInstance3D.new()
	inst.mesh = mesh
	inst.position = pos
	inst.rotation = rot
	inst.material_override = mat
	parent.add_child(inst)
	return inst


## Caixa de tamanho `size` (x, y, z) centrada em `pos`; `rot` em radianos.
## Cor de `color`, com `alpha` opcional (vidro, teia).
static func _box(parent: Node3D, size: Vector3, pos: Vector3, color: Color, rot: Vector3 = Vector3.ZERO, alpha: float = 1.0) -> MeshInstance3D:
	var mesh = BoxMesh.new()
	mesh.size = size
	return _add(parent, mesh, pos, _mat(color, alpha), rot)


## Cilindro (ou cone, se os raios diferem) com eixo ao longo de Y, centrado em
## `pos`; `raio_topo`/`raio_base` em metros, `rot` em radianos pra deitá-lo.
static func _cyl(parent: Node3D, raio_topo: float, raio_base: float, altura: float, pos: Vector3, color: Color, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mesh = CylinderMesh.new()
	mesh.top_radius = raio_topo
	mesh.bottom_radius = raio_base
	mesh.height = altura
	mesh.radial_segments = 12
	return _add(parent, mesh, pos, _mat(color), rot)


## Esfera de raio `raio` centrada em `pos`. `achatamento` multiplica a altura
## (0.5 = meia-altura, vira calota/ovo); `emissao` > 0 faz a esfera brilhar.
static func _sphere(parent: Node3D, raio: float, pos: Vector3, color: Color, achatamento: float = 1.0, emissao: float = 0.0) -> MeshInstance3D:
	var mesh = SphereMesh.new()
	mesh.radius = raio
	mesh.height = raio * 2.0 * achatamento
	mesh.radial_segments = 12
	mesh.rings = 6
	return _add(parent, mesh, pos, _mat(color, 1.0, emissao))


# --- objetos dos andares ------------------------------------------------

## Baú de madeira com tampa e fecho dourado, pequeno. `k` é a escala uniforme
## (1.0 = tamanho normal). Retorna a altura em metros (0.55 * k).
static func _bau(root: Node3D, k: float) -> float:
	_box(root, Vector3(0.7, 0.4, 0.45) * k, Vector3(0, 0.2 * k, 0), MADEIRA)
	_box(root, Vector3(0.72, 0.1, 0.47) * k, Vector3(0, 0.45 * k, 0), MADEIRA_ESCURA)
	_sphere(root, 0.06 * k, Vector3(0, 0.38 * k, 0.24 * k), OURO)
	return 0.55 * k


## Baú grande com monte de ouro (esfera achatada) e moedas soltas no chão
## à frente. Retorna a altura em metros (0.8).
static func _bau_grande(root: Node3D) -> float:
	_box(root, Vector3(0.95, 0.5, 0.6), Vector3(0, 0.25, -0.1), MADEIRA)
	_sphere(root, 0.42, Vector3(0, 0.55, -0.1), OURO, 0.5)
	_cyl(root, 0.12, 0.12, 0.04, Vector3(-0.3, 0.02, 0.4), OURO)
	_cyl(root, 0.12, 0.12, 0.04, Vector3(-0.15, 0.06, 0.45), OURO, Vector3(0.2, 0, 0.1))
	_cyl(root, 0.12, 0.12, 0.04, Vector3(0.3, 0.02, 0.38), OURO)
	return 0.8


## Criatura simples: corpo de cápsula avermelhada, cabeça esférica e dois
## olhos amarelos virados pra +Z. Retorna a altura em metros (1.5).
static func _criatura(root: Node3D) -> float:
	var corpo = CapsuleMesh.new()
	corpo.radius = 0.26
	corpo.height = 1.1
	_add(root, corpo, Vector3(0, 0.55, 0), _mat(Color(0.7, 0.2, 0.2)))
	_sphere(root, 0.2, Vector3(0, 1.25, 0.05), Color(0.8, 0.3, 0.25))
	_sphere(root, 0.04, Vector3(-0.08, 1.28, 0.22), Color(1, 1, 0.6))
	_sphere(root, 0.04, Vector3(0.08, 1.28, 0.22), Color(1, 1, 0.6))
	return 1.5


## Mesa de quatro pés e, ao lado, uma cadeira (assento e encosto girados
## um pouco em Y), tudo em madeira escura. Retorna a altura em metros (0.8).
static func _mobilia(root: Node3D) -> float:
	var cor = MADEIRA_ESCURA
	_box(root, Vector3(0.9, 0.05, 0.55), Vector3(-0.25, 0.7, 0), cor)
	for dx in [-0.4, 0.4]:
		for dz in [-0.22, 0.22]:
			_cyl(root, 0.035, 0.035, 0.7, Vector3(-0.25 + dx, 0.35, dz), cor)
	_box(root, Vector3(0.4, 0.05, 0.4), Vector3(0.6, 0.4, 0), cor, Vector3(0, 0.3, 0))
	_box(root, Vector3(0.4, 0.5, 0.05), Vector3(0.6, 0.65, -0.2), cor, Vector3(0, 0.3, 0))
	for dx in [-0.17, 0.17]:
		for dz in [-0.17, 0.17]:
			_cyl(root, 0.03, 0.03, 0.4, Vector3(0.6 + dx, 0.2, dz), cor)
	return 0.8


## Estante de madeira com 3 prateleiras de 5 livros coloridos. `deslocamento_x`
## move a estante ao longo da parede; `k` escala a largura (usada pela
## biblioteca). Retorna a altura em metros (1.8).
static func _estante(root: Node3D, deslocamento_x: float, k: float) -> float:
	_box(root, Vector3(1.0 * k, 1.8, 0.32), Vector3(deslocamento_x, 0.9, 0), MADEIRA_ESCURA)
	var cores = [Color(0.6, 0.2, 0.2), Color(0.2, 0.35, 0.55), Color(0.25, 0.5, 0.3), Color(0.7, 0.55, 0.2), Color(0.45, 0.25, 0.5)]
	for linha in range(3):
		for i in range(5):
			var x = deslocamento_x + (i - 2) * 0.17 * k
			_box(root, Vector3(0.12 * k, 0.3, 0.22), Vector3(x, 0.4 + linha * 0.5, 0.1), cores[(i + linha) % cores.size()])
	return 1.8


## Três ninhos baixos (esferas achatadas marrons), cada um com dois ovos
## claros por cima. Retorna a altura em metros (0.3).
static func _ninhos(root: Node3D) -> float:
	for pos in [Vector3(-0.4, 0, 0.1), Vector3(0.1, 0, -0.1), Vector3(0.5, 0, 0.15)]:
		_sphere(root, 0.22, pos + Vector3(0, 0.07, 0), Color(0.4, 0.3, 0.15), 0.5)
		_sphere(root, 0.05, pos + Vector3(-0.05, 0.17, 0), Color(0.95, 0.95, 0.9))
		_sphere(root, 0.05, pos + Vector3(0.06, 0.16, 0.03), Color(0.95, 0.95, 0.9))
	return 0.3


## Dois painéis finos e translúcidos, cruzados e rotacionados, imitando
## teias de aranha. Retorna a altura em metros (1.6).
static func _teias(root: Node3D) -> float:
	_box(root, Vector3(1.3, 1.5, 0.01), Vector3(0, 0.85, 0), Color(0.95, 0.95, 0.95), Vector3(0, 0, 0.2), 0.35)
	_box(root, Vector3(1.3, 1.5, 0.01), Vector3(0.1, 0.8, 0.05), Color(0.95, 0.95, 0.95), Vector3(0, 1.0, -0.15), 0.3)
	return 1.6


## Esqueleto em pé: crânio, coluna, três costelas, duas pernas e duas
## hastes de metal verticais ao lado. Retorna a altura em metros (1.6).
static func _esqueleto(root: Node3D) -> float:
	_sphere(root, 0.13, Vector3(0, 1.45, 0), OSSO)
	_cyl(root, 0.04, 0.04, 0.7, Vector3(0, 1.0, 0), OSSO)
	for y in [1.15, 1.05, 0.95]:
		_box(root, Vector3(0.3, 0.03, 0.12), Vector3(0, y, 0), OSSO)
	for dx in [-0.1, 0.1]:
		_cyl(root, 0.035, 0.035, 0.6, Vector3(dx, 0.3, 0), OSSO)
	for dx in [-0.3, 0.3]:
		_cyl(root, 0.015, 0.015, 0.6, Vector3(dx, 1.5, 0), METAL)
	return 1.6


## Pilha de três caixotes de madeira clara, dois embaixo e um em cima, com
## pequenas rotações em Y. Retorna a altura em metros (0.9).
static func _caixotes(root: Node3D) -> float:
	var cor = Color(0.7, 0.55, 0.35)
	_box(root, Vector3(0.5, 0.5, 0.5), Vector3(-0.3, 0.25, 0), cor)
	_box(root, Vector3(0.45, 0.45, 0.45), Vector3(0.3, 0.225, 0.05), cor, Vector3(0, 0.4, 0))
	_box(root, Vector3(0.4, 0.4, 0.4), Vector3(0, 0.7, 0), cor, Vector3(0, 0.2, 0))
	return 0.9


## Três quadros com moldura dourada e tela colorida, levemente inclinados
## pra trás, lado a lado. Retorna a altura em metros (0.6).
static func _quadros(root: Node3D) -> float:
	var telas = [Color(0.45, 0.25, 0.55), Color(0.2, 0.4, 0.55), Color(0.55, 0.3, 0.3)]
	for i in range(3):
		var x = (i - 1) * 0.42
		_box(root, Vector3(0.36, 0.5, 0.04), Vector3(x, 0.3, 0), OURO, Vector3(-0.15, 0, 0))
		_box(root, Vector3(0.3, 0.44, 0.045), Vector3(x, 0.3, 0.005), telas[i], Vector3(-0.15, 0, 0))
	return 0.6


## Espelho de corpo inteiro: moldura dourada e vidro translúcido azulado
## (alfa 0.75) um pouco à frente. Retorna a altura em metros (1.8).
static func _espelho(root: Node3D) -> float:
	_box(root, Vector3(0.8, 1.8, 0.06), Vector3(0, 0.9, 0), OURO)
	_box(root, Vector3(0.7, 1.7, 0.07), Vector3(0, 0.9, 0.005), Color(0.7, 0.9, 0.95), Vector3.ZERO, 0.75)
	return 1.8


## Sino de bronze pendurado numa trave horizontal (eixo em X) sustentada por
## dois postes de madeira, com badalo de metal. Retorna a altura em metros (1.9).
static func _sino(root: Node3D) -> float:
	for dx in [-0.45, 0.45]:
		_cyl(root, 0.05, 0.05, 1.8, Vector3(dx, 0.9, 0), MADEIRA_ESCURA)
	_cyl(root, 0.05, 0.05, 1.0, Vector3(0, 1.8, 0), MADEIRA_ESCURA, Vector3(0, 0, PI / 2.0))
	_cyl(root, 0.12, 0.38, 0.6, Vector3(0, 1.4, 0), BRONZE)
	_sphere(root, 0.07, Vector3(0, 1.05, 0), METAL)
	return 1.9


## Telescópio: tripé de três pernas de metal e tubo de bronze inclinado
## apontando pra cima (-Z), com a ocular na ponta de trás. Retorna a altura em
## metros (1.7).
static func _telescopio(root: Node3D) -> float:
	for ang in [0.0, 2.1, 4.2]:
		_cyl(root, 0.02, 0.02, 1.1, Vector3(cos(ang) * 0.15, 0.55, sin(ang) * 0.15), METAL, Vector3(sin(ang) * 0.25, 0, -cos(ang) * 0.25))
	_cyl(root, 0.07, 0.07, 1.3, Vector3(0, 1.2, -0.25), BRONZE, Vector3(-1.0, 0, 0))
	_cyl(root, 0.045, 0.045, 0.2, Vector3(0, 0.78, 0.2), BRONZE, Vector3(-1.0, 0, 0))
	return 1.7


## Câmara escura: caixa preta com lente de bronze virada pra +Z e uma tela
## clara sobre o tampo. Retorna a altura em metros (1.0).
static func _camera_escura(root: Node3D) -> float:
	_box(root, Vector3(1.0, 0.9, 0.9), Vector3(0, 0.45, 0), Color(0.15, 0.15, 0.18))
	_cyl(root, 0.12, 0.12, 0.15, Vector3(0, 0.5, 0.5), BRONZE, Vector3(PI / 2.0, 0, 0))
	_box(root, Vector3(0.5, 0.03, 0.5), Vector3(0, 0.92, 0), Color(0.9, 0.9, 0.85))
	return 1.0


## Biblioteca: três estantes (escala 0.85) lado a lado em x = -0.85, 0 e
## 0.85. Retorna a altura em metros (1.8).
static func _biblioteca(root: Node3D) -> float:
	_estante(root, -0.85, 0.85)
	_estante(root, 0.0, 0.85)
	_estante(root, 0.85, 0.85)
	return 1.8


## Armadilha de chão: placa vermelha achatada com quatro espinhos de metal
## nos cantos. Retorna a altura em metros (0.2).
static func _armadilha(root: Node3D) -> float:
	_box(root, Vector3(0.9, 0.03, 0.9), Vector3(0, 0.015, 0), Color(0.55, 0.15, 0.12))
	for dx in [-0.35, 0.35]:
		for dz in [-0.35, 0.35]:
			_cyl(root, 0.0, 0.04, 0.14, Vector3(dx, 0.1, dz), METAL)
	return 0.2


## Armadura em pedestal: base, pernas, peitoral, braços, elmo esférico e
## penacho vermelho, quase tudo em metal. Retorna a altura em metros (1.75).
static func _armadura(root: Node3D) -> float:
	_box(root, Vector3(0.5, 0.15, 0.5), Vector3(0, 0.075, 0), Color(0.2, 0.2, 0.22))
	for dx in [-0.1, 0.1]:
		_cyl(root, 0.08, 0.08, 0.6, Vector3(dx, 0.45, 0), METAL)
	_box(root, Vector3(0.45, 0.55, 0.25), Vector3(0, 0.98, 0), METAL)
	for dx in [-0.3, 0.3]:
		_cyl(root, 0.05, 0.05, 0.5, Vector3(dx, 1.0, 0), METAL, Vector3(0, 0, dx * 0.7))
	_sphere(root, 0.16, Vector3(0, 1.4, 0), METAL)
	_box(root, Vector3(0.05, 0.18, 0.2), Vector3(0, 1.6, 0), Color(0.7, 0.15, 0.15))
	return 1.75


## Máquina (tipo tear/prensa): corpo de madeira, duas lâminas largas
## empilhadas, duas rodas pretas (cilindros deitados) e uma barra de metal.
## Retorna a altura em metros (0.9).
static func _maquina(root: Node3D) -> float:
	_box(root, Vector3(0.3, 0.3, 0.9), Vector3(0, 0.45, 0), Color(0.55, 0.4, 0.25))
	_box(root, Vector3(1.6, 0.03, 0.4), Vector3(0, 0.75, 0), Color(0.9, 0.85, 0.7))
	_box(root, Vector3(1.6, 0.03, 0.4), Vector3(0, 0.45, 0.05), Color(0.9, 0.85, 0.7))
	for dx in [-0.25, 0.25]:
		_cyl(root, 0.12, 0.12, 0.05, Vector3(dx, 0.14, 0.2), Color(0.15, 0.15, 0.15), Vector3(0, 0, PI / 2.0))
	_box(root, Vector3(0.7, 0.04, 0.04), Vector3(0, 0.45, 0.48), METAL)
	return 0.9


## Espelho de sinalização: haste de metal sobre base de madeira, com disco
## prateado inclinado (cilindro achatado) no alto. Retorna a altura em metros
## (1.8, valor folgado pro rótulo).
static func _espelho_sinal(root: Node3D) -> float:
	_cyl(root, 0.04, 0.04, 1.2, Vector3(0, 0.6, 0), METAL)
	_cyl(root, 0.45, 0.45, 0.05, Vector3(0, 1.35, 0), Color(0.85, 0.88, 0.9), Vector3(1.2, 0, 0))
	_box(root, Vector3(0.5, 0.06, 0.4), Vector3(0, 0.03, 0), MADEIRA_ESCURA)
	return 1.8


## Caixão com tampa de vidro translúcido (alfa 0.35) e um corpo claro
## visível dentro. Retorna a altura em metros (0.7).
static func _caixao(root: Node3D) -> float:
	_box(root, Vector3(1.8, 0.3, 0.7), Vector3(0, 0.15, 0), MADEIRA_ESCURA)
	_box(root, Vector3(1.4, 0.15, 0.35), Vector3(0, 0.38, 0), OSSO)
	_box(root, Vector3(1.7, 0.3, 0.62), Vector3(0, 0.5, 0), Color(0.75, 0.92, 0.95), Vector3.ZERO, 0.35)
	return 0.7


## Lâmpada grande: base escura de cone truncado e globo verde luminoso
## (emissão 1.6). Retorna a altura em metros (1.3).
static func _lampada(root: Node3D) -> float:
	_cyl(root, 0.2, 0.25, 0.4, Vector3(0, 0.2, 0), Color(0.2, 0.2, 0.22))
	_sphere(root, 0.38, Vector3(0, 0.8, 0), Color(0.75, 1.0, 0.55), 1.0, 1.6)
	return 1.3
