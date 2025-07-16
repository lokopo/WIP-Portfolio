# 2D Platformer

![Status: In Progress](https://img.shields.io/badge/Status-In%20Progress-yellow)

## Project Status
🚧 This project is currently under development. 🚧

### What's Working
- Basic player movement with improved physics
- Health system with damage and invincibility
- Enemy AI with patrol and chase behavior
- Power-ups system (Health, Speed Boost, Jump Boost, Double Jump)
- Level progression system
- Save system for game progress
- UI system for health display and power-up messages
- Goal/checkpoint system for level completion
- Collision detection and respawn mechanics

### Recently Added
- ✅ Enemy AI with detection zones
- ✅ Power-ups with temporary effects
- ✅ Health system with visual feedback
- ✅ Level completion system
- ✅ Save/load functionality
- ✅ UI improvements

### In Progress
- Multiple level designs
- Sound effects and music integration
- Particle effects for visual polish

### Planned Features
- Boss battles
- More enemy types
- Advanced power-ups
- Level editor
- Multiplayer support

## Description
A 2D platformer game built with Godot Engine. This game features classic platforming mechanics with modern twists, including unique power-ups, challenging levels, and engaging gameplay.

## Project Structure

- `assets/`: Contains all game assets
  - `sprites/`: Image assets
  - `music/`: Background music
  - `sounds/`: Sound effects
- `scripts/`: Contains all GDScript files
  - `player.gd`: Player movement, health, and power-up collection
  - `enemy.gd`: Enemy AI with patrol and chase behavior
  - `powerup.gd`: Power-up system with different types
  - `goal.gd`: Level completion triggers
  - `ui_manager.gd`: User interface management
  - `level_manager.gd`: Level progression and loading
  - `save_system.gd`: Game save/load functionality
- `scenes/`: Contains all Godot scene files

## Controls

- Left Arrow or A: Move left
- Right Arrow or D: Move right
- Space: Jump
- E: Interact/Use power-up

## Running the Game

1. Open Godot Engine
2. Click "Import" and select this project folder
3. Click the "Play" button or press F5 to run the game

## Development

To modify the game:
1. Open the project in Godot Engine
2. Navigate to the `scenes` folder to edit game scenes
3. Navigate to the `scripts` folder to edit game logic
4. Add new assets to the appropriate folders in `assets/`

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License
MIT License 