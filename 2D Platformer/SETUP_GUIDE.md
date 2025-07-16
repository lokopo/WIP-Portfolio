# 2D Platformer Setup Guide

This guide explains how to set up and use all the new features added to the 2D Platformer project.

## New Features Overview

### 1. Enemy System
- **File**: `scripts/enemy.gd`
- **Features**: Patrol behavior, player detection, damage dealing
- **Setup**: Add to CharacterBody2D with DetectionArea and Hitbox children

### 2. Power-up System
- **File**: `scripts/powerup.gd`
- **Types**: Health, Speed Boost, Jump Boost, Double Jump
- **Setup**: Add to Area2D with Sprite2D and CollisionShape2D

### 3. Health System
- **File**: `scripts/player.gd` (enhanced)
- **Features**: Health points, damage, invincibility frames, visual feedback
- **Setup**: Automatically included in player script

### 4. Level Completion
- **File**: `scripts/goal.gd`
- **Features**: Level completion triggers, progress tracking
- **Setup**: Add to Area2D with Sprite2D and CollisionShape2D

### 5. UI System
- **File**: `scripts/ui_manager.gd`
- **Features**: Health display, power-up messages, completion notifications
- **Setup**: Add to CanvasLayer as Control node

### 6. Save System
- **File**: `scripts/save_system.gd`
- **Features**: Progress saving, statistics tracking, settings
- **Setup**: Add as Node to main scene

### 7. Level Manager
- **File**: `scripts/level_manager.gd`
- **Features**: Level progression, scene loading, game completion
- **Setup**: Add as Node to main scene

## Quick Setup Instructions

### 1. Set up the Player
1. Open your player scene (`scenes/player.tscn`)
2. Make sure the player script (`scripts/player.gd`) is attached
3. Add the player to the "player" group in the script

### 2. Add Enemies
1. Create a CharacterBody2D node
2. Attach the `scripts/enemy.gd` script
3. Add a Sprite2D child (red color for visibility)
4. Add a CollisionShape2D child for the enemy body
5. Add an Area2D child named "DetectionArea" with a larger CollisionShape2D
6. Add an Area2D child named "Hitbox" with a CollisionShape2D
7. Connect the signals:
   - `DetectionArea.body_entered` → `_on_detection_area_body_entered`
   - `DetectionArea.body_exited` → `_on_detection_area_body_exited`
   - `Hitbox.body_entered` → `_on_hitbox_body_entered`

### 3. Add Power-ups
1. Create an Area2D node
2. Attach the `scripts/powerup.gd` script
3. Set the `powerup_type` export variable (0=Health, 1=Speed, 2=Jump, 3=Double Jump)
4. Add a Sprite2D child (color-coded based on type)
5. Add a CollisionShape2D child
6. The script will automatically handle collection

### 4. Add Level Goals
1. Create an Area2D node
2. Attach the `scripts/goal.gd` script
3. Set the `level_number` export variable
4. Add a Sprite2D child (green for regular, gold for final)
5. Add a CollisionShape2D child
6. The script will automatically handle level completion

### 5. Set up UI
1. Create a CanvasLayer node
2. Add a Control node as child
3. Attach the `scripts/ui_manager.gd` script
4. Add a Label child named "HealthLabel"
5. Add a Label child named "PowerupLabel" (initially hidden)

### 6. Add Game Systems
1. Add a Node with `scripts/level_manager.gd` script
2. Add a Node with `scripts/save_system.gd` script
3. These will automatically handle game progression and saving

## Example Scene Structure

```
Main Scene
├── Player (CharacterBody2D with player.gd)
├── UI (CanvasLayer)
│   └── UIManager (Control with ui_manager.gd)
│       ├── HealthLabel
│       └── PowerupLabel
├── LevelManager (Node with level_manager.gd)
├── SaveSystem (Node with save_system.gd)
├── Platforms (Node2D)
│   └── [Platform StaticBody2D nodes]
├── Enemies (Node2D)
│   └── Enemy (CharacterBody2D with enemy.gd)
│       ├── Sprite2D
│       ├── CollisionShape2D
│       ├── DetectionArea (Area2D)
│       └── Hitbox (Area2D)
├── Powerups (Node2D)
│   └── Powerup (Area2D with powerup.gd)
│       ├── Sprite2D
│       └── CollisionShape2D
└── Goal (Area2D with goal.gd)
    ├── Sprite2D
    └── CollisionShape2D
```

## Testing the Features

1. **Player Health**: The player starts with 3 health points. Take damage from enemies to test the health system.

2. **Enemy AI**: Enemies will patrol back and forth. When the player gets close, they will chase the player.

3. **Power-ups**: Collect the colored power-ups to test different effects:
   - Green: Health restoration
   - Blue: Speed boost (temporary)
   - Yellow: Jump boost (temporary)
   - Purple: Double jump (temporary)

4. **Level Completion**: Reach the green goal to complete the level.

5. **Save System**: Progress is automatically saved. Check the console for save/load messages.

## Customization

### Enemy Behavior
- Modify `speed`, `patrol_distance`, `damage`, and `health` in the enemy script
- Adjust detection area size for different detection ranges

### Power-up Effects
- Change `value` and `duration` in power-up script
- Add new power-up types by extending the enum

### Player Stats
- Adjust `max_health`, `invincibility_time`, `speed`, and `jump_force` in player script

### Level Design
- Create multiple level scenes and add them to the level manager's `level_scenes` dictionary
- Use the demo level as a template for new levels

## Troubleshooting

### Common Issues
1. **Player not taking damage**: Make sure the player is in the "player" group
2. **Enemies not detecting player**: Check that DetectionArea signals are connected
3. **Power-ups not working**: Verify the player has the `collect_powerup` method
4. **UI not updating**: Ensure UI manager is in the "ui_manager" group

### Debug Tips
- Check the console for debug messages
- Use the Godot debugger to inspect node properties
- Verify all required child nodes are present
- Test signals and connections in the Godot editor