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
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - self.height - 10
        self.speed = 5
        self.bullets = []
        self.bullet_speed = 7
        self.lives = 3
        self.score = 0
        
    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x))
        
    def shoot(self):
        if len(self.bullets) < 5:  # Limit bullets
            bullet = {
                'x': self.x + self.width // 2,
                'y': self.y,
                'active': True
            }
            self.bullets.append(bullet)
            
    def update(self):
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
                
    def draw(self, screen):
        # Draw player (triangle)
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, YELLOW, (int(bullet['x']), int(bullet['y'])), 3)

class Invader:
    def __init__(self, x, y, invader_type=0):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.type = invader_type
        self.speed = 1
        self.direction = 1
        self.move_down = False
        self.alive = True
        
    def update(self):
        if self.move_down:
            self.y += 20
            self.move_down = False
            self.direction *= -1
        else:
            self.x += self.speed * self.direction
            
    def draw(self, screen):
        if self.alive:
            colors = [RED, BLUE, CYAN]
            color = colors[self.type]
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
            # Draw simple invader pattern
            pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 5, 5))
            pygame.draw.rect(screen, WHITE, (self.x + 20, self.y + 5, 5, 5))

class TouchButton:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 24)
        self.pressed = False
        
    def draw(self, screen):
        color = (64, 64, 64) if self.pressed else GRAY
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
        pygame.display.set_caption("Space Invaders Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game objects
        self.player = Player()
        self.invaders = []
        self.enemy_bullets = []
        self.stars = []
        
        # Game state
        self.game_over = False
        self.paused = False
        self.wave = 1
        self.last_enemy_shot = 0
        self.enemy_shot_delay = 2000  # milliseconds
        
        # Touch controls
        self.touch_start = None
        self.min_swipe_distance = 30
        
        # Control buttons
        button_width = 80
        button_height = 50
        button_y = WINDOW_HEIGHT - 60
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "LEFT", "left"),
            TouchButton(100, button_y, button_width, button_height, "RIGHT", "right"),
            TouchButton(190, button_y, button_width, button_height, "SHOOT", "shoot"),
            TouchButton(280, button_y, button_width, button_height, "PAUSE", "pause"),
            TouchButton(370, button_y, button_width, button_height, "RESTART", "restart")
        ]
        
        # Game over button
        self.restart_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 50, 
                                        150, 50, "PLAY AGAIN", "restart")
        
        # Initialize game
        self.create_invaders()
        self.create_stars()
        
    def create_invaders(self):
        self.invaders = []
        rows = 5
        cols = 8
        start_x = 50
        start_y = 100
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * 40
                y = start_y + row * 30
                invader_type = min(row, 2)  # Different types for different rows
                self.invaders.append(Invader(x, y, invader_type))
                
    def create_stars(self):
        self.stars = []
        for _ in range(50):
            star = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(0.5, 2.0)
            }
            self.stars.append(star)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.player.shoot()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.player.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(1)
                        
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
            self.player.move(-1)
        elif action == "right":
            self.player.move(1)
        elif action == "shoot":
            self.player.shoot()
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
                self.player.move(1)
            else:
                self.player.move(-1)
        else:
            # Vertical swipe up = shoot
            if dy < 0:
                self.player.shoot()
                
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Update player
        self.player.update()
        
        # Update invaders
        edge_hit = False
        for invader in self.invaders:
            if invader.alive:
                invader.update()
                if invader.x <= 0 or invader.x + invader.width >= WINDOW_WIDTH:
                    edge_hit = True
                    
        # Move invaders down if edge hit
        if edge_hit:
            for invader in self.invaders:
                if invader.alive:
                    invader.move_down = True
                    
        # Check invader collisions with player bullets
        for bullet in self.player.bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            for invader in self.invaders:
                if invader.alive:
                    invader_rect = pygame.Rect(invader.x, invader.y, invader.width, invader.height)
                    if bullet_rect.colliderect(invader_rect):
                        invader.alive = False
                        self.player.bullets.remove(bullet)
                        self.player.score += (invader.type + 1) * 10
                        break
                        
        # Enemy shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_shot > self.enemy_shot_delay:
            alive_invaders = [inv for inv in self.invaders if inv.alive]
            if alive_invaders:
                shooter = random.choice(alive_invaders)
                enemy_bullet = {
                    'x': shooter.x + shooter.width // 2,
                    'y': shooter.y + shooter.height,
                    'active': True
                }
                self.enemy_bullets.append(enemy_bullet)
                self.last_enemy_shot = current_time
                
        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet['y'] += 3
            if bullet['y'] > WINDOW_HEIGHT:
                self.enemy_bullets.remove(bullet)
                
        # Check enemy bullet collisions with player
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for bullet in self.enemy_bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            if bullet_rect.colliderect(player_rect):
                self.enemy_bullets.remove(bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                    
        # Check if invaders reached player
        for invader in self.invaders:
            if invader.alive and invader.y + invader.height >= self.player.y:
                self.game_over = True
                
        # Check if all invaders destroyed
        if not any(invader.alive for invader in self.invaders):
            self.wave += 1
            self.create_invaders()
            self.enemy_shot_delay = max(1000, self.enemy_shot_delay - 200)
            
        # Update stars
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > WINDOW_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WINDOW_WIDTH)
                
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(self.screen, WHITE, (int(star['x']), int(star['y'])), 1)
            
        # Draw game objects
        if not self.game_over:
            self.player.draw(self.screen)
            
            for invader in self.invaders:
                invader.draw(self.screen)
                
            # Draw enemy bullets
            for bullet in self.enemy_bullets:
                pygame.draw.circle(self.screen, RED, (int(bullet['x']), int(bullet['y'])), 3)
                
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
        score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 35))
        
        # Wave
        wave_text = self.small_font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (WINDOW_WIDTH - 100, 10))
        
        # Instructions
        if self.player.score == 0:
            instruction_text = self.small_font.render("Swipe to move, up to shoot", True, WHITE)
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
        final_score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # Wave reached
        wave_text = self.small_font.render(f"Wave Reached: {self.wave}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
        self.screen.blit(wave_text, wave_rect)
        
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
        self.player = Player()
        self.invaders = []
        self.enemy_bullets = []
        self.game_over = False
        self.paused = False
        self.wave = 1
        self.last_enemy_shot = 0
        self.enemy_shot_delay = 2000
        self.create_invaders()
        
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
    game = Game()
    game.run()