extends Node

const SAVE_FILE = "user://savegame.save"

var save_data = {
	"current_level": 1,
	"max_level_unlocked": 1,
	"total_deaths": 0,
	"total_powerups_collected": 0,
	"best_time": {},
	"settings": {
		"sound_enabled": true,
		"music_enabled": true,
		"fullscreen": false
	}
}

func _ready():
	load_game()

func save_game():
	var file = FileAccess.open(SAVE_FILE, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(save_data))
		file.close()
		print("Game saved successfully!")

func load_game():
	if FileAccess.file_exists(SAVE_FILE):
		var file = FileAccess.open(SAVE_FILE, FileAccess.READ)
		if file:
			var json_string = file.get_as_text()
			file.close()
			
			var json = JSON.new()
			var parse_result = json.parse(json_string)
			
			if parse_result == OK:
				save_data = json.data
				print("Game loaded successfully!")
			else:
				print("Error parsing save file!")
	else:
		print("No save file found, starting new game.")

func update_progress(level_number: int, completed: bool = false):
	if completed:
		save_data.max_level_unlocked = max(save_data.max_level_unlocked, level_number + 1)
		save_data.current_level = level_number + 1
	else:
		save_data.current_level = level_number
	
	save_game()

func increment_death_count():
	save_data.total_deaths += 1
	save_game()

func increment_powerup_count():
	save_data.total_powerups_collected += 1
	save_game()

func update_best_time(level_number: int, time: float):
	if not save_data.best_time.has(str(level_number)) or time < save_data.best_time[str(level_number)]:
		save_data.best_time[str(level_number)] = time
		save_game()

func get_save_data():
	return save_data

func reset_save_data():
	save_data = {
		"current_level": 1,
		"max_level_unlocked": 1,
		"total_deaths": 0,
		"total_powerups_collected": 0,
		"best_time": {},
		"settings": {
			"sound_enabled": true,
			"music_enabled": true,
			"fullscreen": false
		}
	}
	save_game()
	print("Save data reset!")

func update_setting(setting_name: String, value):
	if save_data.settings.has(setting_name):
		save_data.settings[setting_name] = value
		save_game()