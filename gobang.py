import os
import pygame
import sys
import random

# ————————————————
# Gobang (Five-in-a-Row) Pygame Complete Version
# Supports: Human vs. Human or Human vs. AI, Undo, Restart
# ————————————————

# If you need to run in a headless environment (no display), uncomment these lines:
# os.environ["SDL_VIDEODRIVER"] = "dummy"
# os.environ["SDL_AUDIODRIVER"] = "dummy"

# Board configuration
BOARD_SIZE  = 15                     # number of rows and columns
GRID_SIZE   = 40                     # pixel size of each grid cell
MARGIN      = 20                     # margin around the board (pixels)
WINDOW_SIZE = BOARD_SIZE * GRID_SIZE + 2 * MARGIN

# Colors (R, G, B)
BACKGROUND_COLOR = (249, 214, 91)    # board background color
LINE_COLOR       = (0, 0, 0)         # grid line color
BLACK            = (0, 0, 0)         # black stone color
WHITE            = (255, 255, 255)   # white stone color
TEXT_COLOR       = (80, 80, 80)      # status text color

# Game modes
MODE_HUMAN = 1
MODE_AI    = 2


class GobangGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Create game window, extra 50px for status bar
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 50))
        pygame.display.set_caption("Gobang (Five-in-a-Row)")
        self.font = pygame.font.SysFont(None, 24)
        self.restart()

    def restart(self):
        """Reset the board and state to start a new game."""
        self.board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.moves = []              # move history for undo
        self.current_player = 'B'    # 'B' = black, 'W' = white
        self.mode = None             # game mode not yet selected

    def draw_board(self):
        """Draw the grid, stones, and status text."""
        self.screen.fill(BACKGROUND_COLOR)

        # Draw grid lines
        for i in range(BOARD_SIZE):
            pos = MARGIN + i * GRID_SIZE
            pygame.draw.line(self.screen, LINE_COLOR,
                             (MARGIN, pos), (WINDOW_SIZE - MARGIN, pos))
            pygame.draw.line(self.screen, LINE_COLOR,
                             (pos, MARGIN), (pos, WINDOW_SIZE - MARGIN))

        # Draw stones
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] != '.':
                    color = BLACK if self.board[y][x] == 'B' else WHITE
                    center = (MARGIN + x * GRID_SIZE, MARGIN + y * GRID_SIZE)
                    pygame.draw.circle(self.screen, color, center,
                                       GRID_SIZE // 2 - 2)

        # Draw status bar
        if self.mode is None:
            msg = "Press 1 = Human vs. Human   2 = Human vs. AI"
        else:
            current = "Black (B)" if self.current_player == 'B' else "White (W)"
            mode_str = "Human-Human" if self.mode == MODE_HUMAN else "Human-AI"
            msg = f"Mode: {mode_str}   Turn: {current}   U=Undo  R=Restart  Q=Quit"
        text_surf = self.font.render(msg, True, TEXT_COLOR)
        self.screen.blit(text_surf, (MARGIN, WINDOW_SIZE + 15))

        pygame.display.flip()

    def get_board_pos(self, mouse_pos):
        """Convert pixel coordinates to board grid (x, y)."""
        mx, my = mouse_pos
        # Check if click is inside the playable board area
        if not (MARGIN - GRID_SIZE/2 <= mx <= WINDOW_SIZE - MARGIN + GRID_SIZE/2):
            return None
        if not (MARGIN - GRID_SIZE/2 <= my <= WINDOW_SIZE - MARGIN + GRID_SIZE/2):
            return None
        # Compute grid indices
        x = round((mx - MARGIN) / GRID_SIZE)
        y = round((my - MARGIN) / GRID_SIZE)
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return x, y
        return None

    def place_piece(self, x, y):
        """Place a stone at (x, y) if empty. Return True on success."""
        if self.board[y][x] == '.':
            self.board[y][x] = self.current_player
            self.moves.append((x, y, self.current_player))
            return True
        return False

    def switch_player(self):
        """Switch turn between black and white."""
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def undo(self):
        """Undo the last move(s). In AI mode, undo two moves at once."""
        if not self.moves:
            return
        if self.mode == MODE_AI and len(self.moves) >= 2:
            # Remove both player and AI last moves
            for _ in range(2):
                x, y, p = self.moves.pop()
                self.board[y][x] = '.'
            self.current_player = 'B'
        else:
            x, y, p = self.moves.pop()
            self.board[y][x] = '.'
            self.current_player = p

    def ai_move(self):
        """AI picks a random empty cell to play."""
        empties = [(x, y) for y in range(BOARD_SIZE)
                         for x in range(BOARD_SIZE) if self.board[y][x] == '.']
        if empties:
            x, y = random.choice(empties)
            self.place_piece(x, y)

    def check_win(self, x, y):
        """Check if the last move at (x, y) created a five-in-a-row."""
        def count_dir(dx, dy):
            count = 1
            for d in (1, -1):
                nx, ny = x + d*dx, y + d*dy
                while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE \
                      and self.board[ny][nx] == self.current_player:
                    count += 1
                    nx += d*dx
                    ny += d*dy
            return count

        # Check horizontal, vertical, and two diagonals
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if count_dir(dx, dy) >= 5:
                return True
        return False

    def run(self):
        """Main game loop: handle events and update display."""
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Mode selection before game starts
                    if self.mode is None:
                        if event.key == pygame.K_1:
                            self.mode = MODE_HUMAN
                        elif event.key == pygame.K_2:
                            self.mode = MODE_AI
                    else:
                        # In-game controls
                        if event.key == pygame.K_u:
                            self.undo()
                        elif event.key == pygame.K_r:
                            self.restart()
                        elif event.key == pygame.K_q:
                            running = False

                elif (event.type == pygame.MOUSEBUTTONDOWN and
                      event.button == 1 and self.mode is not None):
                    pos = self.get_board_pos(event.pos)
                    if pos and self.place_piece(*pos):
                        # Check player win
                        if self.check_win(*pos):
                            print(f"Player {self.current_player} wins!")
                            running = False
                            break
                        self.switch_player()
                        # If AI mode and it's AI's turn, let AI play
                        if self.mode == MODE_AI and self.current_player == 'W':
                            self.ai_move()
                            last_x, last_y, _ = self.moves[-1]
                            if self.check_win(last_x, last_y):
                                print("AI (White) wins!")
                                running = False
                                break
                            self.switch_player()

            clock.tick(30)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GobangGame()
    game.run()
