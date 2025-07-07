import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
GRID_SIZE = 4
TILE_SIZE = 100
GRID_X = (WINDOW_WIDTH - GRID_SIZE * TILE_SIZE) // 2
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

class PuzzleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sliding Puzzle Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.tile_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.moves = 0
        self.game_won = False
        self.start_time = pygame.time.get_ticks()
        
        # Difficulty settings
        self.difficulty = "Medium"
        self.shuffle_moves = 100
        
        # Control buttons
        button_width = 100
        button_height = 40
        button_y = WINDOW_HEIGHT - 100
        
        self.buttons = [
            TouchButton(10, button_y, button_width, button_height, "SHUFFLE", "shuffle"),
            TouchButton(120, button_y, button_width, button_height, "RESET", "reset"),
            TouchButton(230, button_y, button_width, button_height, "EASY", "easy"),
            TouchButton(340, button_y, button_width, button_height, "HARD", "hard"),
            TouchButton(120, button_y + 50, button_width, button_height, "HINT", "hint")
        ]
        
        # Win screen button
        self.new_game_button = TouchButton(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 100, 
                                         150, 50, "NEW GAME", "new_game")
        
        # Initialize puzzle
        self.initialize_puzzle()
        
    def initialize_puzzle(self):
        # Create solved puzzle
        num = 1
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if row == GRID_SIZE - 1 and col == GRID_SIZE - 1:
                    self.grid[row][col] = 0  # Empty space
                else:
                    self.grid[row][col] = num
                    num += 1
                    
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.shuffle_puzzle()
        
    def shuffle_puzzle(self):
        # Shuffle by making random valid moves
        for _ in range(self.shuffle_moves):
            possible_moves = self.get_possible_moves()
            if possible_moves:
                move = random.choice(possible_moves)
                self.make_move(move[0], move[1])
                
        self.moves = 0
        self.game_won = False
        self.start_time = pygame.time.get_ticks()
        
    def get_possible_moves(self):
        moves = []
        empty_row, empty_col = self.empty_pos
        
        # Check all four directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row, new_col = empty_row + dr, empty_col + dc
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                moves.append((new_row, new_col))
                
        return moves
        
    def make_move(self, row, col):
        empty_row, empty_col = self.empty_pos
        
        # Check if the move is valid (adjacent to empty space)
        if abs(row - empty_row) + abs(col - empty_col) == 1:
            # Swap tile with empty space
            self.grid[empty_row][empty_col] = self.grid[row][col]
            self.grid[row][col] = 0
            self.empty_pos = (row, col)
            self.moves += 1
            
            # Check if puzzle is solved
            if self.is_solved():
                self.game_won = True
                
    def is_solved(self):
        num = 1
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if row == GRID_SIZE - 1 and col == GRID_SIZE - 1:
                    if self.grid[row][col] != 0:
                        return False
                else:
                    if self.grid[row][col] != num:
                        return False
                    num += 1
        return True
        
    def get_tile_at_pos(self, pos):
        x, y = pos
        if GRID_X <= x < GRID_X + GRID_SIZE * TILE_SIZE and GRID_Y <= y < GRID_Y + GRID_SIZE * TILE_SIZE:
            col = (x - GRID_X) // TILE_SIZE
            row = (y - GRID_Y) // TILE_SIZE
            return (row, col)
        return None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_s:
                    self.shuffle_puzzle()
                elif event.key == pygame.K_r:
                    self.initialize_puzzle()
                elif not self.game_won:
                    empty_row, empty_col = self.empty_pos
                    if event.key == pygame.K_UP and empty_row < GRID_SIZE - 1:
                        self.make_move(empty_row + 1, empty_col)
                    elif event.key == pygame.K_DOWN and empty_row > 0:
                        self.make_move(empty_row - 1, empty_col)
                    elif event.key == pygame.K_LEFT and empty_col < GRID_SIZE - 1:
                        self.make_move(empty_row, empty_col + 1)
                    elif event.key == pygame.K_RIGHT and empty_col > 0:
                        self.make_move(empty_row, empty_col - 1)
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click/touch
                    # Check button clicks
                    if self.game_won:
                        if self.new_game_button.is_clicked(event.pos):
                            self.initialize_puzzle()
                    else:
                        for button in self.buttons:
                            if button.is_clicked(event.pos):
                                button.pressed = True
                                self.handle_button_action(button.action)
                                
                        # Check tile clicks
                        tile_pos = self.get_tile_at_pos(event.pos)
                        if tile_pos and not self.game_won:
                            row, col = tile_pos
                            if self.grid[row][col] != 0:  # Not empty tile
                                self.make_move(row, col)
                                
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Reset button states
                    for button in self.buttons:
                        button.pressed = False
                        
        return True
        
    def handle_button_action(self, action):
        if action == "shuffle":
            self.shuffle_puzzle()
        elif action == "reset":
            self.initialize_puzzle()
        elif action == "easy":
            self.difficulty = "Easy"
            self.shuffle_moves = 50
            self.shuffle_puzzle()
        elif action == "hard":
            self.difficulty = "Hard"
            self.shuffle_moves = 200
            self.shuffle_puzzle()
        elif action == "hint":
            self.show_hint()
        elif action == "new_game":
            self.initialize_puzzle()
            
    def show_hint(self):
        # Find a tile that can move towards its correct position
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] != 0:
                    tile_num = self.grid[row][col]
                    correct_row = (tile_num - 1) // GRID_SIZE
                    correct_col = (tile_num - 1) % GRID_SIZE
                    
                    # Check if this tile can move towards correct position
                    empty_row, empty_col = self.empty_pos
                    if abs(row - empty_row) + abs(col - empty_col) == 1:
                        # This tile can move, check if it gets closer to correct position
                        current_distance = abs(row - correct_row) + abs(col - correct_col)
                        new_distance = abs(empty_row - correct_row) + abs(empty_col - correct_col)
                        
                        if new_distance < current_distance:
                            # Flash this tile as a hint
                            self.hint_tile = (row, col)
                            return
                            
    def get_elapsed_time(self):
        if self.game_won:
            return (pygame.time.get_ticks() - self.start_time) // 1000
        return (pygame.time.get_ticks() - self.start_time) // 1000
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.font.render("Sliding Puzzle", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw grid
        self.draw_grid()
        
        # Draw UI
        self.draw_ui()
        
        # Draw control buttons
        for button in self.buttons:
            button.draw(self.screen)
            
        # Draw win screen
        if self.game_won:
            self.draw_win_screen()
            
        pygame.display.flip()
        
    def draw_grid(self):
        # Draw grid background
        pygame.draw.rect(self.screen, LIGHT_GRAY, 
                        (GRID_X - 5, GRID_Y - 5, GRID_SIZE * TILE_SIZE + 10, GRID_SIZE * TILE_SIZE + 10))
        
        # Draw tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                tile_num = self.grid[row][col]
                x = GRID_X + col * TILE_SIZE
                y = GRID_Y + row * TILE_SIZE
                
                if tile_num == 0:
                    # Empty space
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # Number tile
                    # Choose color based on correct position
                    correct_row = (tile_num - 1) // GRID_SIZE
                    correct_col = (tile_num - 1) % GRID_SIZE
                    
                    if row == correct_row and col == correct_col:
                        tile_color = GREEN
                    else:
                        tile_color = BLUE
                        
                    pygame.draw.rect(self.screen, tile_color, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE), 2)
                    
                    # Draw number
                    text_surface = self.tile_font.render(str(tile_num), True, WHITE)
                    text_rect = text_surface.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    self.screen.blit(text_surface, text_rect)
                    
    def draw_ui(self):
        # Moves
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, WHITE)
        self.screen.blit(moves_text, (10, 10))
        
        # Time
        time_text = self.small_font.render(f"Time: {self.get_elapsed_time()}s", True, WHITE)
        self.screen.blit(time_text, (10, 35))
        
        # Difficulty
        difficulty_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        self.screen.blit(difficulty_text, (WINDOW_WIDTH - 150, 10))
        
        # Instructions
        if self.moves == 0:
            instruction_text = self.small_font.render("Tap tiles to move them", True, WHITE)
            self.screen.blit(instruction_text, (10, 60))
            
            instruction_text2 = self.small_font.render("Arrange numbers 1-15 in order", True, WHITE)
            self.screen.blit(instruction_text2, (10, 80))
            
    def draw_win_screen(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Congratulations text
        congrats_text = self.font.render("CONGRATULATIONS!", True, WHITE)
        text_rect = congrats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(congrats_text, text_rect)
        
        # Stats
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, WHITE)
        moves_rect = moves_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(moves_text, moves_rect)
        
        time_text = self.small_font.render(f"Time: {self.get_elapsed_time()} seconds", True, WHITE)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(time_text, time_rect)
        
        difficulty_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        difficulty_rect = difficulty_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # New game button
        self.new_game_button.draw(self.screen)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PuzzleGame()
    game.run()