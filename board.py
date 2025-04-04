import numpy as np

# Constants
ROWS, COLS = 6, 7
SQ_SIZE = 100
RADIUS = SQ_SIZE // 2 - 5
WIDTH, HEIGHT = COLS * SQ_SIZE, (ROWS + 1) * SQ_SIZE
BLUE, BLACK, RED, YELLOW, GRAY = (0, 102, 204), (0, 0, 0), (200, 0, 0), (255, 215, 0), (170, 170, 170)
MINIMAX_DEPTH = 5
AI_TURN = 2
PLAYER_TURN = 1

class Board:
    def __init__(self):
        """Initialize the board with all zeroes (empty cells)."""
        self.board = np.zeros((ROWS, COLS), dtype=int)

    def is_available_column(self, col):
        return self.board[0][col] == 0

    def get_available_row(self, col):
        for row in reversed(range(ROWS)):
            if self.board[row][col] == 0:
                return row
        return None

    def place_piece(self, row, col, player):
        self.board[row][col] = player
    
    def has_won(self, player):
        return (
            self.check_horizontal(player) or
            self.check_vertical(player) or
            self.check_diagonal_positive(player) or
            self.check_diagonal_negative(player)
    )

    def check_horizontal(self, player):
        return self.check_direction(player, 0, 1)

    def check_vertical(self, player):
        return self.check_direction(player, 1, 0)

    def check_diagonal_positive(self, player):
        return self.check_direction(player, 1, 1)

    def check_diagonal_negative(self, player):
        return self.check_direction(player, -1, 1)

    def check_direction(self, player, row_step, col_step):
        """Check if the player has four consecutive pieces in a given direction."""
        for r in range(ROWS):
            for c in range(COLS):
                if all(
                    0 <= r + i * row_step < ROWS and
                    0 <= c + i * col_step < COLS and
                    self.board[r + i * row_step][c + i * col_step] == player
                    for i in range(4)
                ):
                    return True
        return False

    def is_draw(self):
        for c in range(COLS):
            if self.is_available_column(c):
                return False
        return True

    def find_available_columns(self):
        available_columns = [col for col in range(COLS) if self.is_available_column(col)]
        return available_columns
    
    def copy(self):
        new_board = Board()
        new_board.board = self.board.copy()
        return new_board
    
    def is_game_over(self, game_board):
        if game_board.has_won(PLAYER_TURN) or game_board.has_won(AI_TURN):
            return True
        return len(game_board.find_available_columns()) == 0
    
    def print_board(self):
        for row in self.board:
            print(" ".join([str(val) for val in row]))
        print() 
