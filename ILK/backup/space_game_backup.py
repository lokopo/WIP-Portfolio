from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import numpy as np
import os

app = Ursina(borderless=False)  # Make window resizable and movable

# Create a skybox
Sky()

# Create coordinate axis indicator
class AxisIndicator(Entity):
    def __init__(self):
        super().__init__(
            position=Vec3(0, 0, -5)  # Place it 5 units in front of spawn
        )
        self.rotation_speed = 100  # Degrees per second
        
        # Create the three poles
        self.x_pole = Entity(
            parent=self,
            model='cube',
            color=color.red,
            scale=(2, 0.1, 0.1),  # Long in X direction
            position=(1, 0, 0)  # Centered on its length
        )
        self.y_pole = Entity(
            parent=self,
            model='cube',
            color=color.green,
            scale=(0.1, 2, 0.1),  # Long in Y direction
            position=(0, 1, 0)  # Centered on its length
        )
        self.z_pole = Entity(
            parent=self,
            model='cube',
            color=color.blue,
            scale=(0.1, 0.1, 2),  # Long in Z direction
            position=(0, 0, 1)  # Centered on its length
        )

    def update(self):
        if not paused:
            rotation_amount = self.rotation_speed * time.dt
            
            # Get the current orientation vectors
            right = self.right
            up = self.up
            forward = self.forward
            
            # Rotate around local axes
            if held_keys['insert']:
                self.rotate(Vec3(rotation_amount, 0, 0), relative_to=self)
            if held_keys['delete']:
                self.rotate(Vec3(-rotation_amount, 0, 0), relative_to=self)
                
            if held_keys['page up']:
                self.rotate(Vec3(0, rotation_amount, 0), relative_to=self)
            if held_keys['page down']:
                self.rotate(Vec3(0, -rotation_amount, 0), relative_to=self)
                
            if held_keys['home']:
                self.rotate(Vec3(0, 0, rotation_amount), relative_to=self)
            if held_keys['end']:
                self.rotate(Vec3(0, 0, -rotation_amount), relative_to=self)

# Create the axis indicator
axis_indicator = AxisIndicator()

# Custom Space Controller
class SpaceController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 10
        self.mouse_sensitivity = Vec2(2000, 2000)  # Back to original value
        self.rotation_speed = 100
        
        # Set up camera exactly like RGB structure
        camera.parent = self
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        mouse.locked = True
        mouse.visible = False
        
        # Create player axis indicator (initially disabled)
        self.axis_indicator = Entity(parent=self)
        self.x_pole = Entity(
            parent=self.axis_indicator,
            model='cube',
            color=color.red,
            scale=(2, 0.1, 0.1),
            position=(1, 0, 0)
        )
        self.y_pole = Entity(
            parent=self.axis_indicator,
            model='cube',
            color=color.green,
            scale=(0.1, 2, 0.1),
            position=(0, 1, 0)
        )
        self.z_pole = Entity(
            parent=self.axis_indicator,
            model='cube',
            color=color.blue,
            scale=(0.1, 0.1, 2),
            position=(0, 0, 1)
        )
        self.axis_indicator.enabled = False
        
        # View mode
        self.third_person = False

    def update(self):
        if not paused:
            # Handle rotations with mouse velocity and time.dt
            rotation_amount_y = mouse.velocity[0] * self.mouse_sensitivity[0] * time.dt
            rotation_amount_x = mouse.velocity[1] * self.mouse_sensitivity[1] * time.dt
            
            # Apply rotations relative to self, like the RGB structure
            if abs(mouse.velocity[0]) > 0:
                self.rotate(Vec3(0, rotation_amount_y, 0), relative_to=self)
            if abs(mouse.velocity[1]) > 0:
                self.rotate(Vec3(-rotation_amount_x, 0, 0), relative_to=self)

            # Roll with Q/E (swapped)
            if held_keys['e']:  # Was Q before
                self.rotate(Vec3(0, 0, self.rotation_speed * time.dt), relative_to=self)
            if held_keys['q']:  # Was E before
                self.rotate(Vec3(0, 0, -self.rotation_speed * time.dt), relative_to=self)

            # Movement in local space
            move_direction = Vec3(0, 0, 0)
            if held_keys['w']: move_direction.z += 1
            if held_keys['s']: move_direction.z -= 1
            if held_keys['d']: move_direction.x += 1
            if held_keys['a']: move_direction.x -= 1
            
            # Transform the movement direction using local orientation vectors
            if move_direction.length() > 0:
                move_direction = move_direction.normalized()
                final_direction = (self.right * move_direction.x + self.forward * move_direction.z).normalized()
                self.position += final_direction * self.speed * time.dt
            
            # Vertical movement using local up vector
            if held_keys['space']:
                self.position += self.up * self.speed * time.dt
            if held_keys['shift']:
                self.position -= self.up * self.speed * time.dt

# Player setup with proper 3D movement
player = SpaceController()

# Create a pause menu
pause_panel = Panel(
    parent=camera.ui,
    model='quad',
    scale=(1, 1),
    color=color.black66,
    enabled=False
)

pause_text = Text(
    parent=pause_panel,
    text='PAUSED\nESC to Resume',
    origin=(0, 0),
    scale=2
)

# Add Return to Desktop button
quit_button = Button(
    parent=pause_panel,
    text='Return to Desktop',
    color=color.red.tint(-.2),
    highlight_color=color.red.tint(-.1),
    pressed_color=color.red.tint(-.3),
    scale=(0.3, 0.1),
    position=(0, -0.2),
    enabled=False
)

def quit_game():
    application.quit()

quit_button.on_click = quit_game

# Planet class
class Planet(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            model='sphere',
            color=color.random_color(),
            position=position,
            scale=random.uniform(1, 3),
            texture='white_cube',  # Basic texture
            collider='sphere'
        )
        # Add subtle rotation
        self.rotation_speed = Vec3(
            random.uniform(-10, 10),
            random.uniform(-10, 10),
            random.uniform(-10, 10)
        )
    
    def update(self):
        self.rotation += self.rotation_speed * time.dt

# Create planets
planets = []
for _ in range(15):  # More planets for a fuller space
    pos = Vec3(
        random.uniform(-20, 20),
        random.uniform(-20, 20),
        random.uniform(-20, 20)
    )
    # Don't spawn planets too close to the player
    if pos.length() > 5:
        planets.append(Planet(position=pos))

# Lighting
DirectionalLight(y=2, z=3, rotation=(45, -45, 45))
AmbientLight(color=Vec4(0.2, 0.2, 0.2, 1))

# Game state
paused = False

def update():
    if not paused:
        pass  # Remove the duplicate vertical movement code

def input(key):
    global paused
    
    if key == 'escape':
        paused = not paused
        pause_panel.enabled = paused
        quit_button.enabled = paused
        player.enabled = not paused
        mouse.locked = not paused
        if paused:
            mouse.visible = True
        else:
            mouse.visible = False
    
    if key == 'f6':  # Screenshot
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        # Use base.win.saveScreenshot() instead of window.screenshot
        base.win.saveScreenshot(Filename(f'screenshots/screenshot_{time.time()}.png'))
        print(f'Screenshot saved to screenshots folder')
    
    if key == 'f7':  # Toggle view and axis visibility
        player.third_person = not player.third_person
        player.axis_indicator.enabled = player.third_person
        if player.third_person:
            camera.position = (0, 0, -15)  # Move camera back
        else:
            camera.position = (0, 0, 0)  # Reset to first person
    
    if key == 'left mouse down' and not paused:
        # Shoot a projectile
        bullet = Entity(
            model='sphere',
            color=color.yellow,
            position=player.position,
            scale=0.2
        )
        bullet.animate_position(
            player.position + player.forward * 100,
            duration=2,
            curve=curve.linear
        )
        destroy(bullet, delay=2)

# Run the game
app.run() 