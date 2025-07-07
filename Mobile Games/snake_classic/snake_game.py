import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - 100) // GRID_SIZE  # Reserve space for UI

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)
GRAY = (128, 128, 128)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        
    def move(self):
        head = self.positions[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
            
        # Check self collision
        if new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
        
    def change_direction(self, direction):
        # Prevent reverse direction
        if (self.direction[0] * -1, self.direction[1] * -1) != direction:
            self.direction = direction
            
    def eat_food(self):
        self.grow = True
        
    def draw(self, screen):
        for i, pos in enumerate(self.positions):
            color = GREEN if i == 0 else DARK_GREEN
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE + 100, 
                             GRID_SIZE - 1, GRID_SIZE - 1)
            pygame.draw.rect(screen, color, rect)

class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)
        
    def generate_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), 
                   random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions:
                return pos
                
    def draw(self, screen):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                          self.position[1] * GRID_SIZE + 100, 
                          GRID_SIZE - 1, GRID_SIZE - 1)
        pygame.draw.rect(screen, RED, rect)

class TouchButton:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Classic - Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Touch controls
        self.touch_start = None
        self.min_swipe_distance = 50
        
        # UI Buttons
        button_width = 100
        button_height = 40
        button_y = WINDOW_HEIGHT - 80
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "PAUSE", "pause"),
            TouchButton(WINDOW_WIDTH - 110, button_y, button_width, button_height, "RESTART", "restart")
        ]
        
        # Game over button
        self.restart_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 50, 
                                        150, 50, "PLAY AGAIN", "restart")
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)
                        
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
                                if button.action == "pause":
                                    self.paused = not self.paused
                                elif button.action == "restart":
                                    self.restart_game()
                                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.touch_start:  # Touch release
                    self.handle_swipe(self.touch_start, event.pos)
                    self.touch_start = None
                    
        return True
        
    def handle_swipe(self, start_pos, end_pos):
        if self.game_over or self.paused:
            return
            
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Check if swipe is long enough
        if abs(dx) < self.min_swipe_distance and abs(dy) < self.min_swipe_distance:
            return
            
        # Determine swipe direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                self.snake.change_direction(RIGHT)
            else:
                self.snake.change_direction(LEFT)
        else:
            # Vertical swipe
            if dy > 0:
                self.snake.change_direction(DOWN)
            else:
                self.snake.change_direction(UP)
                
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Move snake
        if not self.snake.move():
            self.game_over = True
            return
            
        # Check food collision
        if self.snake.positions[0] == self.food.position:
            self.snake.eat_food()
            self.score += 10
            self.food = Food(self.snake.positions)
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game area border
        pygame.draw.rect(self.screen, WHITE, (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 200), 2)
        
        # Draw snake and food
        if not self.game_over:
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
            
        # Draw pause screen
        if self.paused and not self.game_over:
            self.draw_pause()
            
        pygame.display.flip()
        
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Length
        length_text = self.font.render(f"Length: {len(self.snake.positions)}", True, WHITE)
        self.screen.blit(length_text, (10, 50))
        
        # Instructions
        if self.score == 0:
            instruction_text = self.small_font.render("Swipe to move, tap buttons below", True, WHITE)
            self.screen.blit(instruction_text, (10, 70))
        
        # Buttons
        for button in self.buttons:
            button.draw(self.screen)
            
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
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(8)  # Slower speed for mobile
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()