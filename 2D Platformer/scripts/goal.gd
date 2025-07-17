extends Area2D

@export var level_number: int = 1
@export var is_final_goal: bool = false

@onready var sprite = $Sprite2D
@onready var animation_player = $AnimationPlayer

var is_triggered = false

func _ready():
	# Set up the goal appearance
	if sprite:
		if is_final_goal:
			sprite.modulate = Color.GOLD
		else:
			sprite.modulate = Color.GREEN
	
	# Connect the body entered signal
	body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if body.has_method("complete_level") and not is_triggered:
		is_triggered = true
		body.complete_level(level_number)
		
		# Play completion animation
		if animation_player:
			animation_player.play("complete")
		else:
			# Simple scale animation
			var tween = create_tween()
			tween.tween_property(sprite, "scale", Vector2(1.5, 1.5), 0.3)
			tween.tween_property(sprite, "scale", Vector2(1.0, 1.0), 0.3)
		
		# Show completion message
		show_completion_message()

func show_completion_message():
	var message = "Level " + str(level_number) + " Completed!"
	if is_final_goal:
		message = "Congratulations! You've completed the game!"
	
	# Find UI manager and show message
	var ui_manager = get_tree().get_first_node_in_group("ui_manager")
	if ui_manager and ui_manager.has_method("show_completion_message"):
		ui_manager.show_completion_message(message)
	else:
		print(message)