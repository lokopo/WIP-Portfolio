extends Area2D

enum PowerUpType {HEALTH, SPEED_BOOST, JUMP_BOOST, DOUBLE_JUMP}

@export var powerup_type: PowerUpType = PowerUpType.HEALTH
@export var value: float = 1.0
@export var duration: float = 10.0  # For temporary power-ups
@export var rotation_speed: float = 90.0  # Degrees per second

@onready var sprite = $Sprite2D
@onready var animation_player = $AnimationPlayer

var is_collected = false

func _ready():
	# Set up the power-up appearance based on type
	setup_powerup_appearance()
	
	# Connect the body entered signal
	body_entered.connect(_on_body_entered)

func _process(delta):
	# Rotate the power-up
	if sprite and not is_collected:
		sprite.rotation_degrees += rotation_speed * delta

func setup_powerup_appearance():
	if not sprite:
		return
	
	match powerup_type:
		PowerUpType.HEALTH:
			sprite.modulate = Color.GREEN
		PowerUpType.SPEED_BOOST:
			sprite.modulate = Color.BLUE
		PowerUpType.JUMP_BOOST:
			sprite.modulate = Color.YELLOW
		PowerUpType.DOUBLE_JUMP:
			sprite.modulate = Color.PURPLE

func _on_body_entered(body):
	if body.has_method("collect_powerup") and not is_collected:
		body.collect_powerup(powerup_type, value, duration)
		collect()

func collect():
	is_collected = true
	
	# Play collection animation
	if animation_player:
		animation_player.play("collect")
		await animation_player.animation_finished
	
	# Or just disappear immediately if no animation
	queue_free()