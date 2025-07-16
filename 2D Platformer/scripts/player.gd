extends CharacterBody2D

signal level_completed

@export var speed = 300.0
@export var jump_force = -400.0
@export var acceleration = 1500.0
@export var friction = 1000.0
@export var max_health = 3
@export var invincibility_time = 1.0

# Get the gravity from the project settings to be synced with RigidBody nodes
var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

# Respawn position
var respawn_position: Vector2
var current_health: int
var is_invincible = false
var invincibility_timer: Timer

@onready var sprite = $Sprite2D
@onready var animation_player = $AnimationPlayer

func _ready():
	# Store initial position as respawn position
	respawn_position = position
	current_health = max_health
	
	# Create invincibility timer
	invincibility_timer = Timer.new()
	invincibility_timer.wait_time = invincibility_time
	invincibility_timer.one_shot = true
	invincibility_timer.timeout.connect(_on_invincibility_timeout)
	add_child(invincibility_timer)
	
	# Add to player group for UI to find
	add_to_group("player")
	
	# Update UI
	update_health_display()

func _physics_process(delta):
	# Add the gravity
	if not is_on_floor():
		velocity.y += gravity * delta

	# Handle Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_force

	# Get the input direction and handle the movement/deceleration
	var direction = Input.get_axis("move_left", "move_right")
	if direction:
		velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0, friction * delta)

	move_and_slide()
	
	# Check if player fell below the ground
	if position.y > 800:
		respawn()

func respawn():
	# Reset position and velocity
	position = respawn_position
	velocity = Vector2.ZERO
	current_health = max_health
	is_invincible = false
	update_health_display()
	
	if sprite:
		sprite.modulate = Color.WHITE

func take_damage(amount):
	if is_invincible:
		return
	
	current_health -= amount
	update_health_display()
	
	if current_health <= 0:
		# Player died
		respawn()
	else:
		# Start invincibility
		is_invincible = true
		invincibility_timer.start()
		
		# Flash effect
		if sprite:
			flash_effect()

func flash_effect():
	var tween = create_tween()
	tween.set_loops(6)  # Flash 3 times (6 color changes)
	tween.tween_property(sprite, "modulate", Color.RED, 0.1)
	tween.tween_property(sprite, "modulate", Color.WHITE, 0.1)

func _on_invincibility_timeout():
	is_invincible = false

func update_health_display():
	# This will be connected to a UI element
	# For now, we'll just print to console
	print("Health: ", current_health, "/", max_health)

func get_health():
	return {"current": current_health, "max": max_health}

func heal(amount):
	current_health = min(current_health + amount, max_health)
	update_health_display()

func collect_powerup(powerup_type, value, duration):
	match powerup_type:
		0:  # HEALTH
			heal(int(value))
			print("Health power-up collected!")
		1:  # SPEED_BOOST
			apply_speed_boost(value, duration)
			print("Speed boost power-up collected!")
		2:  # JUMP_BOOST
			apply_jump_boost(value, duration)
			print("Jump boost power-up collected!")
		3:  # DOUBLE_JUMP
			enable_double_jump(duration)
			print("Double jump power-up collected!")

func apply_speed_boost(multiplier, duration):
	var original_speed = speed
	speed *= multiplier
	
	# Create a timer to reset the speed
	var timer = Timer.new()
	timer.wait_time = duration
	timer.one_shot = true
	timer.timeout.connect(func(): speed = original_speed; timer.queue_free())
	add_child(timer)
	timer.start()

func apply_jump_boost(multiplier, duration):
	var original_jump_force = jump_force
	jump_force *= multiplier
	
	# Create a timer to reset the jump force
	var timer = Timer.new()
	timer.wait_time = duration
	timer.one_shot = true
	timer.timeout.connect(func(): jump_force = original_jump_force; timer.queue_free())
	add_child(timer)
	timer.start()

func enable_double_jump(duration):
	# This would require additional logic for double jump
	# For now, we'll just increase jump force temporarily
	apply_jump_boost(1.5, duration)

func complete_level(level_number: int):
	print("Level ", level_number, " completed!")
	# Emit signal for level manager
	level_completed.emit() 