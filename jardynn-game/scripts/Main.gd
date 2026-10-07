extends Node3D

## Carrega uma camada gerada pelo pipeline Python (`ynn-generator --json`) e
## instancia na cena o relevo (grade de pontos com altura, ver `terreno` no
## JSON) e o layout 2D (`layout` — lotes de área/torre/estufa/canteiro
## espalhados por um campo do tamanho de um campo de futebol, ver
## `ynn.layout`), além de imprimir no console o texto descritivo e as
## fichas de NPCs/criaturas de cada área. Estufas variam de tamanho/forma
## (planta baixa sorteada por "dado") e gazebos trazem bibelô, tesouro e a
## regra de abrigo noturno. A torre é uma mini-masmorra
## vertical (ver `ynn.generator.generate_torre_conteudo`): o console
## imprime o conteúdo de cada andar, e a malha vem cercada de hera.
##
## Para gerar novos dados (a partir da raiz do repositório):
##   cd ynn-generator
##   python -m ynn.cli --layer 1 --areas 5 --seed 42 --json \
##       --output ../jardynn-game/assets/data/camada1.json \
##       --plant-output-dir ../jardynn-game/assets/plants
## Use --terrain-resolution/--terrain-cell-size (relevo) e
## --field-width/--field-depth/--plot-size (layout) pra ajustar a escala.

@export var layer_json_path: String = "res://assets/data/camada1.json"
@export var plants_dir: String = "res://assets/plants/"
@export var area_spacing: float = 4.0  ## só usado no fallback sem `layout` (camadas antigas)
@export var scatter_radius: float = 1.5
@export var canteiro_radius: float = 3.0
@export var ivy_radius: float = 4.6
@export var ivy_inner_radius: float = 3.6
@export var min_instances_per_variant: int = 2
@export var max_instances_per_variant: int = 5

# O .obj não traz cor (nem material), então cada tipo de objeto ganha uma
# cor fixa — senão tudo aparece branco/cinza e some contra o fundo.
const TorreProps = preload("res://scripts/TorreProps.gd")

const COLOR_TERRENO := Color(0.22, 0.3, 0.16)
const COLOR_PLANTA := Color(0.28, 0.5, 0.22)
const COLOR_FLOR := Color(0.85, 0.4, 0.55)
const COLOR_HERA := Color(0.16, 0.38, 0.18)
const COLOR_GALHO := Color(0.38, 0.26, 0.16)
const COLOR_TORRE := Color(0.62, 0.36, 0.28)
const COLOR_ESTUFA := Color(0.7, 0.88, 0.92)
const COLOR_GAZEBO := Color(0.93, 0.88, 0.74)
const COLOR_TRILHA := Color(0.62, 0.52, 0.36)
const COLOR_ATALHO := Color(0.55, 0.5, 0.78)
const COLOR_DESCIDA := Color(0.78, 0.45, 0.35)

func _ready() -> void:
	var layer_data = _load_json(layer_json_path)
	if layer_data == null:
		push_error("Não foi possível carregar %s" % layer_json_path)
		return

	if layer_data.has("profundidade_maxima"):
		print("== Nível (profundidade máxima %s) ==" % _n(layer_data.get("profundidade_maxima")))
	else:
		print("== Camada %s ==" % _n(layer_data.get("layer", "?")))

	var terreno = layer_data.get("terreno")
	if terreno != null:
		print("Relevo (%s): %s" % [terreno.get("tipo_relevo"), terreno.get("descricao")])
		add_child(_build_terrain(terreno))

	var areas = layer_data.get("areas", [])
	var camada_layout = layer_data.get("layout")

	if camada_layout != null:
		var areas_by_index = {}
		for area in areas:
			areas_by_index[area.get("index")] = area
		var posicoes = {}
		for plot in camada_layout.get("plots", []):
			if plot.has("no_id"):
				posicoes[int(plot.get("no_id"))] = Vector2(plot.get("x", 0.0), plot.get("z", 0.0))
			_spawn_plot(plot, areas_by_index, terreno)
		for aresta in camada_layout.get("arestas", []):
			var de = int(aresta.get("de"))
			var para = int(aresta.get("para"))
			if posicoes.has(de) and posicoes.has(para):
				_spawn_path(posicoes[de], posicoes[para], aresta.get("tipo", "trilha"), terreno)
	else:
		# Compatibilidade com JSON gerado antes do layout 2D: enfileira as
		# áreas numa linha reta, como o script fazia originalmente.
		for i in areas.size():
			_spawn_area(areas[i], i * area_spacing, 0.0, terreno)


func _load_json(path: String):
	if not FileAccess.file_exists(path):
		return null
	var text = FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(text)
	return parsed


func _spawn_plot(plot: Dictionary, areas_by_index: Dictionary, terreno) -> void:
	var tipo = plot.get("tipo")
	var x: float = plot.get("x", 0.0)
	var z: float = plot.get("z", 0.0)

	if plot.has("local"):
		print("[profundidade %s] %s" % [_n(plot.get("profundidade")), plot.get("local")])
		var detalhe = plot.get("detalhe", {})
		print("  Detalhe (%s): %s" % [detalhe.get("tipo_relevo", "?"), detalhe.get("texto", "")])
		if detalhe.get("tesouro") != null:
			print("  Achado extra: %s" % detalhe.get("tesouro"))
		if "saida" in detalhe.get("efeitos", []):
			print("  Há uma porta de volta ao mundo real aqui.")

	match tipo:
		"area":
			var area = areas_by_index.get(plot.get("area_index"))
			if area != null:
				_spawn_area(area, x, z, terreno)
		"torre":
			_spawn_torre(plot, x, z, terreno)
		"estufa":
			var planta = plot.get("planta", {})
			print("--- Estufa em (%.1f, %.1f): d%s, %s portas, %s andar(es) ---" % [x, z, _n(planta.get("dado", "?")), _n(planta.get("portas", "?")), _n(planta.get("andares", "?"))])
			var estufa = plot.get("conteudo", {})
			print(estufa.get("texto", ""))
			if estufa.get("valor_ouro") != null:
				print("  Vale %s de ouro" % _n(estufa.get("valor_ouro")))
			var estufa_criatura = estufa.get("criatura")
			if estufa_criatura != null:
				print("  Criatura: %s (CA %s, DV %s, PV %s)" % [estufa_criatura.get("nome"), _n(estufa_criatura.get("ca")), estufa_criatura.get("dv"), _n(estufa_criatura.get("pontos_de_vida"))])
			_spawn_structure(plot.get("obj", ""), x, z, terreno, COLOR_ESTUFA)
		"gazebo":
			var gazebo = plot.get("conteudo", {})
			print("--- Gazebo em (%.1f, %.1f) ---" % [x, z])
			print(gazebo.get("texto", ""))
			print("  Bibelô: %s" % gazebo.get("bibelo", ""))
			print("  Tesouro: %s" % gazebo.get("tesouro", ""))
			print("  %s" % gazebo.get("refugio", ""))
			_spawn_structure(plot.get("obj", ""), x, z, terreno, COLOR_GAZEBO, true, true)
		"canteiro":
			print("--- Canteiro de %s em (%.1f, %.1f) ---" % [plot.get("especie", "?"), x, z])
			var cor_canteiro = COLOR_FLOR if plot.get("especie") == "flor" else COLOR_PLANTA
			for plant_path in plot.get("plantas_obj", []):
				_spawn_plant_cluster(plant_path, x, z, terreno, canteiro_radius, cor_canteiro)
		_:
			push_warning("Tipo de lote desconhecido no layout: %s" % tipo)


## Instancia a torre e imprime o conteúdo de cada andar (ver
## `ynn.generator.generate_torre_conteudo`: uma mini-masmorra vertical, não
## só decoração — cada andar tem seu próprio conteúdo, o topo é sempre o
## mais raro/significativo). A hera (`hera_obj`, malhas de videira)
## é espalhada rente à base, cobrindo o pé da torre.
func _spawn_torre(plot: Dictionary, x: float, z: float, terreno) -> void:
	var conteudo = plot.get("conteudo", {})
	print("--- Torre em (%.1f, %.1f), %s andares ---" % [x, z, _n(conteudo.get("n_andares", "?"))])
	for andar in conteudo.get("andares", []):
		var marca = " (topo)" if andar.get("numero") == conteudo.get("n_andares") else ""
		print("Andar %s%s: %s" % [_n(andar.get("numero")), marca, andar.get("texto", "")])
		if andar.get("tesouro") != null:
			print("  Tesouro: %s" % andar.get("tesouro"))
		if andar.get("denizen") != null:
			print("  Encontro: %s" % andar.get("denizen"))
			var npc = andar.get("npc")
			if npc != null:
				print("  NPC: %s (PV %s, CA %s)" % [npc.get("classe"), _n(npc.get("pontos_de_vida")), _n(npc.get("classe_de_armadura"))])
			var creature = andar.get("criatura")
			if creature != null:
				print("  Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), _n(creature.get("ca")), creature.get("dv"), _n(creature.get("pontos_de_vida"))])

	# Tudo da torre (malha, trepadeiras, plantas do topo, objetos dos andares,
	# rótulos e luzes) vai debaixo de um nó na base dela: se ela for uma das
	# torres inclinadas, basta girar esse nó e nada se desalinha.
	var geo = plot.get("geometria", {})
	var base_y: float = _height_at(terreno, x, z) if terreno != null else 0.0
	var torre = Node3D.new()
	torre.position = Vector3(x, base_y, z)
	var inclinacao = plot.get("inclinacao")
	if inclinacao != null:
		var azimute: float = inclinacao.get("azimute", 0.0)
		var graus: float = inclinacao.get("graus", 0.0)
		var eixo = Vector3.UP.cross(Vector3(cos(azimute), 0.0, sin(azimute))).normalized()
		torre.basis = Basis(eixo, deg_to_rad(graus))
		print("  A torre está inclinada %.1f graus." % graus)
	add_child(torre)

	_spawn_structure(plot.get("obj", ""), 0.0, 0.0, null, COLOR_TORRE, false, true, torre)

	var trepadeiras = plot.get("trepadeiras_obj")
	if trepadeiras != null and trepadeiras != "":
		print("  Trepadeiras sobem pelas paredes.")
		_spawn_structure(trepadeiras, 0.0, 0.0, null, COLOR_HERA, false, true, torre)

	for ivy_path in plot.get("hera_obj", []):
		_spawn_plant_cluster(ivy_path, 0.0, 0.0, null, ivy_radius, COLOR_HERA, ivy_inner_radius, 0.0, torre)

	var topo = conteudo.get("topo_brotado")
	if topo != null:
		print("  No topo, sem telhado: %s" % topo.get("texto", ""))
		var especie = str(topo.get("especie"))
		var cor_topo = COLOR_FLOR if especie == "flor" else COLOR_PLANTA
		var raio_topo: float = geo.get("raio_topo", 2.5)
		var altura_total: float = geo.get("altura_total", 0.0)
		for topo_path in plot.get("topo_obj", []):
			var instancias = 1 if especie == "arvore" else 2
			var escala_topo = 2.4 if especie == "arvore" else (1.5 if especie == "arbusto" else 1.3)
			_spawn_plant_cluster(topo_path, 0.0, 0.0, null, raio_topo * 0.7, cor_topo, 0.0, altura_total, torre, instancias, escala_topo)

	_spawn_props_torre(plot, torre)


## Posiciona, dentro da torre, o conteúdo sorteado de cada andar: um objeto
## no piso em anel (`prop`, montado por `TorreProps`), um rótulo flutuante e
## uma luz por andar. Tudo sai dos dados *dessa* torre (`geometria` e
## `conteudo`): cada uma tem seu número de andares, o raio de cada piso e a
## posição da porta. Os ângulos do JSON estão no plano de construção (z pra
## cima); no Godot (Y pra cima) o z vira -z.
func _spawn_props_torre(plot: Dictionary, torre: Node3D) -> void:
	var geo = plot.get("geometria", {})
	var raios = geo.get("raios_andar", [])
	if raios.is_empty():
		return
	var altura_andar: float = geo.get("altura_andar", 3.4)
	var raio_vao: float = geo.get("raio_vao", 1.3)
	var porta: float = geo.get("porta_angulo", 0.0)

	for andar in plot.get("conteudo", {}).get("andares", []):
		var indice = int(andar.get("numero")) - 1
		if indice < 0 or indice >= raios.size():
			continue

		var raio_andar: float = raios[indice]
		var raio_meio = (raio_vao + raio_andar) / 2.0
		var angulo = porta + PI + indice * 2.4  # longe da porta, girando a cada andar
		var piso_y = indice * altura_andar + 0.05

		var luz = OmniLight3D.new()
		luz.position = Vector3(0.0, piso_y + altura_andar * 0.65, 0.0)
		luz.omni_range = 6.0
		luz.light_energy = 0.7
		luz.light_color = Color(1.0, 0.85, 0.6)
		torre.add_child(luz)

		var raiz = Node3D.new()
		raiz.position = Vector3(cos(angulo) * raio_meio, piso_y, -sin(angulo) * raio_meio)
		raiz.rotation.y = angulo - PI / 2.0
		var escala = clamp((raio_andar - raio_vao) / 1.4, 0.55, 1.0)
		raiz.scale = Vector3.ONE * escala
		torre.add_child(raiz)

		var prop = andar.get("prop")
		var altura_prop = 0.0
		if prop != null:
			altura_prop = TorreProps.build(str(prop), raiz) * escala

		var nome = str(andar.get("rotulo", ""))
		if andar.get("criatura") != null:
			nome = str(andar.get("criatura").get("nome"))
		elif andar.get("npc") != null:
			nome = str(andar.get("npc").get("classe"))
		var rotulo = Label3D.new()
		rotulo.text = "Andar %s · %s" % [_n(andar.get("numero")), nome]
		rotulo.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		rotulo.font_size = 40
		rotulo.pixel_size = 0.005
		rotulo.outline_size = 10
		rotulo.position = raiz.position + Vector3(0, altura_prop + 0.4, 0)
		torre.add_child(rotulo)


func _spawn_area(area: Dictionary, base_x: float, base_z: float, terreno) -> void:
	print("--- Área %s (%s) ---" % [_n(area.get("index")), area.get("band")])
	print(area.get("text", ""))

	var npc = area.get("npc")
	if npc != null:
		print("NPC: %s (PV %s, CA %s)" % [npc.get("classe"), _n(npc.get("pontos_de_vida")), _n(npc.get("classe_de_armadura"))])

	var creature = area.get("criatura")
	if creature != null:
		print("Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), _n(creature.get("ca")), creature.get("dv"), _n(creature.get("pontos_de_vida"))])

	for plant_path in area.get("plantas_obj", []):
		_spawn_plant_cluster(plant_path, base_x, base_z, terreno, scatter_radius, COLOR_PLANTA)

	for branch_path in area.get("galhos_caidos_obj", []):
		_spawn_fallen_branch(branch_path, base_x, base_z, terreno)


## Espalha várias cópias de uma malha de planta (uma das variantes de
## `plantas_obj`) ao redor de (base_x, base_z), num raio `radius`, cada
## uma com rotação e escala levemente diferentes — um jardim de verdade
## não tem uma única planta isolada por canteiro.
func _spawn_plant_cluster(source_path: String, base_x: float, base_z: float, terreno, radius: float, color: Color, inner_radius: float = 0.0, y_extra: float = 0.0, parent: Node3D = null, instancias: int = -1, escala: float = 1.0) -> void:
	# `source_path` vem do JSON como um caminho de arquivo do lado Python
	# (pode usar "\" no Windows); só o nome do arquivo importa aqui, pois a
	# malha já foi gerada dentro de `plants_dir` por este mesmo pipeline.
	var filename = source_path.replace("\\", "/").get_file()
	var res_path = plants_dir.path_join(filename)

	var mesh = load(res_path)
	if mesh == null:
		push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % res_path)
		return

	var instance_count = instancias if instancias > 0 else randi_range(min_instances_per_variant, max_instances_per_variant)

	var multimesh = MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = mesh
	multimesh.instance_count = instance_count

	for i in instance_count:
		var angle = randf_range(0.0, TAU)
		var dist = sqrt(randf_range(inner_radius * inner_radius, radius * radius))
		var x = base_x + cos(angle) * dist
		var z = base_z + sin(angle) * dist
		var y = (_height_at(terreno, x, z) if terreno != null else 0.0) + y_extra

		var basis = Basis(Vector3.UP, randf_range(0.0, TAU)).scaled(Vector3.ONE * randf_range(0.8, 1.2) * escala)
		multimesh.set_instance_transform(i, Transform3D(basis, Vector3(x, y, z)))

	var multimesh_instance = MultiMeshInstance3D.new()
	multimesh_instance.multimesh = multimesh
	multimesh_instance.material_override = _material(color)
	(parent if parent != null else self).add_child(multimesh_instance)


## Instancia um galho/tronco caído (`galhos_caidos_obj`, ~1 em 6 áreas) —
## a malha já vem deitada da própria geração, então só posiciona e gira em
## torno de Y pra variar a direção em que aponta.
func _spawn_fallen_branch(source_path: String, base_x: float, base_z: float, terreno) -> void:
	var x = base_x + randf_range(-scatter_radius, scatter_radius)
	var z = base_z + randf_range(-scatter_radius, scatter_radius)
	_spawn_structure(source_path, x, z, terreno, COLOR_GALHO, false)


## Desenha uma trilha do mapa de pontos entre dois locais (as arestas de
## `layout.arestas`): uma fita rente ao terreno. Trilha = ligação normal
## entre camadas; atalho = liga a um local já explorado, mais raso; descida
## = leva a um local bem mais fundo.
func _spawn_path(a: Vector2, b: Vector2, tipo: String, terreno) -> void:
	var cor = COLOR_TRILHA
	var largura = 1.4
	if tipo == "atalho":
		cor = COLOR_ATALHO
		largura = 0.9
	elif tipo == "descida":
		cor = COLOR_DESCIDA
		largura = 0.9

	var comprimento = a.distance_to(b)
	if comprimento < 0.01:
		return
	var passos = max(2, int(comprimento / 1.5))
	var direcao = (b - a).normalized()
	var lado = Vector2(-direcao.y, direcao.x) * (largura / 2.0)

	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(passos):
		var p0 = a.lerp(b, float(i) / passos)
		var p1 = a.lerp(b, float(i + 1) / passos)
		var l0 = _ponto_trilha(p0 + lado, terreno)
		var r0 = _ponto_trilha(p0 - lado, terreno)
		var l1 = _ponto_trilha(p1 + lado, terreno)
		var r1 = _ponto_trilha(p1 - lado, terreno)
		st.add_vertex(l0)
		st.add_vertex(r0)
		st.add_vertex(l1)
		st.add_vertex(r0)
		st.add_vertex(r1)
		st.add_vertex(l1)
	st.generate_normals()

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = st.commit()
	mesh_instance.material_override = _material(cor, true)
	add_child(mesh_instance)


func _ponto_trilha(p: Vector2, terreno) -> Vector3:
	var y = _height_at(terreno, p.x, p.y) if terreno != null else 0.0
	return Vector3(p.x, y + 0.1, p.y)


## Cria um material liso da cor dada (ver as constantes COLOR_*).
func _material(color: Color, double_sided: bool = false) -> StandardMaterial3D:
	var material = StandardMaterial3D.new()
	material.albedo_color = color
	if double_sided:
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
	return material


## Converte um número do JSON (sempre float no Godot) pra inteiro legível
## nos prints ("Andar 3", não "Andar 3.0"); outros valores passam como estão.
func _n(value) -> String:
	return str(int(value)) if value is float else str(value)


## Instancia uma malha única já pronta (torre, estufa, gazebo, ou o galho
## caído acima) em (x, z), apoiada na altura do terreno, com a cor dada.
## `random_rotation` gira em Y pra variar a orientação; desligue pra
## estruturas que devam manter uma orientação fixa (torre e galho).
## `double_sided` desliga o descarte de faces de trás: necessário pras
## paredes sem espessura da torre e do gazebo, que se vê por dentro.
func _spawn_structure(source_path: String, x: float, z: float, terreno, color: Color, random_rotation: bool = true, double_sided: bool = false, parent: Node3D = null) -> void:
	if source_path == null or source_path == "":
		return

	var filename = source_path.replace("\\", "/").get_file()
	var res_path = plants_dir.path_join(filename)

	var mesh = load(res_path)
	if mesh == null:
		push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % res_path)
		return

	var y = _height_at(terreno, x, z) if terreno != null else 0.0

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = mesh
	mesh_instance.position = Vector3(x, y, z)
	mesh_instance.material_override = _material(color, double_sided)
	if random_rotation:
		mesh_instance.rotation.y = randf_range(0.0, TAU)
	(parent if parent != null else self).add_child(mesh_instance)


## Monta a malha triangulada do relevo a partir da grade de alturas
## (`terreno.alturas`, `resolucao` x `resolucao`, espaçadas por
## `tamanho_celula`) exportada pelo `ynn.terrain`. A grade é centralizada
## na origem, cobrindo todo o campo do layout.
func _build_terrain(terreno: Dictionary) -> MeshInstance3D:
	var resolution: int = terreno.get("resolucao")
	var cell_size: float = terreno.get("tamanho_celula")
	var alturas: Array = terreno.get("alturas")
	var half = (resolution - 1) / 2.0

	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	for z in range(resolution - 1):
		var z0 = (z - half) * cell_size
		var z1 = (z + 1 - half) * cell_size
		var row = alturas[z]
		var next_row = alturas[z + 1]
		for x in range(resolution - 1):
			var x0 = (x - half) * cell_size
			var x1 = (x + 1 - half) * cell_size

			var p00 = Vector3(x0, row[x], z0)
			var p10 = Vector3(x1, row[x + 1], z0)
			var p01 = Vector3(x0, next_row[x], z1)
			var p11 = Vector3(x1, next_row[x + 1], z1)

			st.add_vertex(p00)
			st.add_vertex(p10)
			st.add_vertex(p01)

			st.add_vertex(p10)
			st.add_vertex(p11)
			st.add_vertex(p01)

	st.generate_normals()

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = st.commit()

	mesh_instance.material_override = _material(COLOR_TERRENO)

	return mesh_instance


## Amostra a altura do relevo em uma posição (x, z) do mundo, por
## interpolação bilinear entre os pontos da grade mais próximos.
func _height_at(terreno: Dictionary, world_x: float, world_z: float) -> float:
	var resolution: int = terreno.get("resolucao")
	var cell_size: float = terreno.get("tamanho_celula")
	var alturas: Array = terreno.get("alturas")
	var half = (resolution - 1) / 2.0

	var gx = clamp(world_x / cell_size + half, 0, resolution - 1)
	var gz = clamp(world_z / cell_size + half, 0, resolution - 1)

	var x0 = int(floor(gx))
	var z0 = int(floor(gz))
	var x1 = min(x0 + 1, resolution - 1)
	var z1 = min(z0 + 1, resolution - 1)
	var tx = gx - x0
	var tz = gz - z0

	var h00 = alturas[z0][x0]
	var h10 = alturas[z0][x1]
	var h01 = alturas[z1][x0]
	var h11 = alturas[z1][x1]

	return lerp(lerp(h00, h10, tx), lerp(h01, h11, tx), tz)
