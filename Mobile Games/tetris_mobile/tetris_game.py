import pygame
import random
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
GRID_X = (WINDOW_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Tetromino shapes
SHAPES = [
    [['.....',
      '..#..',
      '.###.',
      '.....',
      '.....'],
     ['.....',
      '.#...',
      '.##..',
      '.#...',
      '.....'],
     ['.....',
      '.....',
      '.###.',
      '..#..',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '..#..',
      '.....']],
    [['.....',
      '.....',
      '.##..',
      '.##..',
      '.....']],
    [['.....',
      '.....',
      '.###.',
      '.#...',
      '.....'],
     ['.....',
      '.##..',
      '..#..',
      '..#..',
      '.....'],
     ['.....',
      '.....',
      '...#.',
      '.###.',
      '.....'],
     ['.....',
      '.#...',
      '.#...',
      '.##..',
      '.....']],
    [['.....',
      '.....',
      '.###.',
      '...#.',
      '.....'],
     ['.....',
      '..#..',
      '..#..',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.###.',
      '.....'],
     ['.....',
      '.##..',
      '.#...',
      '.#...',
      '.....']],
    [['.....',
      '.....',
      '..##.',
      '.##..',
      '.....'],
     ['.....',
      '.#...',
      '.##..',
      '..#..',
      '.....']],
    [['.....',
      '.....',
      '.##..',
      '..##.',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '.#...',
      '.....']],
    [['.....',
      '.....',
      '.###.',
      '..#..',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '..#..',
      '.....'],
     ['.....',
      '..#..',
      '.###.',
      '.....',
      '.....'],
     ['.....',
      '.#...',
      '.##..',
      '.#...',
      '.....']]
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, BLUE, RED, GREEN, ORANGE]

class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.randint(0, len(SHAPES) - 1)
        self.color = SHAPE_COLORS[self.shape]
        self.rotation = 0
        
    def get_shape(self):
        return SHAPES[self.shape][self.rotation]
        
    def get_rotated_shape(self):
        return SHAPES[self.shape][(self.rotation + 1) % len(SHAPES[self.shape])]

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        # Touch controls
        self.touch_start = None
        self.min_swipe_distance = 30
        self.last_move_time = 0
        self.move_delay = 150  # milliseconds
        
        # Control buttons
        button_width = 70
        button_height = 50
        button_y = WINDOW_HEIGHT - 120
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "LEFT", "left"),
            TouchButton(90, button_y, button_width, button_height, "RIGHT", "right"),
            TouchButton(170, button_y, button_width, button_height, "ROTATE", "rotate"),
            TouchButton(250, button_y, button_width, button_height, "DOWN", "down"),
            TouchButton(330, button_y, button_width, button_height, "DROP", "drop"),
            TouchButton(10, button_y + 60, button_width, button_height, "PAUSE", "pause"),
            TouchButton(90, button_y + 60, button_width, button_height, "RESTART", "restart")
        ]
        
        # Game over button
        self.restart_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 100, 
                                        150, 50, "PLAY AGAIN", "restart")
        
    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 2, 0)
        
    def valid_move(self, piece, dx, dy, rotation=None):
        if rotation is None:
            rotation = piece.rotation
            
        shape = SHAPES[piece.shape][rotation]
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    x = piece.x + j + dx
                    y = piece.y + i + dy
                    
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                        return False
                    if y >= 0 and self.grid[y][x]:
                        return False
                        
        return True
        
    def place_piece(self, piece):
        shape = piece.get_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    x = piece.x + j
                    y = piece.y + i
                    if y >= 0:
                        self.grid[y][x] = piece.color
                        
    def clear_lines(self):
        lines_to_clear = []
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines_to_clear.append(i)
                
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared
        
        # Scoring
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared == 4:
            self.score += 800 * self.level
            
        # Level up
        if self.lines_cleared >= self.level * 10:
            self.level += 1
            self.fall_speed = max(50, self.fall_speed - 50)
            
    def handle_events(self):
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_RETURN:
                        self.drop_piece()
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click/touch
                    self.touch_start = event.pos
                    
                    # Check button clicks
                    if self.game_over:
                        if self.restart_button.is_clicked(event.pos):
                            self.restart_game()
                    else:
                        for button in self.buttons:
                            if button.is_clicked(event.pos):
                                button.pressed = True
                                if current_time - self.last_move_time > self.move_delay:
                                    self.handle_button_action(button.action)
                                    self.last_move_time = current_time
                                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Handle swipe
                    if self.touch_start and not self.game_over and not self.paused:
                        self.handle_swipe(self.touch_start, event.pos)
                    self.touch_start = None
                    
                    # Reset button states
                    for button in self.buttons:
                        button.pressed = False
                        
        return True
        
    def handle_button_action(self, action):
        if self.game_over or self.paused:
            if action == "pause":
                self.paused = not self.paused
            elif action == "restart":
                self.restart_game()
            return
            
        if action == "left":
            self.move_piece(-1, 0)
        elif action == "right":
            self.move_piece(1, 0)
        elif action == "down":
            self.move_piece(0, 1)
        elif action == "rotate":
            self.rotate_piece()
        elif action == "drop":
            self.drop_piece()
        elif action == "pause":
            self.paused = not self.paused
        elif action == "restart":
            self.restart_game()
            
    def handle_swipe(self, start_pos, end_pos):
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Check if swipe is long enough
        if abs(dx) < self.min_swipe_distance and abs(dy) < self.min_swipe_distance:
            return
            
        # Determine swipe direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                self.move_piece(1, 0)
            else:
                self.move_piece(-1, 0)
        else:
            # Vertical swipe
            if dy > 0:
                self.drop_piece()
            else:
                self.rotate_piece()
                
    def move_piece(self, dx, dy):
        if self.valid_move(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
        
    def rotate_piece(self):
        new_rotation = (self.current_piece.rotation + 1) % len(SHAPES[self.current_piece.shape])
        if self.valid_move(self.current_piece, 0, 0, new_rotation):
            self.current_piece.rotation = new_rotation
            
    def drop_piece(self):
        while self.move_piece(0, 1):
            pass
            
    def update(self):
        if self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Handle continuous button presses
        for button in self.buttons:
            if button.pressed and current_time - self.last_move_time > self.move_delay:
                self.handle_button_action(button.action)
                self.last_move_time = current_time
                
        # Piece falling
        self.fall_time += self.clock.get_time()
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.place_piece(self.current_piece)
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
                
                # Check game over
                if not self.valid_move(self.current_piece, 0, 0):
                    self.game_over = True
                    
            self.fall_time = 0
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        self.draw_grid()
        
        # Draw current piece
        if not self.game_over:
            self.draw_piece(self.current_piece)
            
        # Draw UI
        self.draw_ui()
        
        # Draw control buttons
        for button in self.buttons:
            button.draw(self.screen)
            
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
            
        # Draw pause screen
        if self.paused and not self.game_over:
            self.draw_pause()
            
        pygame.display.flip()
        
    def draw_grid(self):
        # Draw grid background
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (GRID_X, GRID_Y, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        
        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    rect = pygame.Rect(GRID_X + x * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE, 
                                     BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)
                    
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (GRID_X + x * BLOCK_SIZE, GRID_Y), 
                           (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT * BLOCK_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (GRID_X, GRID_Y + y * BLOCK_SIZE), 
                           (GRID_X + GRID_WIDTH * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE))
            
    def draw_piece(self, piece):
        shape = piece.get_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    x = GRID_X + (piece.x + j) * BLOCK_SIZE
                    y = GRID_Y + (piece.y + i) * BLOCK_SIZE
                    if y >= GRID_Y:  # Only draw if visible
                        rect = pygame.Rect(x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        pygame.draw.rect(self.screen, piece.color, rect)
                        
    def draw_ui(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 35))
        
        # Lines
        lines_text = self.small_font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (WINDOW_WIDTH - 100, 10))
        
        # Next piece
        next_text = self.small_font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (WINDOW_WIDTH - 100, 100))
        
        # Draw next piece
        if self.next_piece:
            shape = self.next_piece.get_shape()
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell == '#':
                        x = WINDOW_WIDTH - 90 + j * 15
                        y = 130 + i * 15
                        rect = pygame.Rect(x, y, 14, 14)
                        pygame.draw.rect(self.screen, self.next_piece.color, rect)
                        
    def draw_game_over(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # Level reached
        level_text = self.small_font.render(f"Level Reached: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(level_text, level_rect)
        
        # Restart button
        self.restart_button.draw(self.screen)
        
    def draw_pause(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        # Resume instruction
        resume_text = self.small_font.render("Tap PAUSE to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        self.screen.blit(resume_text, resume_rect)
        
    def restart_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.fall_time = 0
        self.fall_speed = 500
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()