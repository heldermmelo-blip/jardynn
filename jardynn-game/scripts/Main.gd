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
@export var ivy_radius: float = 2.0
@export var min_instances_per_variant: int = 2
@export var max_instances_per_variant: int = 5

func _ready() -> void:
	var layer_data = _load_json(layer_json_path)
	if layer_data == null:
		push_error("Não foi possível carregar %s" % layer_json_path)
		return

	print("== Camada %s ==" % layer_data.get("layer", "?"))

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
		for plot in camada_layout.get("plots", []):
			_spawn_plot(plot, areas_by_index, terreno)
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

	match tipo:
		"area":
			var area = areas_by_index.get(plot.get("area_index"))
			if area != null:
				_spawn_area(area, x, z, terreno)
		"torre":
			_spawn_torre(plot, x, z, terreno)
		"estufa":
			var planta = plot.get("planta", {})
			print("--- Estufa em (%.1f, %.1f): d%s, %s portas, %s andar(es) ---" % [x, z, planta.get("dado", "?"), planta.get("portas", "?"), planta.get("andares", "?")])
			_spawn_structure(plot.get("obj", ""), x, z, terreno)
		"gazebo":
			var gazebo = plot.get("conteudo", {})
			print("--- Gazebo em (%.1f, %.1f) ---" % [x, z])
			print(gazebo.get("texto", ""))
			print("  Bibelô: %s" % gazebo.get("bibelo", ""))
			print("  Tesouro: %s" % gazebo.get("tesouro", ""))
			print("  %s" % gazebo.get("refugio", ""))
			_spawn_structure(plot.get("obj", ""), x, z, terreno)
		"canteiro":
			print("--- Canteiro de %s em (%.1f, %.1f) ---" % [plot.get("especie", "?"), x, z])
			for plant_path in plot.get("plantas_obj", []):
				_spawn_plant_cluster(plant_path, x, z, terreno, canteiro_radius)
		_:
			push_warning("Tipo de lote desconhecido no layout: %s" % tipo)


## Instancia a torre e imprime o conteúdo de cada andar (ver
## `ynn.generator.generate_torre_conteudo`: uma mini-masmorra vertical, não
## só decoração — cada andar tem seu próprio conteúdo, o topo é sempre o
## mais raro/significativo). A hera (`hera_obj`, malhas de videira)
## é espalhada rente à base, cobrindo o pé da torre.
func _spawn_torre(plot: Dictionary, x: float, z: float, terreno) -> void:
	var conteudo = plot.get("conteudo", {})
	print("--- Torre em (%.1f, %.1f), %s andares ---" % [x, z, conteudo.get("n_andares", "?")])
	for andar in conteudo.get("andares", []):
		var marca = " (topo)" if andar.get("numero") == conteudo.get("n_andares") else ""
		print("Andar %s%s: %s" % [andar.get("numero"), marca, andar.get("texto", "")])
		if andar.get("tesouro") != null:
			print("  Tesouro: %s" % andar.get("tesouro"))
		if andar.get("denizen") != null:
			print("  Encontro: %s" % andar.get("denizen"))
			var npc = andar.get("npc")
			if npc != null:
				print("  NPC: %s (PV %s, CA %s)" % [npc.get("classe"), npc.get("pontos_de_vida"), npc.get("classe_de_armadura")])
			var creature = andar.get("criatura")
			if creature != null:
				print("  Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), creature.get("ca"), creature.get("dv"), creature.get("pontos_de_vida")])

	_spawn_structure(plot.get("obj", ""), x, z, terreno, false)

	for ivy_path in plot.get("hera_obj", []):
		_spawn_plant_cluster(ivy_path, x, z, terreno, ivy_radius)


func _spawn_area(area: Dictionary, base_x: float, base_z: float, terreno) -> void:
	print("--- Área %s (%s) ---" % [area.get("index"), area.get("band")])
	print(area.get("text", ""))

	var npc = area.get("npc")
	if npc != null:
		print("NPC: %s (PV %s, CA %s)" % [npc.get("classe"), npc.get("pontos_de_vida"), npc.get("classe_de_armadura")])

	var creature = area.get("criatura")
	if creature != null:
		print("Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), creature.get("ca"), creature.get("dv"), creature.get("pontos_de_vida")])

	for plant_path in area.get("plantas_obj", []):
		_spawn_plant_cluster(plant_path, base_x, base_z, terreno, scatter_radius)

	for branch_path in area.get("galhos_caidos_obj", []):
		_spawn_fallen_branch(branch_path, base_x, base_z, terreno)


## Espalha várias cópias de uma malha de planta (uma das variantes de
## `plantas_obj`) ao redor de (base_x, base_z), num raio `radius`, cada
## uma com rotação e escala levemente diferentes — um jardim de verdade
## não tem uma única planta isolada por canteiro.
func _spawn_plant_cluster(source_path: String, base_x: float, base_z: float, terreno, radius: float) -> void:
	# `source_path` vem do JSON como um caminho de arquivo do lado Python
	# (pode usar "\" no Windows); só o nome do arquivo importa aqui, pois a
	# malha já foi gerada dentro de `plants_dir` por este mesmo pipeline.
	var filename = source_path.replace("\\", "/").get_file()
	var res_path = plants_dir.path_join(filename)

	var mesh = load(res_path)
	if mesh == null:
		push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % res_path)
		return

	var instance_count = randi_range(min_instances_per_variant, max_instances_per_variant)

	var multimesh = MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = mesh
	multimesh.instance_count = instance_count

	for i in instance_count:
		var x = base_x + randf_range(-radius, radius)
		var z = base_z + randf_range(-radius, radius)
		var y = _height_at(terreno, x, z) if terreno != null else 0.0

		var basis = Basis(Vector3.UP, randf_range(0.0, TAU)).scaled(Vector3.ONE * randf_range(0.8, 1.2))
		multimesh.set_instance_transform(i, Transform3D(basis, Vector3(x, y, z)))

	var multimesh_instance = MultiMeshInstance3D.new()
	multimesh_instance.multimesh = multimesh
	add_child(multimesh_instance)


## Instancia um galho/tronco caído (`galhos_caidos_obj`, ~1 em 6 áreas) —
## a malha já vem deitada da própria geração, então só posiciona e gira em
## torno de Y pra variar a direção em que aponta.
func _spawn_fallen_branch(source_path: String, base_x: float, base_z: float, terreno) -> void:
	var x = base_x + randf_range(-scatter_radius, scatter_radius)
	var z = base_z + randf_range(-scatter_radius, scatter_radius)
	_spawn_structure(source_path, x, z, terreno, false)


## Instancia uma malha única já pronta (torre, estufa, ou o galho caído
## acima) em (x, z), apoiada na altura do terreno. `random_rotation` gira
## em Y pra variar a orientação; desligue pra estruturas que devam manter
## uma orientação fixa (nenhuma por enquanto usa isso, mas fica disponível).
func _spawn_structure(source_path: String, x: float, z: float, terreno, random_rotation: bool = true) -> void:
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
	if random_rotation:
		mesh_instance.rotation.y = randf_range(0.0, TAU)
	add_child(mesh_instance)


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
			st.add_vertex(p01)
			st.add_vertex(p10)

			st.add_vertex(p10)
			st.add_vertex(p01)
			st.add_vertex(p11)

	st.generate_normals()

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = st.commit()

	var material = StandardMaterial3D.new()
	material.albedo_color = Color(0.22, 0.3, 0.16)
	mesh_instance.material_override = material

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
