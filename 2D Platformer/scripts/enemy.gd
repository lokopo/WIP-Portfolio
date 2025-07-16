extends CharacterBody2D

@export var speed = 100.0
@export var patrol_distance = 200.0
@export var damage = 1
@export var health = 3

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var start_position: Vector2
var patrol_direction = 1
var is_patrolling = true
var player_detected = false
var player = null

@onready var sprite = $Sprite2D
@onready var animation_player = $AnimationPlayer

func _ready():
	start_position = position
	if sprite:
		sprite.flip_h = false

func _physics_process(delta):
	# Add gravity
	if not is_on_floor():
		velocity.y += gravity * delta
	
	# Handle movement
	if is_patrolling:
		patrol_movement(delta)
	elif player_detected and player:
		chase_player(delta)
	
	move_and_slide()
	
	# Flip sprite based on direction
	if sprite and velocity.x != 0:
		sprite.flip_h = velocity.x < 0

func patrol_movement(delta):
	velocity.x = patrol_direction * speed
	
	# Check if we've reached patrol limits
	if position.x > start_position.x + patrol_distance:
		patrol_direction = -1
	elif position.x < start_position.x - patrol_distance:
		patrol_direction = 1
	
	# Check for walls or edges
	if is_on_wall() or (is_on_floor() and not is_on_floor()):
		patrol_direction *= -1

func chase_player(delta):
	if player and is_instance_valid(player):
		var direction = (player.global_position - global_position).normalized()
		velocity.x = direction.x * speed * 1.5
	else:
		player_detected = false
		is_patrolling = true

func _on_detection_area_body_entered(body):
	if body.has_method("take_damage") and body.name == "Player":
		player = body
		player_detected = true
		is_patrolling = false

func _on_detection_area_body_exited(body):
	if body == player:
		player_detected = false
		is_patrolling = true
		player = null

func take_damage(amount):
	health -= amount
	if health <= 0:
		queue_free()
	else:
		# Flash effect when hit
		if sprite:
			sprite.modulate = Color.RED
			await get_tree().create_timer(0.1).timeout
			sprite.modulate = Color.WHITE

func _on_hitbox_body_entered(body):
	if body.has_method("take_damage") and body.name == "Player":
		body.take_damage(damage)