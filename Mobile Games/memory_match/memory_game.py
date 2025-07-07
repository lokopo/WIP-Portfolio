import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
GRID_COLS = 4
GRID_ROWS = 4
CARD_WIDTH = 80
CARD_HEIGHT = 80
MARGIN = 10
GRID_X = (WINDOW_WIDTH - (GRID_COLS * CARD_WIDTH + (GRID_COLS - 1) * MARGIN)) // 2
GRID_Y = 150

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Card colors and symbols
CARD_COLORS = [BLUE, GREEN, RED, YELLOW, PURPLE, ORANGE, PINK, CYAN]
CARD_SYMBOLS = ['♠', '♥', '♦', '♣', '★', '♪', '♫', '☀']

class Card:
    def __init__(self, x, y, symbol, color):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.color = color
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_flipped = False
        self.is_matched = False
        self.flip_time = 0
        
    def flip(self):
        if not self.is_matched:
            self.is_flipped = not self.is_flipped
            self.flip_time = pygame.time.get_ticks()
            
    def draw(self, screen, font):
        if self.is_matched:
            # Matched cards are slightly transparent
            surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            surface.set_alpha(128)
            surface.fill(self.color)
            screen.blit(surface, (self.x, self.y))
            pygame.draw.rect(screen, GREEN, self.rect, 3)
        elif self.is_flipped:
            # Show the symbol and color
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            # Draw symbol
            text_surface = font.render(self.symbol, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        else:
            # Show card back
            pygame.draw.rect(screen, DARK_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            # Draw pattern on back
            pygame.draw.circle(screen, GRAY, self.rect.center, 20)

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

class MemoryGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Memory Match Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.card_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.cards = []
        self.flipped_cards = []
        self.matches = 0
        self.moves = 0
        self.game_won = False
        self.start_time = time.time()
        self.flip_back_time = 0
        self.game_level = 1
        
        # Difficulty settings
        self.difficulty = "Medium"
        self.total_pairs = 8
        
        # Control buttons
        button_width = 100
        button_height = 40
        button_y = WINDOW_HEIGHT - 100
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "NEW GAME", "new_game"),
            TouchButton(120, button_y, button_width, button_height, "EASY", "easy"),
            TouchButton(230, button_y, button_width, button_height, "HARD", "hard"),
            TouchButton(340, button_y, button_width, button_height, "HINT", "hint"),
        ]
        
        # Win screen button
        self.next_level_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 100, 
                                           150, 50, "NEXT LEVEL", "next_level")
        
        # Initialize game
        self.setup_game()
        
    def setup_game(self):
        self.cards = []
        self.flipped_cards = []
        self.matches = 0
        self.moves = 0
        self.game_won = False
        self.start_time = time.time()
        self.flip_back_time = 0
        
        # Create pairs of cards
        symbols = CARD_SYMBOLS[:self.total_pairs]
        colors = CARD_COLORS[:self.total_pairs]
        
        card_pairs = []
        for i in range(self.total_pairs):
            # Create two identical cards
            card_pairs.extend([{'symbol': symbols[i], 'color': colors[i]}] * 2)
            
        # Shuffle the cards
        random.shuffle(card_pairs)
        
        # Create card objects
        for i, card_data in enumerate(card_pairs):
            row = i // GRID_COLS
            col = i % GRID_COLS
            
            x = GRID_X + col * (CARD_WIDTH + MARGIN)
            y = GRID_Y + row * (CARD_HEIGHT + MARGIN)
            
            card = Card(x, y, card_data['symbol'], card_data['color'])
            self.cards.append(card)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_n:
                    self.setup_game()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click/touch
                    # Check button clicks
                    if self.game_won:
                        if self.next_level_button.is_clicked(event.pos):
                            self.next_level()
                    else:
                        button_clicked = False
                        for button in self.buttons:
                            if button.is_clicked(event.pos):
                                button.pressed = True
                                self.handle_button_action(button.action)
                                button_clicked = True
                                break
                                
                        # Check card clicks only if no button was clicked
                        if not button_clicked and len(self.flipped_cards) < 2:
                            for card in self.cards:
                                if card.rect.collidepoint(event.pos):
                                    if not card.is_flipped and not card.is_matched:
                                        card.flip()
                                        self.flipped_cards.append(card)
                                        
                                        if len(self.flipped_cards) == 2:
                                            self.moves += 1
                                            self.check_match()
                                        break
                                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Reset button states
                    for button in self.buttons:
                        button.pressed = False
                        
        return True
        
    def handle_button_action(self, action):
        if action == "new_game":
            self.setup_game()
        elif action == "easy":
            self.difficulty = "Easy"
            self.total_pairs = 6
            self.setup_game()
        elif action == "hard":
            self.difficulty = "Hard"
            self.total_pairs = 8
            self.setup_game()
        elif action == "hint":
            self.show_hint()
        elif action == "next_level":
            self.next_level()
            
    def show_hint(self):
        # Briefly show two unmatched cards
        unmatched_cards = [card for card in self.cards if not card.is_matched and not card.is_flipped]
        if len(unmatched_cards) >= 2:
            # Show first two cards for a brief moment
            hint_cards = random.sample(unmatched_cards, 2)
            for card in hint_cards:
                card.is_flipped = True
                
            # Set timer to flip them back
            self.flip_back_time = pygame.time.get_ticks() + 1000  # 1 second
            
    def next_level(self):
        self.game_level += 1
        self.total_pairs = min(8, 4 + self.game_level)
        self.setup_game()
        
    def check_match(self):
        if len(self.flipped_cards) == 2:
            card1, card2 = self.flipped_cards
            
            if card1.symbol == card2.symbol and card1.color == card2.color:
                # Match found
                card1.is_matched = True
                card2.is_matched = True
                self.matches += 1
                self.flipped_cards = []
                
                # Check if game is won
                if self.matches == self.total_pairs:
                    self.game_won = True
            else:
                # No match, flip back after a delay
                self.flip_back_time = pygame.time.get_ticks() + 1000  # 1 second
                
    def update(self):
        # Handle flipping cards back
        if self.flip_back_time > 0 and pygame.time.get_ticks() > self.flip_back_time:
            for card in self.flipped_cards:
                if not card.is_matched:
                    card.flip()
            self.flipped_cards = []
            self.flip_back_time = 0
            
        # Handle hint timeout
        if self.flip_back_time > 0:
            current_time = pygame.time.get_ticks()
            for card in self.cards:
                if card.is_flipped and not card.is_matched and card not in self.flipped_cards:
                    if current_time > self.flip_back_time:
                        card.flip()
                        
    def get_elapsed_time(self):
        if self.game_won:
            return int(time.time() - self.start_time)
        return int(time.time() - self.start_time)
        
    def calculate_score(self):
        # Score based on moves and time
        time_bonus = max(0, 300 - self.get_elapsed_time())
        move_penalty = self.moves * 2
        base_score = self.total_pairs * 100
        return max(0, base_score + time_bonus - move_penalty)
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.font.render("Memory Match", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen, self.card_font)
            
        # Draw UI
        self.draw_ui()
        
        # Draw control buttons
        for button in self.buttons:
            button.draw(self.screen)
            
        # Draw win screen
        if self.game_won:
            self.draw_win_screen()
            
        pygame.display.flip()
        
    def draw_ui(self):
        # Matches
        matches_text = self.small_font.render(f"Matches: {self.matches}/{self.total_pairs}", True, WHITE)
        self.screen.blit(matches_text, (10, 10))
        
        # Moves
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, WHITE)
        self.screen.blit(moves_text, (10, 35))
        
        # Time
        time_text = self.small_font.render(f"Time: {self.get_elapsed_time()}s", True, WHITE)
        self.screen.blit(time_text, (10, 60))
        
        # Level
        level_text = self.small_font.render(f"Level: {self.game_level}", True, WHITE)
        self.screen.blit(level_text, (WINDOW_WIDTH - 100, 10))
        
        # Difficulty
        difficulty_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        self.screen.blit(difficulty_text, (WINDOW_WIDTH - 120, 35))
        
        # Instructions
        if self.moves == 0:
            instruction_text = self.small_font.render("Tap cards to flip them", True, WHITE)
            self.screen.blit(instruction_text, (10, 85))
            
            instruction_text2 = self.small_font.render("Find matching pairs", True, WHITE)
            self.screen.blit(instruction_text2, (10, 105))
            
    def draw_win_screen(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Congratulations text
        congrats_text = self.font.render("LEVEL COMPLETE!", True, WHITE)
        text_rect = congrats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(congrats_text, text_rect)
        
        # Stats
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, WHITE)
        moves_rect = moves_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(moves_text, moves_rect)
        
        time_text = self.small_font.render(f"Time: {self.get_elapsed_time()} seconds", True, WHITE)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(time_text, time_rect)
        
        score_text = self.small_font.render(f"Score: {self.calculate_score()}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.small_font.render(f"Level: {self.game_level}", True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        self.screen.blit(level_text, level_rect)
        
        # Next level button
        self.next_level_button.draw(self.screen)
        
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
    game = MemoryGame()
    game.run()