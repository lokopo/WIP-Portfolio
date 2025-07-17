extends Node

signal level_completed(level_number: int)
signal game_completed

@export var current_level: int = 1
@export var total_levels: int = 3

var level_scenes = {
	1: "res://scenes/level_1.tscn",
	2: "res://scenes/level_2.tscn", 
	3: "res://scenes/level_3.tscn"
}

var current_level_scene: Node
var player: Node2D

func _ready():
	# Find the player
	player = get_tree().get_first_node_in_group("player")
	
	# Connect to level completion signals
	if player:
		player.connect("level_completed", _on_level_completed)

func load_level(level_number: int):
	if level_number > total_levels:
		game_completed.emit()
		return
	
	current_level = level_number
	
	# Load the level scene
	var level_scene_path = level_scenes.get(level_number, "res://scenes/main.tscn")
	var level_scene = load(level_scene_path)
	
	if level_scene:
		# Remove current level if it exists
		if current_level_scene:
			current_level_scene.queue_free()
		
		# Instance and add the new level
		current_level_scene = level_scene.instantiate()
		get_tree().current_scene.add_child(current_level_scene)
		
		# Reset player position
		if player:
			player.respawn()
		
		print("Loaded level ", level_number)

func next_level():
	load_level(current_level + 1)

func restart_level():
	load_level(current_level)

func _on_level_completed():
	level_completed.emit(current_level)
	
	# Wait a moment then load next level
	await get_tree().create_timer(2.0).timeout
	next_level()

func get_level_progress():
	return {
		"current": current_level,
		"total": total_levels,
		"percentage": (float(current_level) / float(total_levels)) * 100.0
	}