extends Node3D

## Carrega uma camada gerada pelo pipeline Python (`ynn-generator --json`) e
## instancia na cena as plantas (.obj) de cada área, além de imprimir no
## console o texto descritivo e as fichas de NPCs/criaturas encontradas.
##
## Para gerar novos dados (a partir da raiz do repositório):
##   cd ynn-generator
##   python -m ynn.cli --layer 1 --areas 5 --seed 42 --json \
##       --output ../jardynn-game/assets/data/camada1.json \
##       --plant-output-dir ../jardynn-game/assets/plants

@export var layer_json_path: String = "res://assets/data/camada1.json"
@export var plants_dir: String = "res://assets/plants/"
@export var area_spacing: float = 4.0

func _ready() -> void:
	var layer_data = _load_json(layer_json_path)
	if layer_data == null:
		push_error("Não foi possível carregar %s" % layer_json_path)
		return

	print("== Camada %s ==" % layer_data.get("layer", "?"))
	var areas = layer_data.get("areas", [])
	for i in areas.size():
		_spawn_area(areas[i], i)


func _load_json(path: String):
	if not FileAccess.file_exists(path):
		return null
	var text = FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(text)
	return parsed


func _spawn_area(area: Dictionary, index: int) -> void:
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
		_spawn_plant(plant_path, index)


func _spawn_plant(source_path: String, index: int) -> void:
	# `source_path` vem do JSON como um caminho de arquivo do lado Python
	# (pode usar "\" no Windows); só o nome do arquivo importa aqui, pois a
	# malha já foi gerada dentro de `plants_dir` por este mesmo pipeline.
	var filename = source_path.replace("\\", "/").get_file()
	var res_path = plants_dir.path_join(filename)

	var mesh = load(res_path)
	if mesh == null:
		push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % res_path)
		return

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = mesh
	mesh_instance.position = Vector3(index * area_spacing, 0, 0)
	add_child(mesh_instance)
