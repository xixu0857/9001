import pygame
import sys


# 配置常量
BOARD_SIZE    = 15                    # 棋盘行列数
GRID_SIZE     = 40                    # 每格大小（像素）
MARGIN        = 20                    # 边缘留白（像素）
WINDOW_SIZE   = BOARD_SIZE * GRID_SIZE + 2 * MARGIN

# 颜色定义
BACKGROUND_COLOR = (249, 214, 91)     # 棋盘背景色
LINE_COLOR       = (0, 0, 0)          # 网格线颜色
BLACK            = (0, 0, 0)          # 黑子颜色
WHITE            = (255, 255, 255)    # 白子颜色

class GobangGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Gobang (五子棋)")
        self.board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'B'  # 'B'=黑棋, 'W'=白棋
        self.moves = []            # 落子记录，用于撤销

    def draw_board(self):
        """绘制棋盘和所有棋子"""
        self.screen.fill(BACKGROUND_COLOR)
        # 画网格
        for i in range(BOARD_SIZE):
            pos = MARGIN + i * GRID_SIZE
            pygame.draw.line(self.screen, LINE_COLOR,
                             (MARGIN, pos), (WINDOW_SIZE - MARGIN, pos))
            pygame.draw.line(self.screen, LINE_COLOR,
                             (pos, MARGIN), (pos, WINDOW_SIZE - MARGIN))
        # 画棋子
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] != '.':
                    color = BLACK if self.board[y][x] == 'B' else WHITE
                    center = (MARGIN + x * GRID_SIZE, MARGIN + y * GRID_SIZE)
                    pygame.draw.circle(self.screen, color, center,
                                       GRID_SIZE // 2 - 2)
        pygame.display.flip()

    def get_board_pos(self, mouse_pos):
        """将鼠标坐标转换为棋盘格索引"""
        mx, my = mouse_pos
        if not (MARGIN - GRID_SIZE/2 <= mx <= WINDOW_SIZE - MARGIN + GRID_SIZE/2):
            return None
        if not (MARGIN - GRID_SIZE/2 <= my <= WINDOW_SIZE - MARGIN + GRID_SIZE/2):
            return None
        x = round((mx - MARGIN) / GRID_SIZE)
        y = round((my - MARGIN) / GRID_SIZE)
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return x, y
        return None

    def place_piece(self, x, y):
        """在 (x,y) 落子"""
        if self.board[y][x] == '.':
            self.board[y][x] = self.current_player
            self.moves.append((x, y))
            return True
        return False

    def switch_player(self):
        """切换执棋方"""
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def undo(self):
        """撤销上一步"""
        if self.moves:
            x, y = self.moves.pop()
            self.board[y][x] = '.'
            self.switch_player()

    def restart(self):
        """重开新局"""
        self.board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.moves.clear()
        self.current_player = 'B'

    def check_win(self, x, y):
        """判断最近落子 (x,y) 是否成五子连珠"""
        def count_dir(dx, dy):
            cnt = 1
            for d in (1, -1):
                nx, ny = x + d*dx, y + d*dy
                while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE \
                      and self.board[ny][nx] == self.current_player:
                    cnt += 1
                    nx += d*dx
                    ny += d*dy
            return cnt

        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            if count_dir(dx, dy) >= 5:
                return True
        return False

    def run(self):
        """游戏主循环：处理事件并渲染"""
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = self.get_board_pos(event.pos)
                    if pos and self.place_piece(*pos):
                        if self.check_win(*pos):
                            print(f"玩家 {self.current_player} 获胜！")
                            running = False
                        else:
                            self.switch_player()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:  # U：撤销
                        self.undo()
                    elif event.key == pygame.K_r:  # R：重开
                        self.restart()
                    elif event.key == pygame.K_q:  # Q：退出
                        running = False

            clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GobangGame()
    game.run()
