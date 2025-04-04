import time
import random
import math
from board import *

class MCTSNode:
    def __init__(self, board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

    def is_fully_expanded(self):
        """Check if all possible moves have been explored"""
        available_moves = self.board.find_available_columns()
        tried_moves = {child.move for child in self.children}
        return all(move in tried_moves for move in available_moves)


    def best_child(self, exploration_weight=1.41):
        """Select the child node with the best UCT score"""
        return max(self.children, key=lambda child: child.uct_score(exploration_weight))

    def uct_score(self, exploration_weight=1.41):
        """Calculate Upper Confidence Bound (UCT) score"""
        if self.visits == 0:
            return float('inf')  # Encourage exploration of unvisited nodes
        return (self.wins / self.visits) + exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)

class MonteCarloTreeSearch:
    def __init__(self, game_board, iterations=1000, time_limit=2, exploration_weight=1.0):
        self.game_board = game_board
        self.iterations = iterations
        self.time_limit = time_limit
        self.exploration_weight = exploration_weight

    def get_move(self, game_board):
        self.game_board = game_board
        return self.search()

    def search(self):
        root = MCTSNode(self.game_board.copy())
        start_time = time.time()

        for _ in range(self.iterations):
            if time.time() - start_time > self.time_limit:
                break
            self.simulate(root)

        return root.best_child(exploration_weight=0).move  # Greedy selection at the end

    def simulate(self, node):
        selected_node = self.selection(node)
        result = self.rollout(selected_node)
        self.backpropagate(selected_node, result)

    def selection(self, node):
        while node.is_fully_expanded() and node.children:
            unvisited = [child for child in node.children if child.visits == 0]
            if unvisited:
                return random.choice(unvisited)
            node = node.best_child(exploration_weight=self.exploration_weight)
        return self.expand(node)

    def expand(self, node):
        untried_moves = [m for m in node.board.find_available_columns() if m not in [child.move for child in node.children]]
        if untried_moves:
            move = random.choice(untried_moves)
            new_board = node.board.copy()
            row = new_board.get_available_row(move)
            new_board.place_piece(row, move, AI_TURN)
            child_node = MCTSNode(new_board, move, node)
            node.children.append(child_node)
            return child_node
        return node

    def rollout(self, node):
        temp_board = node.board.copy()
        current_turn = PLAYER_TURN

        while not temp_board.is_draw() and not temp_board.has_won(AI_TURN) and not temp_board.has_won(PLAYER_TURN):
            available_moves = temp_board.find_available_columns()

            # First, play a winning move if possible
            for move in available_moves:
                temp_board_copy = temp_board.copy()
                row = temp_board_copy.get_available_row(move)
                temp_board_copy.place_piece(row, move, current_turn)
                if temp_board_copy.has_won(current_turn):
                    move_to_play = move
                    break
            else:
                # Then, block opponent's win
                for move in available_moves:
                    temp_board_copy = temp_board.copy()
                    row = temp_board_copy.get_available_row(move)
                    temp_board_copy.place_piece(row, move, PLAYER_TURN)
                    if temp_board_copy.has_won(PLAYER_TURN):
                        move_to_play = move
                        break
                else:
                    move_to_play = random.choice(available_moves)  # Otherwise, play randomly

            row = temp_board.get_available_row(move_to_play)
            temp_board.place_piece(row, move_to_play, current_turn)
            current_turn = AI_TURN if current_turn == PLAYER_TURN else PLAYER_TURN

        if temp_board.has_won(AI_TURN):
            return 1
        elif temp_board.has_won(PLAYER_TURN):
            return -1  
        return 0  # Draw

    def backpropagate(self, node, result):
        """Update node statistics and penalize bad losses more."""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
