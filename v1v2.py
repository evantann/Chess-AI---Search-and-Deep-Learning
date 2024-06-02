import pygame
import os
import chess
import random
from aiv1 import Min as aiv1_Min, Max as aiv1_Max, evaluate_board as aiv1_evaluate_board, gen_children as aiv1_gen_children
from aiv2 import minimax as aiv2_minimax, evaluate_board as aiv2_evaluate_board, piece_square_table as aiv2_piece_square_table, MAX as aiv2_MAX, MIN as aiv2_MIN

# Performance metrics
ai1_wins = 0
ai2_wins = 0
draws = 0
games_played = 0
max_games = 10  # Set the number of games to play

# Define the Piece class
class Piece(pygame.sprite.Sprite):
    def __init__(self, filename, cols, rows):
        pygame.sprite.Sprite.__init__(self)
        self.pieces = {chess.Piece(pt, c): i for i, (c, pt) in enumerate([(c, pt) for c in (chess.WHITE, chess.BLACK) for pt in (chess.KING, chess.QUEEN, chess.BISHOP, chess.KNIGHT, chess.ROOK, chess.PAWN)])}
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.cell_width = self.spritesheet.get_width() // cols
        self.cell_height = self.spritesheet.get_height() // rows
        self.cells = [(i % cols * self.cell_width, i // cols * self.cell_height, self.cell_width, self.cell_height) for i in range(cols * rows)]

    def draw(self, surface, piece, coords):
        if piece in self.pieces:
            surface.blit(self.spritesheet, coords, self.cells[self.pieces[piece]])

# Helper functions
def coords_to_square(x, y):
    return chess.square(x, 7 - y)

def square_to_coords(square):
    return chess.square_file(square), 7 - chess.square_rank(square)

# Drawing functions
def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

def draw_pieces_on_board():
    for row in range(8):
        for col in range(8):
            square = coords_to_square(col, row)
            piece = board.piece_at(square)
            if piece:
                chess_pieces.draw(screen, piece, (col * square_size + (square_size - chess_pieces.cell_width) // 2, row * square_size + (square_size - chess_pieces.cell_height) // 2))

def show_menu():
    global running, ai1_color, board
    font = pygame.font.Font(None, 36)
    menu_text = ["Choose who goes first", "1. AI 1 (White)", "2. AI 2 (White)"]
    while True:
        screen.fill((0, 0, 0))
        for i, line in enumerate(menu_text):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (screen_size // 2 - text.get_width() // 2, screen_size // 2 - text.get_height() // 2 + i * 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    ai1_color = chess.WHITE
                    return
                elif event.key == pygame.K_2:
                    ai1_color = chess.BLACK
                    return

# Initialize Pygame
pygame.init()

# Set up the display
screen_size = 800
square_size = screen_size // 8
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Chess Board")

# Load the chess pieces
filename = os.path.join('res', 'pieces.png')
chess_pieces = Piece(filename, 6, 2)

# Define chess.com-like green colors
DARK_GREEN = (118, 150, 86)
LIGHT_GREEN = (238, 238, 210)

board = chess.Board()
running = True
max_depth = 4
fps = 60
clock = pygame.time.Clock()

# Show the menu to choose who goes first
ai1_color = None
show_menu()

# Game loop
while running and games_played < max_games:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    draw_pieces_on_board()

    pygame.display.flip()

    if board.turn == ai1_color:  # AI 1's turn
        if ai1_color == chess.WHITE:
            res = aiv1_Max(board, 0, -9999, 9999, max_depth)  # Depth is adjustable
        else:
            res = aiv1_Min(board, 0, -9999, 9999, max_depth)  # Depth is adjustable
        ai_move = res[1]
        if ai_move:
            board.push(ai_move)
            print(f"AI 1 {ai_move.uci()}")
        else:
            print("No valid AI 1 move found!")
    else:  # AI 2's turn
        legal_moves = list(board.legal_moves)
        _, ai_move = aiv2_minimax(max_depth, board.turn == chess.WHITE, aiv2_MIN, aiv2_MAX, board)
        if ai_move:
            board.push(ai_move)
            print(f"AI 2 {ai_move.uci()}")
        else:
            ai_move = random.choice(legal_moves)
            board.push(ai_move)
            print(f"AI (random) {ai_move.uci()}")

    if board.is_game_over():
        result = board.result()
        games_played += 1
        if result == '1-0':
            if ai1_color == chess.WHITE:
                print("AI 1 (White) won")
                ai1_wins += 1
            else:
                print("AI 2 (White) won")
                ai2_wins += 1
        elif result == '0-1':
            if ai1_color == chess.BLACK:
                print("AI 1 (Black) won")
                ai1_wins += 1
            else:
                print("AI 2 (Black) won")
                ai2_wins += 1
        else:
            print("The game was a draw")
            draws += 1
        
        board.reset()

        if games_played >= max_games:
            running = False

    clock.tick(fps)

pygame.quit()

# Print performance metrics
print(f"Games played: {games_played}")
print(f"AI 1 Wins: {ai1_wins}")
print(f"AI 2 Wins: {ai2_wins}")
print(f"Draws: {draws}")
