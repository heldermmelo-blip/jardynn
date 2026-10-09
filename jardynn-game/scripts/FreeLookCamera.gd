extends Camera3D

## Câmera livre de debug (`Camera3D`) pra navegar e inspecionar a cena gerada;
## não é controle de jogador. WASD move no plano da câmera, E sobe e Q desce
## (eixo Y do mundo), Shift acelera, e segurar o botão direito do mouse captura
## o cursor e gira a câmera (yaw/pitch). Os `@export` ajustam velocidade,
## multiplicador do Shift e sensibilidade do mouse.

@export var move_speed: float = 24.0
@export var boost_multiplier: float = 3.0
@export var mouse_sensitivity: float = 0.003

var _looking: bool = false
var _yaw: float = 0.0
var _pitch: float = 0.0

## Lê a rotação inicial da câmera pra que o primeiro movimento do mouse
## parta da orientação que ela já tem na cena.
func _ready() -> void:
	_yaw = rotation.y
	_pitch = rotation.x


## Botão direito liga/desliga o modo de olhar (captura/solta o mouse); com ele
## ligado, o movimento do mouse atualiza yaw/pitch, com pitch limitado a +-1.5 rad.
func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT:
		_looking = event.pressed
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if _looking else Input.MOUSE_MODE_VISIBLE

	if event is InputEventMouseMotion and _looking:
		_yaw -= event.relative.x * mouse_sensitivity
		_pitch -= event.relative.y * mouse_sensitivity
		_pitch = clamp(_pitch, -1.5, 1.5)
		rotation = Vector3(_pitch, _yaw, 0)


## Move a câmera por quadro: soma as direções das teclas pressionadas,
## normaliza e aplica `move_speed * delta` (vezes `boost_multiplier` com Shift).
func _process(delta: float) -> void:
	var direction = Vector3.ZERO
	if Input.is_key_pressed(KEY_W):
		direction -= transform.basis.z
	if Input.is_key_pressed(KEY_S):
		direction += transform.basis.z
	if Input.is_key_pressed(KEY_A):
		direction -= transform.basis.x
	if Input.is_key_pressed(KEY_D):
		direction += transform.basis.x
	if Input.is_key_pressed(KEY_E):
		direction += Vector3.UP
	if Input.is_key_pressed(KEY_Q):
		direction -= Vector3.UP

	if direction.length() > 0.0:
		direction = direction.normalized()
		var speed = move_speed * (boost_multiplier if Input.is_key_pressed(KEY_SHIFT) else 1.0)
		position += direction * speed * delta
