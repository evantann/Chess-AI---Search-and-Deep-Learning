import pygame
import os
import chess
from stockfish import Stockfish
import random

# Initialize Stockfish engine using the pip-installed stockfish package
stockfish = Stockfish()
stockfish.set_skill_level(3)  # Set the skill level (0 to 20)

# Performance metrics
ai_wins = 0
ai_losses = 0
draws = 0
games_played = 0
max_games = 10  # Set the number of games to play

# Elo calculation parameters
initial_elo = 1200
opponent_elo = 1200  # Assuming Stockfish has a very high rating
K = 32  # K-factor in Elo rating system

MAX, MIN = 10000, -10000  # Use more realistic values for MAX and MIN

# PeSTO evaluation tables
mg_value = [82, 337, 365, 477, 1025, 0]
eg_value = [94, 281, 297, 512, 936, 0]

mg_pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    98, 134, 61, 95, 68, 126, 34, -11,
    -6, 7, 26, 31, 65, 56, 25, -20,
    -14, 13, 6, 21, 23, 12, 17, -23,
    -27, -2, -5, 12, 17, 6, 10, -25,
    -26, -4, -4, -10, 3, 3, 33, -12,
    -35, -1, -20, -23, -15, 24, 38, -22,
    0, 0, 0, 0, 0, 0, 0, 0
]

eg_pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    178, 173, 158, 134, 147, 132, 165, 187,
    94, 100, 85, 67, 56, 53, 82, 84,
    32, 24, 13, 5, -2, 4, 17, 17,
    13, 9, -3, -7, -7, -8, 3, -1,
    4, 7, -6, 1, 0, -5, -1, -8,
    13, 8, 8, 10, 13, 0, 2, -7,
    0, 0, 0, 0, 0, 0, 0, 0
]

mg_knight_table = [
    -167, -89, -34, -49, 61, -97, -15, -107,
    -73, -41, 72, 36, 23, 62, 7, -17,
    -47, 60, 37, 65, 84, 129, 73, 44,
    -9, 17, 19, 53, 37, 69, 18, 22,
    -13, 4, 16, 13, 28, 19, 21, -8,
    -23, -9, 12, 10, 19, 17, 25, -16,
    -29, -53, -12, -3, -1, 18, -14, -19,
    -105, -21, -58, -33, -17, -28, -19, -23
]

eg_knight_table = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25, -8, -25, -2, -9, -25, -24, -52,
    -24, -20, 10, 9, -1, -9, -19, -41,
    -17, 3, 22, 22, 22, 11, 8, -18,
    -18, -6, 16, 25, 16, 17, 4, -18,
    -23, -3, -1, 15, 10, -3, -20, -22,
    -42, -20, -10, -5, -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64
]

mg_bishop_table = [
    -29, 4, -82, -37, -25, -42, 7, -8,
    -26, 16, -18, -13, 30, 59, 18, -47,
    -16, 37, 43, 40, 35, 50, 37, -2,
    -4, 5, 19, 50, 37, 37, 7, -2,
    -6, 13, 13, 26, 34, 12, 10, 4,
    0, 15, 15, 15, 14, 27, 18, 10,
    4, 15, 16, 0, 7, 21, 33, 1,
    -33, -3, -14, -21, -13, -12, -39, -21
]

eg_bishop_table = [
    -14, -21, -11, -8, -7, -9, -17, -24,
    -8, -4, 7, -12, -3, -13, -4, -14,
    2, -8, 0, -1, -2, 6, 0, 4,
    -3, 9, 12, 9, 14, 10, 3, 2,
    -6, 3, 13, 19, 7, 10, -3, -9,
    -12, -3, 8, 10, 13, 3, -7, -15,
    -14, -18, -7, -1, 4, -9, -15, -27,
    -23, -9, -23, -5, -9, -16, -5, -17
]

mg_rook_table = [
    32, 42, 32, 51, 63, 9, 31, 43,
    27, 32, 58, 62, 80, 67, 26, 44,
    -5, 19, 26, 36, 17, 45, 61, 16,
    -24, -11, 7, 26, 24, 35, -8, -20,
    -36, -26, -12, -1, 9, -7, 6, -23,
    -45, -25, -16, -17, 3, 0, -5, -33,
    -44, -16, -20, -9, -1, 11, -6, -71,
    -19, -13, 1, 17, 16, 7, -37, -26
]

eg_rook_table = [
    13, 10, 18, 15, 12, 12, 8, 5,
    11, 13, 13, 11, -3, 3, 8, 3,
    7, 7, 7, 5, 4, -3, -5, -3,
    4, 3, 13, 1, 2, 1, -1, 2,
    3, 5, 8, 4, -5, -6, -8, -11,
    -4, 0, -5, -1, -7, -12, -8, -16,
    -6, -6, 0, 2, -9, -9, -11, -3,
    -9, 2, 3, -1, -5, -13, 4, -20
]

mg_queen_table = [
    -28, 0, 29, 12, 59, 44, 43, 45,
    -24, -39, -5, 1, -16, 57, 28, 54,
    -13, -17, 7, 8, 29, 56, 47, 57,
    -27, -27, -16, -16, -1, 17, -2, 1,
    -9, -26, -9, -10, -2, -4, 3, -3,
    -14, 2, -11, -2, -5, 2, 14, 5,
    -35, -8, 11, 2, 8, 15, -3, 1,
    -1, -18, -9, 10, -15, -25, -31, -50
]

eg_queen_table = [
    -9, 22, 22, 27, 27, 19, 10, 20,
    -17, 20, 32, 41, 58, 25, 30, 0,
    -20, 6, 9, 49, 47, 35, 19, 9,
    3, 22, 24, 45, 57, 40, 57, 36,
    -18, 28, 19, 47, 31, 34, 39, 23,
    -16, -27, 15, 6, 9, 17, 10, 5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43, -5, -32, -20, -41
]

mg_king_table = [
    -65, 23, 16, -15, -56, -34, 2, 13,
    29, -1, -20, -7, -8, -4, -38, -29,
    -9, 24, 2, -16, -20, 6, 22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49, -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
    1, 7, -8, -64, -43, -16, 9, 8,
    -15, 36, 12, -54, 8, -28, 24, 14
]

eg_king_table = [
    -74, -35, -18, -18, -11, 15, 4, -17,
    -12, 17, 14, 17, 17, 38, 23, 11,
    10, 17, 23, 15, 20, 45, 44, 13,
    -8, 22, 24, 27, 26, 33, 26, 3,
    -18, -4, 21, 24, 27, 23, 9, -11,
    -19, -3, 11, 21, 23, 16, 7, -9,
    -27, -11, 4, 13, 14, 4, -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43
]

mg_table = [
    mg_pawn_table, mg_knight_table, mg_bishop_table,
    mg_rook_table, mg_queen_table, mg_king_table
]

eg_table = [
    eg_pawn_table, eg_knight_table, eg_bishop_table,
    eg_rook_table, eg_queen_table, eg_king_table
]

gamephase_inc = [0, 1, 1, 2, 4, 0]

def evaluate_board(board):
    mg_score = [0, 0]
    eg_score = [0, 0]
    game_phase = 0

    for square, piece in board.piece_map().items():
        piece_type = piece.piece_type - 1
        color = 0 if piece.color == chess.WHITE else 1
        mg_score[color] += mg_table[piece_type][square]
        eg_score[color] += eg_table[piece_type][square]
        game_phase += gamephase_inc[piece_type]

    mg_phase = game_phase
    if mg_phase > 24:
        mg_phase = 24
    eg_phase = 24 - mg_phase

    mg_total = mg_score[board.turn] - mg_score[1 - board.turn]
    eg_total = eg_score[board.turn] - eg_score[1 - board.turn]

    eval_value = (mg_total * mg_phase + eg_total * eg_phase) / 24
    return eval_value

def minimax(depth, maximizingPlayer, alpha, beta, board):
    if depth == 0 or board.is_game_over():
        eval_value = evaluate_board(board)
        return eval_value, None

    best_move = None

    if maximizingPlayer:
        best = MIN
        for move in board.legal_moves:
            board.push(move)
            val, _ = minimax(depth - 1, False, alpha, beta, board)
            board.pop()
            if val > best:
                best = val
                best_move = move
            alpha = max(alpha, best)
            if beta <= alpha:
                break
    else:
        best = MAX
        for move in board.legal_moves:
            board.push(move)
            val, _ = minimax(depth - 1, True, alpha, beta, board)
            board.pop()
            if val < best:
                best = val
                best_move = move
            beta = min(beta, best)
            if beta <= alpha:
                break
    return best, best_move

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

# Game loop
while running and games_played < max_games:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    draw_pieces_on_board()

    pygame.display.flip()

    if board.turn == chess.BLACK:  # AI plays as Black
        legal_moves = list(board.legal_moves)
        _, ai_move = minimax(max_depth, False, MIN, MAX, board)
        if ai_move:
            board.push(ai_move)
            print(f"Black {ai_move.uci()}")
        else:
            ai_move = random.choice(legal_moves)
            board.push(ai_move)
            print(f"Black (random) {ai_move.uci()}")

    elif board.turn == chess.WHITE:  # Stockfish's turn
        stockfish.set_fen_position(board.fen())
        result = stockfish.get_best_move()
        move = chess.Move.from_uci(result)
        board.push(move)
        print(f"White {move.uci()}")

    if board.is_game_over():
        result = board.result()
        games_played += 1
        if result == '1-0':
            print("Stockfish (White) won")
            ai_losses += 1
            actual_score = 0
        elif result == '0-1':
            print("AI (Black) won")
            ai_wins += 1
            actual_score = 1
        else:
            print("The game was a draw")
            draws += 1
            actual_score = 0.5
        
        expected_score = 1 / (1 + 10 ** ((opponent_elo - initial_elo) / 400))
        initial_elo += K * (actual_score - expected_score)
        initial_elo = int(initial_elo)  # Convert Elo to integer
        print(f"Current Elo after game {games_played}: {initial_elo}")

        board.reset()

    clock.tick(fps)

pygame.quit()

# Print performance metrics
print(f"Games played: {games_played}")
print(f"AI Wins: {ai_wins}")
print(f"AI Losses: {ai_losses}")
print(f"Draws: {draws}")
print(f"Estimated Elo rating: {initial_elo}")
