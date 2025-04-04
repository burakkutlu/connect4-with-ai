import math
from board import *

class Minimax:
    def __init__(self, game_board, depth=MINIMAX_DEPTH):
        """Initialize the Minimax AI with a given game board and depth."""
        self.depth = depth
        self.game_board = game_board  
    
    def assess_window(self, window, player):
        """Assess a window (4 consecutive pieces) for the player."""
        score = 0
        opp_player = AI_TURN if player == PLAYER_TURN else PLAYER_TURN

        player_piece_count = window.count(player)
        opponent_piece_count = window.count(opp_player)
        empty_piece_count = window.count(0)

        if player_piece_count == 4:
            score += 1000
        elif player_piece_count == 3 and empty_piece_count == 1:
            score += 10
        elif player_piece_count == 2 and empty_piece_count == 2:
            score += 3
        if opponent_piece_count == 3 and empty_piece_count == 1:
            score -= 8
        elif opponent_piece_count == 2 and empty_piece_count == 2:
            score -= 2

        return score
    
    def double_the_score_for_center(self, game_board, player, score):
        """Double the score if any piece in the column is in the center column."""
        center_col = COLS // 2

        for row in range(ROWS):
            if game_board[row][center_col] == player:
                score += 5  
        return score

    def score_position(self, game_board, player):
        """Score the current board position for the given player."""
        score = 0
        score = self.double_the_score_for_center(game_board, player, score)
        for row in range(ROWS):
            row_array = list(game_board[row, :])
            for col in range(COLS - 3):
                score += self.assess_window(row_array[col:col+4], player)

        for col in range(COLS):
            col_array = list(game_board[:, col])
            for row in range(ROWS - 3):
                score += self.assess_window(col_array[row:row+4], player)

        for row in range(3,ROWS):
            for col in range(COLS - 3):
                diagonal_window = [game_board[row-i][col+i] for i in range(4)]
                score += self.assess_window(diagonal_window, player)

        for row in range(3,ROWS):
            for col in range(3,COLS):
                diagonal_window = [game_board[row-i][col-i] for i in range(4)]
                score += self.assess_window(diagonal_window, player)
        return score
    
    def simulate_move(self, game_board, col, player):
        row = game_board.get_available_row(col)
        temp_board = game_board.copy()
        temp_board.place_piece(row, col, player)
        return temp_board

    def minimax(self, game_board, depth, is_max, alpha, beta):
        #game_board.print_board()
        game_over = game_board.is_game_over(game_board)
        if depth == 0 or game_over:
            if game_over:
                if game_board.has_won(AI_TURN):  # AI wins
                    return (None, 1000000)
                elif game_board.has_won(PLAYER_TURN):  # Human wins
                    return (None, -1000000)
                else:  # Draw
                    return (None, 0)
            else:
                return (None, self.score_position(game_board.board, AI_TURN))

        valid_columns = game_board.find_available_columns()      
        best_col = valid_columns[0]
        if is_max:
            value = -math.inf
            for col in valid_columns:
                temp_board = self.simulate_move(game_board, col, AI_TURN)
                new_score = self.minimax(temp_board, depth - 1, False, alpha, beta)[1]
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(value, alpha)
                if alpha >= beta:
                    break
            return best_col, value
        else:
            value = math.inf
            for col in valid_columns:
                temp_board = self.simulate_move(game_board, col, PLAYER_TURN)
                new_score = self.minimax(temp_board, depth - 1, True, alpha, beta)[1]
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(value, beta) 
                if alpha >= beta:
                    break
            return best_col, value

    def get_move(self, game_board):
        """Return the best column for AI to play."""
        col, _ = self.minimax(game_board, self.depth, True, -math.inf, math.inf)
        return col  
  