import pygame
import random
import math
import sys

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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game settings
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
BALL_SIZE = 12
BALL_SPEED = 5
BRICK_WIDTH = 45
BRICK_HEIGHT = 20
BRICK_ROWS = 8
BRICK_COLS = 10

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - 50
        self.speed = PADDLE_SPEED
        
    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.get_rect())
        pygame.draw.rect(screen, GRAY, self.get_rect(), 2)

class Ball:
    def __init__(self):
        self.size = BALL_SIZE
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.dx = random.choice([-1, 1]) * BALL_SPEED
        self.dy = -BALL_SPEED
        self.stuck = True
        
    def move(self):
        if not self.stuck:
            self.x += self.dx
            self.y += self.dy
            
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        
    def bounce_x(self):
        self.dx = -self.dx
        
    def bounce_y(self):
        self.dy = -self.dy
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.dx = random.choice([-1, 1]) * BALL_SPEED
        self.dy = -BALL_SPEED
        self.stuck = True
        
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 2)

class Brick:
    def __init__(self, x, y, color, points=10):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.points = points
        self.destroyed = False
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, self.get_rect())
            pygame.draw.rect(screen, WHITE, self.get_rect(), 1)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.type = power_type
        self.speed = 2
        self.active = True
        
        # Different power-up types
        self.types = {
            'expand': {'color': GREEN, 'symbol': 'E'},
            'shrink': {'color': RED, 'symbol': 'S'},
            'multi_ball': {'color': BLUE, 'symbol': 'M'},
            'life': {'color': YELLOW, 'symbol': 'L'}
        }
        
    def move(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.active = False
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen, font):
        if self.active:
            color = self.types[self.type]['color']
            symbol = self.types[self.type]['symbol']
            
            pygame.draw.rect(screen, color, self.get_rect())
            pygame.draw.rect(screen, WHITE, self.get_rect(), 2)
            
            text = font.render(symbol, True, WHITE)
            text_rect = text.get_rect(center=self.get_rect().center)
            screen.blit(text, text_rect)

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

class BreakoutGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Breakout Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game objects
        self.paddle = Paddle()
        self.balls = [Ball()]
        self.bricks = []
        self.powerups = []
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.game_won = False
        self.paused = False
        
        # Touch controls
        self.touch_start = None
        self.min_swipe_distance = 30
        
        # Control buttons
        button_width = 80
        button_height = 40
        button_y = WINDOW_HEIGHT - 120
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "LEFT", "left"),
            TouchButton(100, button_y, button_width, button_height, "RIGHT", "right"),
            TouchButton(190, button_y, button_width, button_height, "LAUNCH", "launch"),
            TouchButton(280, button_y, button_width, button_height, "PAUSE", "pause"),
            TouchButton(370, button_y, button_width, button_height, "RESTART", "restart")
        ]
        
        # Game over button
        self.restart_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 50, 
                                        150, 50, "PLAY AGAIN", "restart")
        
        # Initialize game
        self.create_bricks()
        
    def create_bricks(self):
        self.bricks = []
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE]
        
        start_x = (WINDOW_WIDTH - BRICK_COLS * BRICK_WIDTH) // 2
        start_y = 80
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * BRICK_WIDTH
                y = start_y + row * BRICK_HEIGHT
                color = colors[row % len(colors)]
                points = (BRICK_ROWS - row) * 10
                
                brick = Brick(x, y, color, points)
                self.bricks.append(brick)
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    if self.balls[0].stuck:
                        self.balls[0].stuck = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.paddle.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.paddle.move(1)
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click/touch
                    self.touch_start = event.pos
                    
                    # Check button clicks
                    if self.game_over or self.game_won:
                        if self.restart_button.is_clicked(event.pos):
                            self.restart_game()
                    else:
                        for button in self.buttons:
                            if button.is_clicked(event.pos):
                                button.pressed = True
                                self.handle_button_action(button.action)
                                
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
            self.paddle.move(-1)
        elif action == "right":
            self.paddle.move(1)
        elif action == "launch":
            if self.balls[0].stuck:
                self.balls[0].stuck = False
        elif action == "pause":
            self.paused = not self.paused
        elif action == "restart":
            self.restart_game()
            
    def handle_swipe(self, start_pos, end_pos):
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Check if swipe is long enough
        if abs(dx) < self.min_swipe_distance and abs(dy) < self.min_swipe_distance:
            # Tap to launch ball
            if self.balls[0].stuck:
                self.balls[0].stuck = False
            return
            
        # Determine swipe direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                self.paddle.move(1)
            else:
                self.paddle.move(-1)
        else:
            # Vertical swipe up = launch
            if dy < 0 and self.balls[0].stuck:
                self.balls[0].stuck = False
                
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Update balls
        for ball in self.balls[:]:
            if ball.stuck:
                # Ball follows paddle when stuck
                ball.x = self.paddle.x + self.paddle.width // 2
                ball.y = self.paddle.y - ball.size
            else:
                ball.move()
                
                # Wall collisions
                if ball.x - ball.size//2 <= 0 or ball.x + ball.size//2 >= WINDOW_WIDTH:
                    ball.bounce_x()
                if ball.y - ball.size//2 <= 0:
                    ball.bounce_y()
                    
                # Paddle collision
                if ball.get_rect().colliderect(self.paddle.get_rect()):
                    if ball.dy > 0:  # Ball is moving down
                        ball.bounce_y()
                        
                        # Add spin based on where ball hits paddle
                        hit_pos = (ball.x - self.paddle.x) / self.paddle.width
                        ball.dx = (hit_pos - 0.5) * BALL_SPEED * 2
                        
                # Ball fell off screen
                if ball.y > WINDOW_HEIGHT:
                    self.balls.remove(ball)
                    
        # Check if all balls are gone
        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.balls = [Ball()]
                
        # Brick collisions
        for ball in self.balls:
            for brick in self.bricks:
                if not brick.destroyed and ball.get_rect().colliderect(brick.get_rect()):
                    brick.destroyed = True
                    self.score += brick.points
                    
                    # Simple bounce (can be improved)
                    ball.bounce_y()
                    
                    # Chance to spawn power-up
                    if random.random() < 0.1:  # 10% chance
                        power_type = random.choice(['expand', 'shrink', 'multi_ball', 'life'])
                        powerup = PowerUp(brick.x + brick.width//2, brick.y + brick.height, power_type)
                        self.powerups.append(powerup)
                    
                    break
                    
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.move()
            
            # Check collision with paddle
            if powerup.get_rect().colliderect(self.paddle.get_rect()):
                self.apply_powerup(powerup.type)
                self.powerups.remove(powerup)
            elif not powerup.active:
                self.powerups.remove(powerup)
                
        # Check win condition
        if all(brick.destroyed for brick in self.bricks):
            self.level += 1
            self.create_bricks()
            # Speed up ball slightly
            for ball in self.balls:
                ball.dx *= 1.1
                ball.dy *= 1.1
                
    def apply_powerup(self, power_type):
        if power_type == 'expand':
            self.paddle.width = min(120, self.paddle.width + 20)
        elif power_type == 'shrink':
            self.paddle.width = max(40, self.paddle.width - 20)
        elif power_type == 'multi_ball':
            if len(self.balls) < 5:
                new_ball = Ball()
                new_ball.x = self.balls[0].x
                new_ball.y = self.balls[0].y
                new_ball.dx = random.choice([-1, 1]) * BALL_SPEED
                new_ball.dy = -BALL_SPEED
                new_ball.stuck = False
                self.balls.append(new_ball)
        elif power_type == 'life':
            self.lives += 1
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game objects
        if not self.game_over:
            self.paddle.draw(self.screen)
            
            for ball in self.balls:
                ball.draw(self.screen)
                
            for brick in self.bricks:
                brick.draw(self.screen)
                
            for powerup in self.powerups:
                powerup.draw(self.screen, self.small_font)
                
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
        
    def draw_ui(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 35))
        
        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WINDOW_WIDTH - 100, 10))
        
        # Instructions
        if self.balls[0].stuck:
            instruction_text = self.small_font.render("Tap LAUNCH or swipe up to start", True, WHITE)
            self.screen.blit(instruction_text, (10, 60))
            
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
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
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
        self.paddle = Paddle()
        self.balls = [Ball()]
        self.bricks = []
        self.powerups = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.game_won = False
        self.paused = False
        self.create_bricks()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BreakoutGame()
    game.run()