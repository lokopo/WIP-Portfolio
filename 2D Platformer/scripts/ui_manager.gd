extends Control

@onready var health_label = $HealthLabel
@onready var powerup_timer = $PowerupTimer
@onready var powerup_label = $PowerupLabel

var player: Node2D

func _ready():
	# Find the player node
	player = get_tree().get_first_node_in_group("player")
	if player:
		# Connect to player's health update signal (we'll add this later)
		player.connect("health_changed", _on_player_health_changed)
		update_health_display()

func _on_player_health_changed(current_health, max_health):
	update_health_display(current_health, max_health)

func update_health_display(current_health = null, max_health = null):
	if not health_label:
		return
	
	if current_health == null or max_health == null:
		# Try to get from player
		if player and player.has_method("get_health"):
			var health_data = player.get_health()
			current_health = health_data.current
			max_health = health_data.max
	
	if current_health != null and max_health != null:
		health_label.text = "Health: %d/%d" % [current_health, max_health]
		
		# Change color based on health
		if current_health <= max_health * 0.3:
			health_label.modulate = Color.RED
		elif current_health <= max_health * 0.6:
			health_label.modulate = Color.YELLOW
		else:
			health_label.modulate = Color.GREEN

func show_powerup_message(message: String, duration: float = 3.0):
	if powerup_label:
		powerup_label.text = message
		powerup_label.visible = true
		
		# Hide after duration
		await get_tree().create_timer(duration).timeout
		powerup_label.visible = false

func _on_powerup_collected(powerup_type: String, duration: float):
	var message = "Power-up collected: " + powerup_type
	show_powerup_message(message, duration)