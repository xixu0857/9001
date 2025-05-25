import pygame #Pygame is a Python game development library based on SDL (Simple DirectMedia Layer), which provides basic functions for creating interactive multimedia programs (especially 2D games).
import os
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
board_size  = 15                     # number of rows and columns
grid_size   = 40                     # pixel size of each grid cell
margin      = 20                     # margin around the board (pixels)
window_size = board_size * grid_size + 2 * margin

# Colors (R, G, B)
background_color = (249, 214, 91)    # board background color
line_color       = (0, 0, 0)         # grid line color
letter_color       = (80, 80, 80)      # status text color
black_chese           = (0, 0, 0)         # black stone color
white_chese            = (255, 255, 255)   # white stone color


# Game modes
human_mode = 1
ai_mode    = 2


class GobangGame:
    def __init__(self):
        '''
        Initialize Pygame：This code is the constructor (initialization method) of the GobangGame class. 
        Its function is to complete the basic settings of the Pygame environment and window initialization when creating a game object, 
        and call the restart() method to prepare for a new game.'''
        pygame.init()
        # Create game window, extra 50px for status bar
        self.screen = pygame.display.set_mode((window_size, window_size + 50))
        pygame.display.set_caption("Gobang (Five-in-a-Row)")
        self.font = pygame.font.SysFont(None, 24)
        #Reset the board and state to start a new game
        self.restart()

    def restart(self):
        '''
        Reset the board and state to start a new game. Clear the board, clear the move history,
        reset the current player to black, and set the game mode to unselected, in preparation for a new game.
        '''
        temp_board = []
        for i in range(board_size):
            row = []
            for j in range(board_size):
                row.append('.')
            temp_board.append(row)
        self.board = temp_board #Reset the entire board.

        self.moves = []              # move history for undo
        self.current_player = 'B'    # 'B' = black, 'W' = white  Reset the chess position to Black ('B'), ensuring that Black goes first in every new game.
        self.mode = None             # game mode not yet selected

    def draw_board(self):
        '''Draw the "chessboard" of the game interface, including background fill, stones, status text and grid lines.'''

        self.screen.fill(background_color)
        # Draw grid lines
        for i in range(board_size):
            pos = margin + i * grid_size
            #Draw horizontal lines
            pygame.draw.line(self.screen, line_color,
                             (margin, pos), (window_size - margin, pos))
            #Draw vertical lines
            pygame.draw.line(self.screen, line_color,
                             (pos, margin), (pos, window_size - margin))

        # Draw stones
        for y in range(board_size):
            for x in range(board_size):
                if self.board[y][x] != '.':
                    if self.board[y][x]=='B':
                        color = black_chese
                    else:
                        color = white_chese
                    
                    center = (margin + x * grid_size, margin + y * grid_size)
                    pygame.draw.circle(self.screen, color, center, grid_size // 2 - 2)

        # Draw status bar
        if self.mode is None:
            msg = "Press 1 = Human vs. Human   2 = Human vs. AI"
        else:
            current = "Black (B)" if self.current_player == 'B' else "White (W)"
            mode_str = "Human VS Human" if self.mode == human_mode else "Human(black chess) VS AI"
            msg = f"Mode: {mode_str}   Turn: {current}   u=Undo  r=Restart  q=Quit"
        text_surf = self.font.render(msg, True, letter_color)
        self.screen.blit(text_surf, (margin, window_size + 15))
        #Update the entire screen: All previous drawing operations on various Surfaces (including the background, grid, 
        # chess pieces, text, etc. drawn on self.screen) are presented to the display window at once
        pygame.display.flip()

    def get_board_pos(self, mouse_pos):
        '''
        Convert the pixel coordinates of the mouse click to the grid coordinates (x, y) on the chessboard. 
        If the click is not in the chessboard area, return None
        '''
        mx, my = mouse_pos
        # Check if click is inside the playable board area
        if mx < margin - grid_size/2 or mx > window_size - margin + grid_size/2:
            return None
        if my < margin - grid_size/2 or my > window_size - margin + grid_size/2:
            return None
        # Compute grid indices
        x = round((mx - margin) / grid_size)
        y = round((my - margin) / grid_size)
        if 0 <= x < board_size and 0 <= y < board_size:
            return x, y
        else:
            return None

    def switch_player(self):
        '''Switch current_player turn between black and white.'''
        if self.current_player=='B':
            self.current_player='W'
        else:
            self.current_player='B'

    def place_chess(self, x, y):
        '''
        Try to place a chess piece at the specified board coordinates (x, y), 
        and update the internal state and record if successful, and finally return 
        whether the operation is successful.
        '''
        if self.board[y][x] == '.':
            self.board[y][x] = self.current_player # Change '.' to the current player's marker self.current_player
            self.moves.append((x, y, self.current_player))
            return True # Indicates that the move was successful. The caller can decide whether to switch players or determine the winner based on this.
        return False

    def undo(self):
        '''
        Implemented the "Undo" function: undo the last move in "Human vs. Human" mode, 
        and undo the player's and AI's moves in "Human vs. Machine" mode.
        '''
        # self.moves is a list of all the pieces that have been moved (in the form of (x, y, player))
        if not self.moves:
            return
        # Check if the current mode is "human vs. AI" (self.mode == ai_mode), and if there are at least two moves available. 
        # The reason for two moves is that in "human vs. AI" mode, every time the player makes a move, the AI ​​will also make a move, 
        # and both moves need to be retracted at the same time when retracting.
        if self.mode == ai_mode and len(self.moves) >= 2:
            # Remove both player and AI last moves
            for _ in range(2): # 2: Remove both player and AI last moves
                x, y, player = self.moves.pop()
                self.board[y][x] = '.'
            self.current_player = 'B'
        else:
            x, y, player = self.moves.pop()
            self.board[y][x] = '.'
            self.current_player = player

    def ai_move(self):
        '''AI move strategy - randomly select a position in all spaces to place the chess'''
        empties = []    
        #Find all vacancies                 
        for y in range(board_size):     
            for x in range(board_size):  
                if self.board[y][x] == '.':   
                    empties.append((x, y))  
        if empties:
            x, y = random.choice(empties)
            self.place_chess(x, y)

    def check_win(self, x, y):
        '''
        Determine whether the chess piece just dropped at coordinate (x, y) allows the current player to form a "five in a row", 
        that is, at least 5 chess pieces of the same color are arranged continuously in the horizontal direction, vertical direction or two diagonals.'''
        #
        def count_dir(dx, dy):
            count = 1 #Because we need to take the newly placed chess piece into account, we start from 1.
            for d in (1, -1):
                nx, ny = x + d*dx, y + d*dy
                while 0 <= nx < board_size and 0 <= ny < board_size \
                      and self.board[ny][nx] == self.current_player:
                    count += 1
                    nx += d*dx
                    ny += d*dy
            return count #After searching both sides, count is the total number of consecutive pieces of the same color, including the middle piece and both sides.

        # Call count_dir for all four directions: check horizontal, vertical, and two diagonals
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if count_dir(dx, dy) >= 5:
                return True
        return False
    
    def run(self):
        '''Main game loop: handle events and update display.'''
        clock = pygame.time.Clock() #Used to control the loop speed (frame rate).
        running = True #Is a Boolean variable that controls whether the main loop continues.

        while running:
            self.draw_board()
            for event in pygame.event.get():
                #Listen for the operating system's "close window" request. Once received, set running to False and exit the main loop.
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # General shortcut keys: Note that it is English input method, enter lowercase letters
                    if event.key == pygame.K_u:
                        print("DEBUG: Undo")  
                        self.undo()
                        continue
                    if event.key == pygame.K_r:
                        print("DEBUG: Restart")
                        self.restart()
                        continue
                    if event.key == pygame.K_q:
                        print("DEBUG: Quit")
                        running = False
                        continue

                    # Mode selection: When the game has not started (self.mode is None), press 1 to enter "Human vs. Human" 
                    # and press 2 to enter "Human vs. Machine".
                    if self.mode is None:
                        if event.key == pygame.K_1:
                            print("DEBUG: mode set to HUMAN")
                            self.mode = human_mode
                        elif event.key == pygame.K_2:
                            print("DEBUG: mode set to AI")
                            self.mode = ai_mode
                        continue

                # Handle mouse click events (drop)
                elif (event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1 and self.mode is not None):
                    pos = self.get_board_pos(event.pos)
                    if pos and self.place_chess(*pos):
                        if self.check_win(*pos):
                            print(f"Player {self.current_player} wins!")
                            running = False
                            break
                        self.switch_player()
                        # In human-machine mode, when it is the white chess piece's turn, the AI ​​will automatically make the move
                        if self.mode == ai_mode and self.current_player == 'W':
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
