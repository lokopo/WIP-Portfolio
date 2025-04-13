extends CharacterBody2D

@export var speed = 300.0
@export var jump_force = -400.0
@export var acceleration = 1500.0
@export var friction = 1000.0

# Get the gravity from the project settings to be synced with RigidBody nodes
var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

# Respawn position
var respawn_position: Vector2

func _ready():
	# Store initial position as respawn position
	respawn_position = position

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