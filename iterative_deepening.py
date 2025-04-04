import math
from board import *

class IterativeDeepeningAI:
    def __init__(self, game_board, max_depth=7):
        self.game_board = game_board
        self.max_depth = max_depth  # Maximum depth for search

    def get_move(self, game_board):
        """Perform Iterative Deepening DFS to find the best move."""
        self.game_board = game_board
        best_move = None

        # Check for forced moves (win or block)
        forced_move = self.check_for_forced_move()
        if forced_move is not None:
            return forced_move  # Return immediately if there's a forced move (win or block)

        # If no forced moves, proceed with iterative deepening search
        depth = 1
        while depth <= self.max_depth:
            move = self.depth_limited_search(depth, True, -math.inf, math.inf)
            if move is not None:
                best_move = move
            depth += 1

        return best_move


    def check_for_forced_move(self):
        """Check for forced winning or blocking moves."""
        valid_moves = self.game_board.find_available_columns()

        for move in valid_moves:
            temp_board = self.game_board.copy()
            row = temp_board.get_available_row(move)

            # Check if AI can win with this move
            temp_board.place_piece(row, move, AI_TURN)
            if temp_board.has_won(AI_TURN):
                return move  # AI wins, return this move

            # Check if the player can win with this move and block it
            temp_board = self.game_board.copy()
            temp_board.place_piece(row, move, PLAYER_TURN)
            if temp_board.has_won(PLAYER_TURN):
                return move  # Block the player's winning move

        return None


    def depth_limited_search(self, depth, is_max_player, alpha, beta):
        """Perform Depth-First Search with depth limit and Alpha-Beta Pruning."""
        valid_moves = self.order_moves(self.game_board.find_available_columns())
        best_move = None

        if is_max_player:
            max_score = float('-inf')
            for col in valid_moves:
                temp_board = self.game_board.copy()
                row = temp_board.get_available_row(col)
                temp_board.place_piece(row, col, AI_TURN)

                current_score = self.minimax(temp_board, depth - 1, False, alpha, beta)

                if current_score > max_score:
                    max_score = current_score
                    best_move = col
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break  # Alpha cut-off

            return best_move
        else:
            min_score = float('inf')
            for col in valid_moves:
                temp_board = self.game_board.copy()
                row = temp_board.get_available_row(col)
                temp_board.place_piece(row, col, PLAYER_TURN)

                current_score = self.minimax(temp_board, depth - 1, True, alpha, beta)

                if current_score < min_score:
                    min_score = current_score
                    best_move = col
                beta = min(beta, min_score)
                if beta <= alpha:
                    break  # Beta cut-off

            return best_move

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax with Alpha-Beta Pruning for DFS search."""
        if depth == 0 or board.is_game_over(board):
            return self.evaluate_board(board)

        valid_moves = board.find_available_columns()

        if is_maximizing:
            max_eval = float('-inf')
            for col in valid_moves:
                temp_board = board.copy()
                row = temp_board.get_available_row(col)
                temp_board.place_piece(row, col, AI_TURN)
                eval = self.minimax(temp_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                temp_board = board.copy()
                row = temp_board.get_available_row(col)
                temp_board.place_piece(row, col, PLAYER_TURN)
                eval = self.minimax(temp_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return min_eval

    def evaluate_board(self, board):
        """Evaluate board position for AI."""
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                if board.board[row][col] == AI_TURN:
                    score += self.evaluate_position(board, row, col, AI_TURN)
                elif board.board[row][col] == PLAYER_TURN:
                    score -= self.evaluate_position(board, row, col, PLAYER_TURN)
        return score

    def evaluate_position(self, board, row, col, player):
        """Evaluate a position for potential connections and immediate threats."""
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Vertical, horizontal, diagonal

        for dr, dc in directions:
            consecutive = 0
            open_ends = 0
            empty_positions = []  # Track empty positions for blocking

            for i in range(4):  # Check for a window of 4 cells (for 4-in-a-row)
                r, c = row + i * dr, col + i * dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board.board[r][c] == player:
                        consecutive += 1
                    elif board.board[r][c] == 0:
                        open_ends += 1
                        empty_positions.append((r, c))  # Store empty positions

            # Detect threat: 2 pieces and 2 empty spaces (potential win for the opponent)
            if consecutive == 2 and open_ends == 2:
                # Block the opponent's threat by playing in one of the empty positions
                if player == PLAYER_TURN:  # If it's the opponent's turn
                    return empty_positions[0][1]  # Return column to block opponent

            # Score for AI's potential moves (if needed, for evaluation later)
            if consecutive == 2 and open_ends > 1:
                if player == PLAYER_TURN:
                    return -1000000  # Penalize AI for not blocking opponent's 2-in-a-row
                else:
                    score += 5000  # Reward AI for making the move

        return score  # Return score for AI's own position (default case)


    def order_moves(self, available_moves):
        """Sort moves to prioritize blocking moves first, then winning moves."""
        move_scores = {}

        for move in available_moves:
            temp_board = self.game_board.copy()
            row = temp_board.get_available_row(move)

            # Winning move
            temp_board.place_piece(row, move, AI_TURN)
            if temp_board.has_won(AI_TURN):
                return [move]  # Play immediately if it's a winning move

            # Blocking move
            temp_board = self.game_board.copy()
            temp_board.place_piece(row, move, PLAYER_TURN)
            if temp_board.has_won(PLAYER_TURN):
                return [move]  # Block immediately if the player would win

            # Assign a default score 
            move_scores[move] = 0

        # Apply custom column order (if no immediate win or block)
        custom_order = [3, 2, 4, 1, 5, 0, 6]
        ordered_moves = [move for move in custom_order if move in available_moves]

        return ordered_moves
