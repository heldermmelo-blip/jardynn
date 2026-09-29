extends Camera3D

## Câmera livre de debug: WASD move, Q/E sobe/desce, botão direito do mouse
## segura pra olhar em volta, Shift acelera. Só pra navegar e inspecionar a
## cena gerada — não é controle de jogador.

@export var move_speed: float = 24.0
@export var boost_multiplier: float = 3.0
@export var mouse_sensitivity: float = 0.003

var _looking: bool = false
var _yaw: float = 0.0
var _pitch: float = 0.0

func _ready() -> void:
	_yaw = rotation.y
	_pitch = rotation.x


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT:
		_looking = event.pressed
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if _looking else Input.MOUSE_MODE_VISIBLE

	if event is InputEventMouseMotion and _looking:
		_yaw -= event.relative.x * mouse_sensitivity
		_pitch -= event.relative.y * mouse_sensitivity
		_pitch = clamp(_pitch, -1.5, 1.5)
		rotation = Vector3(_pitch, _yaw, 0)


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
