extends Node3D

## Carrega uma camada gerada pelo pipeline Python (`ynn-generator --json`) e
## instancia na cena o relevo (grade de pontos com altura, ver `terreno` no
## JSON) e as plantas (.obj) de cada área sobre ele, além de imprimir no
## console o texto descritivo e as fichas de NPCs/criaturas encontradas.
##
## Para gerar novos dados (a partir da raiz do repositório):
##   cd ynn-generator
##   python -m ynn.cli --layer 1 --areas 5 --seed 42 --json \
##       --output ../jardynn-game/assets/data/camada1.json \
##       --plant-output-dir ../jardynn-game/assets/plants
## Use --terrain-resolution/--terrain-cell-size pra ajustar a grade de relevo.

@export var layer_json_path: String = "res://assets/data/camada1.json"
@export var plants_dir: String = "res://assets/plants/"
@export var area_spacing: float = 4.0

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
	for i in areas.size():
		_spawn_area(areas[i], i, terreno)


func _load_json(path: String):
	if not FileAccess.file_exists(path):
		return null
	var text = FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(text)
	return parsed


func _spawn_area(area: Dictionary, index: int, terreno) -> void:
	print("--- Área %s (%s) ---" % [area.get("index"), area.get("band")])
	print(area.get("text", ""))

	var npc = area.get("npc")
	if npc != null:
		print("NPC: %s (PV %s, CA %s)" % [npc.get("classe"), npc.get("pontos_de_vida"), npc.get("classe_de_armadura")])

	var creature = area.get("criatura")
	if creature != null:
		print("Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), creature.get("ca"), creature.get("dv"), creature.get("pontos_de_vida")])

	var plant_path = area.get("planta_obj")
	if plant_path != null and plant_path != "":
		_spawn_plant(plant_path, index, terreno)


func _spawn_plant(source_path: String, index: int, terreno) -> void:
	# `source_path` vem do JSON como um caminho de arquivo do lado Python
	# (pode usar "\" no Windows); só o nome do arquivo importa aqui, pois a
	# malha já foi gerada dentro de `plants_dir` por este mesmo pipeline.
	var filename = source_path.replace("\\", "/").get_file()
	var res_path = plants_dir.path_join(filename)

	var mesh = load(res_path)
	if mesh == null:
		push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % res_path)
		return

	var x = index * area_spacing
	var y = _height_at(terreno, x, 0.0) if terreno != null else 0.0

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = mesh
	mesh_instance.position = Vector3(x, y, 0)
	add_child(mesh_instance)


## Monta a malha triangulada do relevo a partir da grade de alturas
## (`terreno.alturas`, `resolucao` x `resolucao`, espaçadas por
## `tamanho_celula`) exportada pelo `ynn.terrain`. A grade é centralizada na
## origem, então a linha das áreas (sempre em z=0) cruza a malha pelo meio.
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
