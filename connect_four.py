import pygame
import sys
import time
from board import *
from minimax import Minimax
from greedy import GreedyAI
from iterative_deepening import IterativeDeepeningAI
from mcts import MonteCarloTreeSearch 

class Connect4:
    def __init__(self, ai_algorithm):
        """Initialize the game, set up Pygame, and create the game board."""
        pygame.init()
        self.screen = None
        self.font = pygame.font.Font(None, 40)
        self.board = Board()  # Use Board class
        self.current_player = PLAYER_TURN
        self.game_over = False
        self.history = []
        self.ai = ai_algorithm(self.board)  # Use the provided AI algorithm
        
    def create_screen(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")
        self.draw_board()
    
    def draw_board(self, highlight_col=None):
        """Draw the entire game board on the screen."""
        if not self.screen:
            return
        self.screen.fill(BLACK)
        for c in range(COLS):
            for r in range(ROWS):
                color = BLUE if c != highlight_col else GRAY
                x, y = c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE + SQ_SIZE // 2
                pygame.draw.rect(self.screen, color, (c * SQ_SIZE, r * SQ_SIZE + SQ_SIZE, SQ_SIZE, SQ_SIZE), border_radius=10)
                pygame.draw.circle(self.screen, BLACK, (x, y), RADIUS)
                piece = self.board.board[r][c]
                if piece != 0:
                    pygame.draw.circle(self.screen, RED if piece == PLAYER_TURN else YELLOW, (x, y), RADIUS)
        pygame.display.update()
    
    def make_move(self, col):
        row = self.board.get_available_row(col)
        if row is not None:
            self.board.place_piece(row, col, self.current_player)
            self.history.append((row, col))
            self.animate_drop(col, row, self.current_player)
            self.draw_board()
            if self.board.has_won(self.current_player):
                winner_text = "Player Wins!" if self.current_player == PLAYER_TURN else "AI Wins!"
                self.show_message(winner_text, RED if self.current_player == PLAYER_TURN else YELLOW)
                self.game_over = True
            elif self.board.is_draw():
                self.show_message("It's a Draw!", GRAY)
                self.game_over = True
            else:
                self.current_player = 3 - self.current_player

    def show_message(self, text, color):
        label = self.font.render(text, True, color)
        self.screen.fill(BLACK, (0, 0, WIDTH, SQ_SIZE))
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, SQ_SIZE // 4))
        pygame.display.update()

    def play(self):
        self.create_screen()
        self.restart_game()
        self.draw_board()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and self.game_over and event.key == pygame.K_r:
                    self.restart_game()
                    self.draw_board()

                if event.type == pygame.MOUSEMOTION and not self.game_over:
                    col = event.pos[0] // SQ_SIZE
                    self.draw_board(highlight_col=col)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    col = event.pos[0] // SQ_SIZE
                    if 0 <= col < COLS:
                        if self.current_player == PLAYER_TURN:
                            self.make_move(col)
                            
            if self.current_player == AI_TURN and not self.game_over:
                col = self.ai.get_move(self.board)
                if col is not None:
                    self.make_move(col)

    def restart_game(self):
        self.board = Board()
        self.current_player = PLAYER_TURN
        self.game_over = False
        self.history = []

    def animate_drop(self, col, final_row, player):
        for temp_row in range(ROWS-1, ROWS-final_row, -1):
            self.draw_board()
            pygame.draw.circle(self.screen, RED if player == 1 else YELLOW,
                            (col * SQ_SIZE + SQ_SIZE // 2, HEIGHT - (temp_row + 1) * SQ_SIZE + SQ_SIZE // 2), RADIUS)
            pygame.display.update()
            time.sleep(0.05)

if __name__ == "__main__":
    Connect4(Minimax).play()
    #Connect4(GreedyAI).play()
    #Connect4(IterativeDeepeningAI).play()
    #Connect4(MonteCarloTreeSearch).play()
