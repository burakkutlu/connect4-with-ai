import pygame
import sys
import time
from board import *
from minimax import Minimax
from greedy import GreedyAI
from iterative_deepening import IterativeDeepeningAI
from mcts import MonteCarloTreeSearch 

class Connect4:
    def __init__(self):
        """Initialize the game, set up Pygame, and create the game board."""
        pygame.init()
        self.screen = None
        self.font = pygame.font.Font(None, 40)
        self.board = Board()  # Use Board class
        self.current_player = PLAYER_TURN
        self.game_over = False
        self.history = []
        
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

    # play function to play with player vs ai
    def play(self, ai_class):
        self.create_screen()
        self.restart_game()
        self.draw_board()
        ai = ai_class(self.board)
        

        total_ai_time = 0
        ai_moves = 0
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and self.game_over and event.key == pygame.K_r:
                    self.restart_game()
                    self.draw_board()
                    total_ai_time = 0
                    ai_moves = 0

                if event.type == pygame.MOUSEMOTION and not self.game_over:
                    col = event.pos[0] // SQ_SIZE
                    self.draw_board(highlight_col=col)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    col = event.pos[0] // SQ_SIZE
                    if 0 <= col < COLS:
                        if self.current_player == PLAYER_TURN:
                            self.make_move(col)
                            
            if self.current_player == AI_TURN and not self.game_over:
                start = time.time()
                col = ai.get_move(self.board)
                end = time.time()
                if col is not None:
                    total_ai_time += (end - start)
                    ai_moves += 1
                    self.make_move(col)

            # End of game: show duration
            if self.game_over:
                if ai_moves > 0:
                    avg_time = total_ai_time / ai_moves
                    print(f"AI made {ai_moves} moves.")
                    print(f"Total AI thinking time: {total_ai_time:} seconds")
                    print(f"Average time per move: {avg_time:} seconds")
                else:
                    print("AI made no moves.")
                break


    def play_game(self, ai1_class, ai2_class, rounds):
        """Simulate a series of games between two AIs."""
        results = {'ai1_wins': 0, 'ai2_wins': 0, 'draws': 0}
        timings = {
            'ai1_total_time': 0.0, 'ai1_moves': 0,
            'ai2_total_time': 0.0, 'ai2_moves': 0
        }

        self.create_screen()
        for _ in range(rounds):
            self.restart_game()
            ai1, ai2 = ai1_class(self.board), ai2_class(self.board)
            self.current_player = PLAYER_TURN
            self.draw_board()

            while not self.game_over:
                pygame.event.pump()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                active_player = self.current_player
                # Zaman ölçümü burada olacak
                start_time = time.time()
                self.handle_player_turn(ai1, ai2)
                elapsed = time.time() - start_time

                if active_player == PLAYER_TURN:
                    timings['ai1_total_time'] += elapsed
                    timings['ai1_moves'] += 1
                else:
                    timings['ai2_total_time'] += elapsed
                    timings['ai2_moves'] += 1

            self.update_results(results)
            time.sleep(0.5)

        return results, timings

    def handle_player_turn(self, ai1, ai2):
        """Handle the turn of the current player (either AI or human)."""
        # Check if it's the player's turn or the AI's turn
        if self.current_player == PLAYER_TURN and not self.game_over:
            col = ai1.get_move(self.board)

            if col is not None:
                self.make_move(col)

        # If it's the AI's turn, let the AI make a move
        elif self.current_player == AI_TURN and not self.game_over:
            col = ai2.get_move(self.board)

            if col is not None:
                self.make_move(col)

        time.sleep(0.1)

    def update_results(self, results):
        """Update the results dictionary based on the game outcome."""
        if self.board.has_won(PLAYER_TURN):
            #print(f"first one wins")
            results['ai1_wins'] += 1
        elif self.board.has_won(AI_TURN):
            #print(f"second one wins")
            results['ai2_wins'] += 1
        else:
            #print(f"draw")
            results['draws'] += 1

    def play_ai_vs_ai(self, ai1_class, ai2_class, rounds=1):
        """Run the simulation: play {rounds} games, then swap players and play another {rounds} games."""
        print(f"Playing the first {rounds} games...")
        results, timings = self.play_game(ai1_class, ai2_class, rounds)

        print(f"\nFirst {rounds} games complete:")
        print(f"{ai1_class.__name__} wins: {results['ai1_wins']}")
        print(f"{ai2_class.__name__} wins: {results['ai2_wins']}")
        print(f"Draws: {results['draws']}")

        avg1 = timings['ai1_total_time'] / timings['ai1_moves'] if timings['ai1_moves'] > 0 else 0.0
        avg2 = timings['ai2_total_time'] / timings['ai2_moves'] if timings['ai2_moves'] > 0 else 0.0

        print(f"{ai1_class.__name__} avg move time: {avg1:.4f} sec")
        print(f"{ai2_class.__name__} avg move time: {avg2:.4f} sec")

        print(f"\nSwapping players and playing another {rounds} games...")
        results_swapped, timings_swapped = self.play_game(ai2_class, ai1_class, rounds)

        print(f"\nSecond {rounds} games complete (after swapping players):")
        print(f"{ai2_class.__name__} wins: {results_swapped['ai1_wins']}")
        print(f"{ai1_class.__name__} wins: {results_swapped['ai2_wins']}")
        print(f"Draws: {results_swapped['draws']}")

        avg1_swapped = timings_swapped['ai1_total_time'] / timings_swapped['ai1_moves'] if timings_swapped['ai1_moves'] > 0 else 0.0
        avg2_swapped = timings_swapped['ai2_total_time'] / timings_swapped['ai2_moves'] if timings_swapped['ai2_moves'] > 0 else 0.0

        print(f"{ai2_class.__name__} avg move time (as first player): {avg1_swapped:.4f} sec")
        print(f"{ai1_class.__name__} avg move time (as second player): {avg2_swapped:.4f} sec")

        pygame.quit()

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

    
def simulate_games(ai1_class, ai2_class):
        game = Connect4()
        game.play_ai_vs_ai(ai1_class, ai2_class)

if __name__ == "__main__":

    game = Connect4()
    #game.play(Minimax)
    #game.play(GreedyAI)
    #game.play(MonteCarloTreeSearch)
    #game.play(IterativeDeepeningAI)

    #simulate_games(Minimax, GreedyAI)
    simulate_games(IterativeDeepeningAI, MonteCarloTreeSearch)


    """simulate_games(Minimax, GreedyAI)
    simulate_games(Minimax, MonteCarloTreeSearch)
    simulate_games(Minimax, IterativeDeepeningAI)
    simulate_games(GreedyAI, IterativeDeepeningAI)
    simulate_games(GreedyAI, MonteCarloTreeSearch)
    simulate_games(IterativeDeepeningAI, MonteCarloTreeSearch)"""



