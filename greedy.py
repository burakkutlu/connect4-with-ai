import random
from board import *

class GreedyAI:
    def __init__(self, game_board):
        """Greedy AI selects the best immediate move."""
        self.game_board = game_board  
    
    def play_greedy(self):
        """Greedy AI chooses the move with the highest score."""
        moves = {}
        for col in range(COLS):
            if self.game_board.is_available_column(col):
                row = self.game_board.get_available_row(col)
                value = 0
                value += self.adjacent_near_move(row, col, AI_TURN)
                value += self.self_win(row, col, AI_TURN)
                value += self.block_opponent(row, col, PLAYER_TURN)
                moves[col] = value
        
        return max(moves, key=moves.get) if moves else random.choice(range(COLS))

    def adjacent_near_move(self, row, col, player):
        """Count how many of the player's pieces are adjacent in all directions."""
        adjacent_count = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            count = 0
            r, c = row, col
            while 0 <= r + dr < ROWS and 0 <= c + dc < COLS and self.game_board.board[r + dr][c + dc] == player:
                count += 1
                r += dr
                c += dc
            adjacent_count += count ** 2  # Exponential weighting to favor longer chains
        
        return adjacent_count
    
    def self_win(self, row, col, player):
        """Check if playing this move results in a win."""
        temp_board = self.game_board.copy()
        temp_board.place_piece(row, col, player)
        return 10000 if temp_board.has_won(player) else 0
    
    def block_opponent(self, row, col, opponent):
        """Check if placing here prevents an opponent's win."""
        temp_board = self.game_board.copy()
        temp_board.place_piece(row, col, opponent)
        return 5000 if temp_board.has_won(opponent) else 0

    def get_move(self, game_board):  
        """Get the best move by calling play_greedy()."""
        self.game_board = game_board  # Update the game board reference
        return self.play_greedy()
