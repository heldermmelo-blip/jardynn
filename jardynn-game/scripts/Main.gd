extends Node3D

## Carrega uma camada gerada pelo pipeline Python (`ynn-generator --json`) e
## instancia na cena o relevo (grade de pontos com altura, ver `terreno` no
## JSON) e o layout 2D (`layout` — lotes de área/torre/estufa/canteiro
## espalhados por um campo do tamanho de um campo de futebol, ver
## `ynn.layout`), além de imprimir no console o texto descritivo e as
## fichas de NPCs/criaturas de cada área. Estufas têm porte, alas, estado
## (às vezes em ruínas) e uma malha por material; uma minúscula pode ficar
## num espelho d'água e a colossal cobre o nível inteiro, com portal de
## entrada e de saída. Gazebos trazem bibelô, tesouro e a
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
const COLOR_VIDRO := Color(0.72, 0.9, 0.95, 0.28)
const COLOR_SOCO := Color(0.55, 0.53, 0.5)
const COLOR_MORTO := Color(0.3, 0.22, 0.14)
const COLOR_PISO_PRETO := Color(0.06, 0.06, 0.07)
const COLOR_PISO_BRANCO := Color(0.88, 0.87, 0.82)
const COLOR_PLANTA_MORTA := Color(0.36, 0.27, 0.16)
const ARVORES_GRANDES := ["carvalho", "salgueiro", "pinheiro", "araucaria", "dracena_dragao"]
const COR_FLORA_ESTUFA := {
	"cacto_coluna": Color(0.3, 0.55, 0.32),
	"cacto_barril": Color(0.35, 0.6, 0.3),
	"agave": Color(0.45, 0.62, 0.55),
	"palmeira": Color(0.22, 0.5, 0.2),
	"folha_larga": Color(0.18, 0.6, 0.25),
	"samambaia": Color(0.25, 0.55, 0.2),
	"videira": Color(0.2, 0.42, 0.2),
	"flor": Color(0.85, 0.4, 0.55),
	"arbusto": Color(0.28, 0.5, 0.22),
	"cipreste": Color(0.1, 0.3, 0.16),
	"topiaria": Color(0.2, 0.46, 0.2),
	"cogumelo": Color(0.75, 0.35, 0.3),
	"dracena_dragao": Color(0.32, 0.5, 0.3),
}
const COR_PITORESCO := {
	"pedra": Color(0.66, 0.64, 0.6),
	"marmore": Color(0.8, 0.79, 0.76),
	"obsidiana": Color(0.06, 0.06, 0.08),
	"pedra_preta": Color(0.1, 0.1, 0.12),
	"gramado": Color(0.24, 0.46, 0.2),
	"sebe": Color(0.1, 0.32, 0.13),
	"piso": Color(0.55, 0.5, 0.4),
	"hera": Color(0.16, 0.4, 0.18),
	"folha": Color(0.2, 0.52, 0.26),
	"porta": Color(0.04, 0.03, 0.03),
	"agua": Color(0.28, 0.48, 0.56, 0.78),
	"gelo": Color(0.78, 0.9, 0.96, 0.88),
	"flor": Color(0.97, 0.8, 0.88),
	"ferro": Color(0.1, 0.13, 0.12),
	"jarro": Color(0.68, 0.64, 0.56),
	"musgo": Color(0.2, 0.42, 0.16),
	"madeira": Color(0.5, 0.36, 0.22),
	"reboco": Color(0.78, 0.7, 0.46),
	"telha": Color(0.58, 0.3, 0.22),
}
const COR_TORRE := {
	"tijolo": Color(0.62, 0.36, 0.28),
	"madeira": Color(0.42, 0.28, 0.17),
	"telhado": Color(0.36, 0.2, 0.18),
	"terra": Color(0.25, 0.18, 0.1),
	"tapete": Color(0.3, 0.36, 0.2),
	"agua": Color(0.3, 0.45, 0.52, 0.7),
	"papel": Color(0.8, 0.74, 0.58),
	"ferro": Color(0.1, 0.13, 0.12),
	"pedra": Color(0.66, 0.64, 0.6),
	"jarro": Color(0.68, 0.64, 0.56),
	"musgo": Color(0.2, 0.42, 0.16),
}
const COR_GAZEBO := {
	"madeira": Color(0.93, 0.88, 0.74),
	"telhado": Color(0.72, 0.36, 0.3),
	"ferro": Color(0.1, 0.13, 0.12),
	"pedra": Color(0.66, 0.64, 0.6),
	"jarro": Color(0.68, 0.64, 0.56),
	"musgo": Color(0.2, 0.42, 0.16),
}
const COR_MOLDURA := {
	"verde": Color(0.16, 0.36, 0.24),
	"verdete": Color(0.3, 0.55, 0.5),
	"branca": Color(0.92, 0.92, 0.9),
	"preta": Color(0.08, 0.08, 0.09),
	"ferrugem": Color(0.5, 0.26, 0.14),
}
const COLOR_GAZEBO := Color(0.93, 0.88, 0.74)
const COLOR_TRILHA := Color(0.62, 0.52, 0.36)
const COLOR_ATALHO := Color(0.55, 0.5, 0.78)
const COLOR_DESCIDA := Color(0.78, 0.45, 0.35)

var _terreno_atual = null


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
	_terreno_atual = terreno
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
		if layer_data.has("estufa_colossal"):
			_spawn_estufa_colossal(layer_data.get("estufa_colossal"), posicoes)
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
		if detalhe.get("tesouros") != null:
			print("  Pilha de tesouro: %s de prata e %s" % [_n(detalhe.get("prata")), " / ".join(PackedStringArray(detalhe.get("tesouros")))])
		elif detalhe.get("tesouro") != null:
			print("  Achado extra: %s" % detalhe.get("tesouro"))
		if plot.get("estado") != null:
			print("  O lugar %s." % ("está inteiro" if plot.get("estado") == "intacta" else "jaz em ruínas"))
		if "saida" in detalhe.get("efeitos", []):
			print("  Há uma porta de volta ao mundo real aqui.")

	match tipo:
		"area":
			var area = areas_by_index.get(plot.get("area_index"))
			if area != null:
				_spawn_area(area, x, z, terreno)
		"torre":
			_spawn_torre(plot, x, z, terreno)
		"estufa", "orquidario":
			_spawn_estufa(plot, x, z, terreno)
		"fonte", "estatuas", "labirinto", "mausoleu", "lago", "lago_gelado", "xadrez", "escadaria", "casa_inclinada":
			_spawn_pitoresco(plot, x, z)
		"gazebo":
			var gazebo = plot.get("conteudo", {})
			print("--- Gazebo em (%.1f, %.1f) ---" % [x, z])
			print(gazebo.get("texto", ""))
			print("  Bibelô: %s" % gazebo.get("bibelo", ""))
			print("  Tesouro: %s" % gazebo.get("tesouro", ""))
			print("  %s" % gazebo.get("refugio", ""))
			if plot.get("estado") == "ruina":
				print("  O coreto está em ruínas: parapeito e telhado vencidos, musgo na base.")
			print("  Parapeito: %s." % str(plot.get("estilo", "?")).replace("_", " "))
			if plot.has("malhas"):
				var raiz_gazebo = Node3D.new()
				raiz_gazebo.position = Vector3(x, _height_at(terreno, x, z) if terreno != null else 0.0, z)
				raiz_gazebo.rotation.y = randf_range(0.0, TAU)
				add_child(raiz_gazebo)
				_spawn_malhas_torre(plot.get("malhas"), raiz_gazebo, COR_GAZEBO)
			else:
				_spawn_structure(plot.get("obj", ""), x, z, terreno, COLOR_GAZEBO, true, true)
		"canteiro":
			print("--- Canteiro de %s em (%.1f, %.1f) ---" % [plot.get("especie", "?"), x, z])
			var cor_canteiro = COLOR_FLOR if plot.get("especie") == "flor" else COLOR_PLANTA
			for plant_path in plot.get("plantas_obj", []):
				_spawn_plant_cluster(plant_path, x, z, terreno, canteiro_radius, cor_canteiro)
		_:
			push_warning("Tipo de lote desconhecido no layout: %s" % tipo)

	_spawn_ambiente(plot, x, z, terreno)
	_spawn_cupula_vidro(plot, x, z, terreno)


## Estufa comum: moldura de ferro pintada, vidro (às vezes quebrado), soco de
## pedra, piso xadrez e trepadeiras mortas, cada grupo de malha com seu
## material. `rotacao_y` vira a porta pro caminho que leva até ela; se ela
## está num espelho d'água, desenha a água e a calçada até a porta.
func _spawn_estufa(plot: Dictionary, x: float, z: float, terreno) -> void:
	var casas: Array = plot.get("estufas", [])
	var rotulo = "Orquidário" if plot.get("tipo") == "orquidario" else "Estufas"
	var estado = " em ruínas" if plot.get("estado") == "ruina" else ""
	print("--- %s%s em (%.1f, %.1f): %d casa(s) de vidro, dados jogados no papel ---" % [rotulo, estado, x, z, casas.size()])
	var y = _height_at(terreno, x, z) if terreno != null else 0.0
	for casa in casas:
		var planta = casa.get("planta", {})
		print("  d%s tirou %s: %s lados, %s andar(es)%s%s" % [_n(casa.get("dado")), _n(casa.get("resultado")), _n(planta.get("lados")), _n(planta.get("andares")), ", piso em xadrez" if planta.get("piso_xadrez") else "", ", lacrada" if planta.get("lacrada") else ""])
		var conteudo = casa.get("conteudo", {})
		print("    %s" % conteudo.get("texto", ""))
		if conteudo.get("valor_ouro") != null:
			print("    Vale %s de ouro" % _n(conteudo.get("valor_ouro")))
		if conteudo.get("valor_prata") != null:
			print("    As orquídeas valem %s de prata a um colecionador" % _n(conteudo.get("valor_prata")))
		var criatura = conteudo.get("criatura")
		if criatura != null:
			var qtd = " (x%s)" % _n(conteudo.get("quantidade")) if conteudo.get("quantidade") != null else ""
			print("    Criatura: %s%s (CA %s, DV %s, PV %s)" % [criatura.get("nome"), qtd, _n(criatura.get("ca")), criatura.get("dv"), _n(criatura.get("pontos_de_vida"))])
		var raiz = Node3D.new()
		raiz.position = Vector3(x + float(casa.get("x", 0.0)), y, z + float(casa.get("z", 0.0)))
		raiz.rotation.y = casa.get("rotacao_y", 0.0)
		add_child(raiz)
		_spawn_malhas_estufa(casa.get("malhas", {}), planta, raiz)
		_spawn_flora_interna(casa.get("flora_interna"), raiz)


## "Teto de Vidro": o lugar inteiro fica dentro de uma estufa gigante, uma
## cúpula de vidro sobre o lote.
func _spawn_cupula_vidro(plot: Dictionary, x: float, z: float, terreno) -> void:
	var cupula = plot.get("cupula_vidro")
	if cupula == null:
		return
	print("  O lugar inteiro está dentro de uma estufa gigante (cúpula de %.0f m de raio)." % float(cupula.get("raio", 0.0)))
	var raiz = Node3D.new()
	raiz.position = Vector3(x, _height_at(terreno, x, z) if terreno != null else 0.0, z)
	raiz.rotation.y = cupula.get("rotacao_y", 0.0)
	add_child(raiz)
	_spawn_malhas_estufa(cupula.get("malhas", {}), {"moldura": "verdete", "estado": cupula.get("estado")}, raiz)


## O Detalhe de cada lugar muda o clima dele: água parada, geada, cinzas, brasas,
## brilho de plantas luminosas, um poste aceso. (O estado, inteiro ou em ruínas,
## vem do mesmo Detalhe e já deu forma às estruturas.)
func _spawn_ambiente(plot: Dictionary, x: float, z: float, terreno) -> void:
	var efeitos = plot.get("detalhe", {}).get("efeitos", [])
	var raio: float = float(plot.get("raio_ocupado", 9.0)) + 5.0
	if plot.has("cupula_vidro"):
		raio = float(plot.get("cupula_vidro").get("raio", raio))
	var y = (_height_at(terreno, x, z) if terreno != null else 0.0)
	var cor = null
	var altura = 0.08
	if "alagado" in efeitos:
		cor = Color(0.28, 0.44, 0.5, 0.55)
		altura = 0.35
	elif "congelado" in efeitos:
		cor = Color(0.85, 0.93, 0.98, 0.7)
		altura = 0.1
	elif "queimado" in efeitos or "fumegante" in efeitos:
		cor = Color(0.08, 0.07, 0.07, 0.8)
	if cor != null:
		var st = SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		var n = 36
		var c0 = Vector3(x, y + altura, z)
		for i in range(n):
			var a0 = TAU * i / n
			var a1 = TAU * (i + 1) / n
			st.add_vertex(c0)
			st.add_vertex(c0 + Vector3(cos(a1), 0.0, sin(a1)) * raio)
			st.add_vertex(c0 + Vector3(cos(a0), 0.0, sin(a0)) * raio)
		st.generate_normals()
		var disco = MeshInstance3D.new()
		disco.mesh = st.commit()
		var material = StandardMaterial3D.new()
		material.albedo_color = cor
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
		disco.material_override = material
		disco.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(disco)
	if "fumegante" in efeitos:
		for k in range(4):
			var brasa = OmniLight3D.new()
			brasa.light_color = Color(1.0, 0.45, 0.15)
			brasa.omni_range = 5.0
			brasa.light_energy = 0.9
			var ang = TAU * k / 4.0 + 0.5
			brasa.position = Vector3(x + cos(ang) * raio * 0.5, y + 0.5, z + sin(ang) * raio * 0.5)
			add_child(brasa)
	if "luminoso" in efeitos:
		for k in range(5):
			var luz = OmniLight3D.new()
			luz.light_color = Color(0.5, 1.0, 0.8)
			luz.omni_range = 6.0
			luz.light_energy = 0.8
			var ang = TAU * k / 5.0
			luz.position = Vector3(x + cos(ang) * raio * 0.45, y + 1.2, z + sin(ang) * raio * 0.45)
			add_child(luz)
	if "poste" in efeitos:
		var poste = MeshInstance3D.new()
		var cil = CylinderMesh.new()
		cil.top_radius = 0.06
		cil.bottom_radius = 0.1
		cil.height = 3.6
		poste.mesh = cil
		poste.material_override = _material(Color(0.08, 0.1, 0.09))
		poste.position = Vector3(x + raio * 0.35, y + 1.8, z)
		add_child(poste)
		var lampada = OmniLight3D.new()
		lampada.light_color = Color(1.0, 0.85, 0.55)
		lampada.omni_range = 11.0
		lampada.position = Vector3(x + raio * 0.35, y + 3.8, z)
		add_child(lampada)


## Uma malha por material: o .obj da moldura (`malhas.moldura`) mais as
## variantes `_vidro`, `_soco`, `_morto`, `_piso_preto` e `_piso_branco`.
func _spawn_malhas_estufa(malhas: Dictionary, planta: Dictionary, pai: Node3D) -> void:
	var cor_moldura: Color = COR_MOLDURA.get(planta.get("moldura", "verde"), COLOR_ESTUFA)
	var cores = {
		"moldura": cor_moldura,
		"soco": COLOR_SOCO,
		"morto": COLOR_MORTO,
		"piso_preto": COLOR_PISO_PRETO,
		"piso_branco": COLOR_PISO_BRANCO,
	}
	for grupo in ["soco", "piso_preto", "piso_branco", "moldura", "morto", "vidro"]:
		if not malhas.has(grupo):
			continue
		var caminho: String = malhas.get(grupo)
		var filename = caminho.replace("\\", "/").get_file()
		var mesh = load(plants_dir.path_join(filename))
		if mesh == null:
			push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % filename)
			continue
		var mi = MeshInstance3D.new()
		mi.mesh = mesh
		if grupo == "vidro":
			mi.material_override = _material_vidro()
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			mi.material_override = _material(cores[grupo], true)
		pai.add_child(mi)


## Plantas de dentro da estufa (`flora_interna`): cada exemplar já vem com
## posição local, escala, giro e se está morto (as estufas em ruína têm
## plantas secas, em marrom). Vão sob o mesmo nó da estufa, então giram com
## ela.
func _spawn_flora_interna(flora, pai: Node3D) -> void:
	if flora == null or flora.is_empty():
		return
	var plantas: Array = flora.get("plantas", [])
	print("  Flora interna: %s, tema %s, %s plantas (%s)" % [flora.get("densidade", "?"), flora.get("tema", "?"), str(plantas.size()), ", ".join(PackedStringArray(flora.get("especies", [])))])
	if flora.get("mortas", 0.0) > 0.0:
		print("  %d%% delas estão mortas." % int(round(float(flora.get("mortas")) * 100.0)))
	var meshes := {}
	var materiais := {}
	for planta in plantas:
		var caminho: String = planta.get("obj", "")
		if caminho == "":
			continue
		if not meshes.has(caminho):
			meshes[caminho] = load(plants_dir.path_join(caminho.replace("\\", "/").get_file()))
		var mesh = meshes[caminho]
		if mesh == null:
			continue
		var morta: bool = planta.get("morta", false)
		var especie = str(planta.get("especie"))
		var chave = "morta" if morta else especie
		if not materiais.has(chave):
			materiais[chave] = _material(COLOR_PLANTA_MORTA, true) if morta else _material_planta(mesh, COR_FLORA_ESTUFA.get(especie, COLOR_PLANTA), true)
		var mi = MeshInstance3D.new()
		mi.mesh = mesh
		mi.material_override = materiais[chave]
		mi.position = Vector3(planta.get("x", 0.0), 0.05, planta.get("z", 0.0))
		mi.rotation.y = planta.get("rot", 0.0)
		mi.scale = Vector3.ONE * float(planta.get("escala", 1.0))
		pai.add_child(mi)


## Estrutura pitoresca do livro (fonte, estátuas, labirinto, mausoléu, lago,
## gramado de xadrez): uma malha por material, sobre o chão aplainado pelo
## gerador (y = 0). `rotacao_y` já vem calculada (ou vira a porta pro caminho).
func _spawn_pitoresco(plot: Dictionary, x: float, z: float) -> void:
	var tipo = str(plot.get("tipo"))
	print("--- %s em (%.1f, %.1f), raio %.1f m ---" % [tipo.capitalize(), x, z, float(plot.get("raio_ocupado", 0.0))])
	var extra = plot.get("pitoresco", {})
	if plot.get("estado") == "ruina":
		print("  Está em ruínas.")
	print("  Ferragens e parapeito: %s." % str(plot.get("estilo", "?")).replace("_", " "))
	if tipo == "fonte":
		print("  A fonte está %s." % ("seca" if extra.get("seca") else "cheia d'água"))
	elif tipo == "estatuas":
		print("  %s estátuas%s." % [_n(extra.get("estatuas", 0)), ", viradas de costas para o centro" if extra.get("de_costas") else ""])
	elif tipo == "labirinto":
		print("  Labirinto de %sx%s células, com um vão de entrada." % [_n(extra.get("n", 0)), _n(extra.get("n", 0))])
	elif tipo == "xadrez":
		print("  %s peças gigantes espalhadas pelo tabuleiro." % str(extra.get("pecas", []).size()))

	var raiz = Node3D.new()
	raiz.position = Vector3(x, 0.0, z)
	raiz.rotation.y = plot.get("rotacao_y", 0.0)
	add_child(raiz)
	var malhas: Dictionary = plot.get("malhas", {})
	for grupo in malhas:
		var filename = str(malhas[grupo]).replace("\\", "/").get_file()
		var mesh = load(plants_dir.path_join(filename))
		if mesh == null:
			push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % filename)
			continue
		var cor: Color = COR_PITORESCO.get(grupo, COLOR_TORRE)
		var mi = MeshInstance3D.new()
		mi.mesh = mesh
		if cor.a < 1.0:
			var material = StandardMaterial3D.new()
			material.albedo_color = cor
			material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			material.cull_mode = BaseMaterial3D.CULL_DISABLED
			material.roughness = 0.1
			mi.material_override = material
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			mi.material_override = _material(cor, true)
		raiz.add_child(mi)


## Torre do livro: tijolo, madeira (porta entreaberta, venezianas, escada, pisos),
## telhado, tapete mofado, poças d'água junto às janelas e papel de parede
## descascando — cada material da sua cor, todos de dupla face.
func _spawn_malhas_torre(malhas: Dictionary, torre: Node3D, cores: Dictionary = COR_TORRE) -> void:
	for grupo in malhas:
		var filename = str(malhas[grupo]).replace("\\", "/").get_file()
		var mesh = load(plants_dir.path_join(filename))
		if mesh == null:
			push_warning("Malha não encontrada (reimporte o projeto no editor após gerar os .obj): %s" % filename)
			continue
		var cor: Color = cores.get(grupo, COLOR_TORRE)
		var mi = MeshInstance3D.new()
		mi.mesh = mesh
		if cor.a < 1.0:
			var material = StandardMaterial3D.new()
			material.albedo_color = cor
			material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			material.cull_mode = BaseMaterial3D.CULL_DISABLED
			material.roughness = 0.1
			mi.material_override = material
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			mi.material_override = _material(cor, true)
		torre.add_child(mi)


func _material_vidro() -> StandardMaterial3D:
	var material = StandardMaterial3D.new()
	material.albedo_color = COLOR_VIDRO
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.roughness = 0.1
	return material


## A estufa colossal: o vidro dela cobre o nível inteiro. Entra-se por um
## portal de um lado (junto ao nó de entrada) e só se sai pelo portal do lado
## oposto (junto ao local mais fundo). `posicoes` mapeia nó -> (x, z).
func _spawn_estufa_colossal(colossal: Dictionary, posicoes: Dictionary) -> void:
	var planta = colossal.get("planta", {})
	var raio: float = colossal.get("raio", 55.0)
	print("=== ESTUFA COLOSSAL (raio %.0f m, %s andares, %s) ===" % [raio, _n(planta.get("andares", 3)), "em estado lastimável" if planta.get("estado") == "lastimavel" else "conservada"])
	print(colossal.get("texto", ""))
	if planta.get("piso_xadrez"):
		print("  Piso em xadrez preto e branco.")

	var raiz = Node3D.new()
	raiz.position = Vector3(0.0, 0.0, 0.0)
	add_child(raiz)
	_spawn_malhas_estufa(colossal.get("malhas", {}), planta, raiz)
	_spawn_flora_interna(colossal.get("flora_interna"), raiz)

	for porta in colossal.get("portas", []):
		var tipo = str(porta.get("tipo"))
		var pos = Vector2(porta.get("x", 0.0), porta.get("z", 0.0))
		var entrada = tipo == "entrada"
		print("  Portal de %s em (%.1f, %.1f), junto ao nó %s" % [tipo, pos.x, pos.y, _n(porta.get("no_id"))])
		_spawn_portal(pos, entrada)
		var no_id = int(porta.get("no_id", -1))
		if posicoes.has(no_id):
			_spawn_path(pos, posicoes[no_id], "trilha", _terreno_atual)


## Aro luminoso de pé na porta da estufa colossal, com rótulo e luz: verde
## na entrada, âmbar na saída.
func _spawn_portal(pos: Vector2, entrada: bool) -> void:
	var cor = Color(0.3, 1.0, 0.5) if entrada else Color(1.0, 0.7, 0.25)
	var aro = MeshInstance3D.new()
	var torus = TorusMesh.new()
	torus.inner_radius = 2.7
	torus.outer_radius = 3.1
	aro.mesh = torus
	aro.rotation.x = PI / 2.0
	aro.position = Vector3(pos.x, 3.2, pos.y)
	var material = StandardMaterial3D.new()
	material.albedo_color = cor
	material.emission_enabled = true
	material.emission = cor
	material.emission_energy_multiplier = 1.6
	aro.material_override = material
	add_child(aro)

	var luz = OmniLight3D.new()
	luz.light_color = cor
	luz.omni_range = 14.0
	luz.position = Vector3(pos.x, 3.2, pos.y)
	add_child(luz)

	var rotulo = Label3D.new()
	rotulo.text = "ENTRADA" if entrada else "SAÍDA"
	rotulo.font_size = 96
	rotulo.pixel_size = 0.02
	rotulo.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	rotulo.modulate = cor
	rotulo.position = Vector3(pos.x, 7.2, pos.y)
	add_child(rotulo)


## Instancia a torre e imprime o conteúdo de cada andar (ver
## `ynn.generator.generate_torre_conteudo`: uma mini-masmorra vertical, não
## só decoração — cada andar tem seu próprio conteúdo, o topo é sempre o
## mais raro/significativo). A hera (`hera_obj`, malhas de videira)
## é espalhada rente à base, cobrindo o pé da torre.
func _spawn_torre(plot: Dictionary, x: float, z: float, terreno) -> void:
	var conteudo = plot.get("conteudo", {})
	print("--- Torre em (%.1f, %.1f), %s andares ---" % [x, z, _n(conteudo.get("n_andares", "?"))])
	if plot.get("estado") == "ruina":
		print("  A torre está em ruínas: parte das paredes desabou, portas e venezianas caíram, o parapeito se desfez.")
	print("  Ferragens e parapeito: %s." % str(plot.get("estilo", "?")).replace("_", " "))
	for andar in conteudo.get("andares", []):
		var marca = " (topo)" if andar.get("numero") == conteudo.get("n_andares") else ""
		print("Andar %s%s: %s" % [_n(andar.get("numero")), marca, andar.get("texto", "")])
		if andar.get("tesouros") != null:
			for achado in andar.get("tesouros"):
				print("  Tesouro: %s" % achado)
		elif andar.get("tesouro") != null:
			print("  Tesouro: %s" % andar.get("tesouro"))
		if andar.get("livro_de_magias") != null:
			print("  Entre os livros, um livro de magias de 1º nível: %s" % andar.get("livro_de_magias").get("nome"))
		if andar.get("quadros") != null:
			print("  %s retratos, valendo %s de ouro no total" % [_n(andar.get("quadros").get("quantidade")), _n(andar.get("quadros").get("valor_ouro"))])
		if andar.get("biblioteca") != null:
			var b = andar.get("biblioteca")
			print("  Livros de magia: %s de 1º, %s de 2º, %s de 3º, %s de 4º, %s de 5º e 1 de 6º ou mais" % [_n(b.get("nivel_1")), _n(b.get("nivel_2")), _n(b.get("nivel_3")), _n(b.get("nivel_4")), _n(b.get("nivel_5"))])
		if andar.get("denizen") != null:
			print("  Encontro: %s" % andar.get("denizen"))
			var npc = andar.get("npc")
			if npc != null:
				print("  NPC: %s (PV %s, CA %s)" % [npc.get("classe"), _n(npc.get("pontos_de_vida")), _n(npc.get("classe_de_armadura"))])
			var creature = andar.get("criatura")
			if creature != null:
				print("  Criatura: %s (CA %s, DV %s, PV %s)" % [creature.get("nome"), _n(creature.get("ca")), creature.get("dv"), _n(creature.get("pontos_de_vida"))])

	var escalada = plot.get("escalada")
	if escalada != null:
		var andares_janela := []
		for a_janela in escalada.get("andares_com_janela"):
			andares_janela.append(_n(a_janela))
		print("  Porta térrea entreaberta; janelas de veneziana nos andares %s." % ", ".join(PackedStringArray(andares_janela)))
		print("  %s" % ("Trepadeiras sobem pela parede até as janelas." if escalada.get("trepadeiras") else "Sem trepadeiras: só o tijolo, pra quem quiser escalar."))
		print("  Escalada: %s" % escalada.get("regra"))

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

	if plot.has("malhas"):
		_spawn_malhas_torre(plot.get("malhas"), torre)
	else:
		_spawn_structure(plot.get("obj", ""), 0.0, 0.0, null, COLOR_TORRE, false, true, torre)

	var trepadeiras = plot.get("trepadeiras_obj")
	if trepadeiras != null and trepadeiras != "":
		print("  Trepadeiras sobem pelas paredes.")
		_spawn_structure(trepadeiras, 0.0, 0.0, null, COLOR_HERA, false, true, torre)

	for ivy_path in plot.get("hera_obj", []):
		_spawn_plant_cluster(ivy_path, 0.0, 0.0, null, ivy_radius, COLOR_HERA, ivy_inner_radius, 0.0, torre)

	var queimado = conteudo.get("topo_queimado")
	if queimado != null:
		print("  No topo, sem telhado: %s" % queimado.get("texto", ""))
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
		var extra: bool = andar.get("extra", false)
		var angulo = porta + PI + indice * 2.4 + (PI * 0.75 if extra else 0.0)  # longe da porta, girando a cada andar; o 2º do topo do outro lado
		var piso_y = indice * altura_andar + 0.05

		if not extra:
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

	# árvores de verdade (carvalho, salgueiro, pinheiro, araucária) têm de 5 a 30 m:
	# poucas por variante e bem mais espalhadas que uma touceira de arbustos
	var grande = str(area.get("especie_vegetacao")) in ARVORES_GRANDES
	for plant_path in area.get("plantas_obj", []):
		if grande:
			_spawn_plant_cluster(plant_path, base_x, base_z, terreno, scatter_radius * 5.0, COLOR_PLANTA, 0.0, 0.0, null, randi_range(1, 2))
		else:
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
	multimesh_instance.material_override = _material_planta(mesh, color)
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


## Material de uma planta: se a malha traz cor de vértice (as flores têm haste
## verde, corola e miolo coloridos, e cada flor uma cor), usa essa cor; senão
## a cor fixa `cor`.
var _malhas_coloridas := {}

func _material_planta(mesh, cor: Color, double_sided: bool = false) -> StandardMaterial3D:
	var colorida: bool = _malhas_coloridas.get(mesh, null) if _malhas_coloridas.has(mesh) else _tem_cor_de_vertice(mesh)
	_malhas_coloridas[mesh] = colorida
	if not colorida:
		return _material(cor, double_sided)
	var material = StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.roughness = 0.8
	return material


func _tem_cor_de_vertice(mesh) -> bool:
	if mesh == null or mesh.get_surface_count() == 0:
		return false
	var arrays = mesh.surface_get_arrays(0)
	return arrays.size() > Mesh.ARRAY_COLOR and arrays[Mesh.ARRAY_COLOR] != null


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
