import pygame
import sys
import os
import subprocess

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Game information
GAMES = [
    {
        'name': 'Snake Classic',
        'description': 'Classic snake game with touch controls',
        'file': 'snake_classic/snake_game.py',
        'color': GREEN,
        'icon': '🐍',
        'difficulty': 'Easy'
    },
    {
        'name': 'Tetris Mobile',
        'description': 'Block-stacking puzzle game',
        'file': 'tetris_mobile/tetris_game.py',
        'color': BLUE,
        'icon': '🧩',
        'difficulty': 'Medium'
    },
    {
        'name': 'Space Invaders',
        'description': 'Classic arcade shooter',
        'file': 'space_invaders/space_game.py',
        'color': PURPLE,
        'icon': '👾',
        'difficulty': 'Medium'
    },
    {
        'name': 'Puzzle Slider',
        'description': 'Number sliding puzzle',
        'file': 'puzzle_slider/puzzle_game.py',
        'color': ORANGE,
        'icon': '🔢',
        'difficulty': 'Easy'
    },
    {
        'name': 'Memory Match',
        'description': 'Card matching memory game',
        'file': 'memory_match/memory_game.py',
        'color': YELLOW,
        'icon': '🧠',
        'difficulty': 'Easy'
    },
    {
        'name': 'Breakout',
        'description': 'Ball and paddle arcade game',
        'file': 'breakout/breakout_game.py',
        'color': RED,
        'icon': '🎯',
        'difficulty': 'Medium'
    }
]

class GameButton:
    def __init__(self, x, y, width, height, game_info):
        self.rect = pygame.Rect(x, y, width, height)
        self.game_info = game_info
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 28)
        self.icon_font = pygame.font.Font(None, 48)
        self.pressed = False
        self.hover = False
        
    def draw(self, screen):
        # Base color
        color = self.game_info['color']
        if self.hover:
            # Lighten color on hover
            color = tuple(min(255, c + 30) for c in color)
        if self.pressed:
            # Darken color when pressed
            color = tuple(max(0, c - 30) for c in color)
            
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        
        # Draw icon
        icon_text = self.icon_font.render(self.game_info['icon'], True, WHITE)
        icon_rect = icon_text.get_rect()
        icon_rect.centerx = self.rect.centerx
        icon_rect.y = self.rect.y + 10
        screen.blit(icon_text, icon_rect)
        
        # Draw title
        title_text = self.title_font.render(self.game_info['name'], True, WHITE)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.rect.centerx
        title_rect.y = self.rect.y + 70
        screen.blit(title_text, title_rect)
        
        # Draw description
        desc_lines = self.wrap_text(self.game_info['description'], self.rect.width - 20)
        y_offset = 100
        for line in desc_lines:
            desc_text = self.font.render(line, True, WHITE)
            desc_rect = desc_text.get_rect()
            desc_rect.centerx = self.rect.centerx
            desc_rect.y = self.rect.y + y_offset
            screen.blit(desc_text, desc_rect)
            y_offset += 25
            
        # Draw difficulty
        diff_text = self.font.render(f"Difficulty: {self.game_info['difficulty']}", True, WHITE)
        diff_rect = diff_text.get_rect()
        diff_rect.centerx = self.rect.centerx
        diff_rect.y = self.rect.bottom - 30
        screen.blit(diff_text, diff_rect)
        
    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, WHITE)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
        
    def update_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

class TouchButton:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 24)
        self.pressed = False
        
    def draw(self, screen):
        color = DARK_GRAY if self.pressed else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class GameLauncher:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mobile Games Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Scrolling
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Create game buttons
        self.game_buttons = []
        button_width = WINDOW_WIDTH - 40
        button_height = 160
        y_offset = 120
        
        for i, game in enumerate(GAMES):
            x = 20
            y = y_offset + i * (button_height + 20)
            button = GameButton(x, y, button_width, button_height, game)
            self.game_buttons.append(button)
            
        # Calculate max scroll
        total_height = len(GAMES) * (button_height + 20) + y_offset + 100
        self.max_scroll = max(0, total_height - WINDOW_HEIGHT)
        
        # Control buttons
        button_width = 100
        button_height = 40
        button_y = WINDOW_HEIGHT - 60
        
        self.control_buttons = [
            TouchButton(WINDOW_WIDTH - 220, button_y, button_width, button_height, "ABOUT", "about"),
            TouchButton(WINDOW_WIDTH - 110, button_y, button_width, button_height, "EXIT", "exit")
        ]
        
        # Touch controls
        self.touch_start = None
        self.last_mouse_pos = (0, 0)
        
        # About dialog
        self.show_about = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click/touch
                    self.touch_start = event.pos
                    
                    if self.show_about:
                        self.show_about = False
                        continue
                    
                    # Check control buttons
                    for button in self.control_buttons:
                        if button.is_clicked(event.pos):
                            button.pressed = True
                            if button.action == "about":
                                self.show_about = True
                            elif button.action == "exit":
                                return False
                                
                    # Check game buttons
                    adjusted_pos = (event.pos[0], event.pos[1] + self.scroll_y)
                    for button in self.game_buttons:
                        if button.is_clicked(adjusted_pos):
                            button.pressed = True
                            self.launch_game(button.game_info)
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.touch_start = None
                    
                    # Reset button states
                    for button in self.control_buttons:
                        button.pressed = False
                    for button in self.game_buttons:
                        button.pressed = False
                        
            elif event.type == pygame.MOUSEMOTION:
                self.last_mouse_pos = event.pos
                
                # Handle scrolling
                if self.touch_start and not self.show_about:
                    dy = self.touch_start[1] - event.pos[1]
                    self.scroll_y += dy * 2
                    self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
                    self.touch_start = event.pos
                    
                # Update hover states
                adjusted_pos = (event.pos[0], event.pos[1] + self.scroll_y)
                for button in self.game_buttons:
                    button.update_hover(adjusted_pos)
                    
        return True
        
    def launch_game(self, game_info):
        try:
            # Get the directory of this launcher script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            game_path = os.path.join(current_dir, game_info['file'])
            
            if os.path.exists(game_path):
                print(f"Launching {game_info['name']}...")
                # Close the launcher
                pygame.quit()
                
                # Launch the game
                subprocess.run([sys.executable, game_path])
                
                # Restart the launcher after game closes
                pygame.init()
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                pygame.display.set_caption("Mobile Games Launcher")
                
            else:
                print(f"Game file not found: {game_path}")
                
        except Exception as e:
            print(f"Error launching game: {e}")
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.font.render("🎮 Mobile Games", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.small_font.render("Choose a game to play", True, GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Create a surface for scrollable content
        scroll_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT * 2))
        scroll_surface.fill(BLACK)
        
        # Draw game buttons on scroll surface
        for button in self.game_buttons:
            button.draw(scroll_surface)
            
        # Blit the visible portion of the scroll surface
        visible_rect = pygame.Rect(0, self.scroll_y, WINDOW_WIDTH, WINDOW_HEIGHT - 80)
        self.screen.blit(scroll_surface, (0, 0), visible_rect)
        
        # Draw control buttons (always visible)
        for button in self.control_buttons:
            button.draw(self.screen)
            
        # Draw scroll indicator
        if self.max_scroll > 0:
            indicator_height = max(20, int((WINDOW_HEIGHT - 200) * (WINDOW_HEIGHT - 200) / (self.max_scroll + WINDOW_HEIGHT - 200)))
            indicator_y = 100 + int((WINDOW_HEIGHT - 300) * self.scroll_y / self.max_scroll)
            
            pygame.draw.rect(self.screen, DARK_GRAY, (WINDOW_WIDTH - 10, 100, 8, WINDOW_HEIGHT - 200))
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH - 10, indicator_y, 8, indicator_height))
            
        # Draw about dialog
        if self.show_about:
            self.draw_about()
            
        # Draw instructions at bottom
        if not self.show_about:
            instruction_text = self.small_font.render("Swipe to scroll • Tap to select", True, GRAY)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
            self.screen.blit(instruction_text, instruction_rect)
            
        pygame.display.flip()
        
    def draw_about(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # About box
        box_width = WINDOW_WIDTH - 40
        box_height = 400
        box_x = 20
        box_y = (WINDOW_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, DARK_GRAY, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), 3)
        
        # About text
        about_lines = [
            "🎮 Mobile Games Collection",
            "",
            "Created for Android devices using Python & Pygame",
            "",
            "Features:",
            "• 6 classic arcade games",
            "• Touch-optimized controls",
            "• Works on Pydroid 3",
            "• Open source code",
            "",
            "Perfect for learning Python game development!",
            "",
            "Tap anywhere to close"
        ]
        
        y_offset = box_y + 20
        for line in about_lines:
            if line.startswith("🎮"):
                text = self.font.render(line, True, WHITE)
            else:
                text = self.small_font.render(line, True, WHITE)
                
            text_rect = text.get_rect()
            text_rect.centerx = WINDOW_WIDTH // 2
            text_rect.y = y_offset
            self.screen.blit(text, text_rect)
            
            if line.startswith("🎮"):
                y_offset += 40
            else:
                y_offset += 25
                
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()