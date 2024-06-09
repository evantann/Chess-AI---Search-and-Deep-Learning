import pygame
import os
import chess
import chess.syzygy
import chess.polyglot
from stockfish import Stockfish
import random
import time

# Initialize Stockfish engine using the pip-installed stockfish package
stockfish = Stockfish()
stockfish.set_skill_level(4)  # Set the skill level (0 to 20)

# Initialize Syzygy tablebases
tablebase = chess.syzygy.Tablebase()

# Directory containing the Polyglot books
polyglot_directory = 'polyglot-collection'
polyglot_filenames = [
    'Perfect2023.bin', 'Titans.bin', 'Book.bin', 'book2.bin', 'codekiddy.bin', 'baron30.bin',
    'DCbook_large.bin', 'Elo2400.bin', 'final-book.bin', 'gm2001.bin',
    'gm2600.bin', 'human.bin', 'komodo.bin', 'KomodoVariety.bin', 'Performance.bin', 'varied.bin'
]
polyglot_books = [os.path.join(polyglot_directory, filename) for filename in polyglot_filenames]

def get_book_move(board):
    for book_filename in polyglot_books:
        try:
            with chess.polyglot.open_reader(book_filename) as reader:
                entry = reader.find(board)
                return entry.move
        except (KeyError, IndexError):
            continue
    return None

# Performance metrics
ai_wins = 0
ai_losses = 0
draws = 0
games_played = 0
max_games = 10  # Set the number of games to play
move_times = []  # List to store move calculation times

# Elo calculation parameters
initial_elo = 1200
opponent_elo = 1200  # Assuming Stockfish has a very high rating
K = 32  # K-factor in Elo rating system

MAX, MIN = 10000, -10000  # Use more realistic values for MAX and MIN

def start_move_timer():
    return time.time()

def stop_move_timer(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    move_times.append(elapsed_time)

piece_square_table = {
    chess.PAWN: [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ],
    chess.KNIGHT: [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ],
    chess.BISHOP: [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ],
    chess.ROOK: [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ],
    chess.QUEEN: [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ],
    chess.KING: [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
}

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

def evaluate_board(board):
    if board.is_checkmate():
        return MIN if board.turn else MAX

    # Check for endgame using Syzygy tablebases
    with tablebase:
        if not (board.has_castling_rights(chess.WHITE) or board.has_castling_rights(chess.BLACK) or board.has_legal_en_passant()):
            try:
                wdl = tablebase.probe_wdl(board)
                if wdl is not None:
                    print("Syzygy tablebase used for evaluation.")
                    return wdl * MAX  # Scale the WDL result to a large value
            except KeyError:
                pass
    
    material = sum(get_piece_value(piece) for piece in board.piece_map().values())
    positional = sum(piece_square_table[piece.piece_type][square // 8][square % 8] * (1 if piece.color == chess.WHITE else -1) for square, piece in board.piece_map().items())
    
    # Add a bonus for pawn advancement in the endgame
    if len(board.piece_map()) <= 10:  # Endgame condition
        pawn_bonus = 0
        for square, piece in board.piece_map().items():
            if piece.piece_type == chess.PAWN:
                rank = chess.square_rank(square)
                if piece.color == chess.WHITE:
                    pawn_bonus += (rank * 10)  # Reward for advancing pawns
                else:
                    pawn_bonus -= ((7 - rank) * 10)
        return material + positional + pawn_bonus
    
    return material + positional

def get_piece_value(piece):
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 5000,
        chess.KING: 30000
    }
    return values[piece.piece_type] if piece.color == chess.WHITE else -values[piece.piece_type]

def order_moves(board):
    """
    Order the moves based on their priority: captures, checks, promotions, and then quiet moves.
    """
    move_scores = []
    for move in board.legal_moves:
        if board.gives_check(move):
            score = 50  # Arbitrary score for checks
        elif move.promotion:
            score = 75  # Arbitrary score for promotions
        else:
            score = 10  # Lower score for quiet moves
        move_scores.append((score, move))

    # Sort moves by their scores in descending order
    move_scores.sort(reverse=True, key=lambda x: x[0])
    ordered_moves = [move for score, move in move_scores]

    return ordered_moves

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
            if (piece):
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
        start_time = start_move_timer()  # Start timing
        time_limit = 15  # Time limit for AI move calculation
        book_move = get_book_move(board)
        if book_move:
            board.push(book_move)
            print(f"Black (book) {book_move.uci()}")
        else:
            _, ai_move = minimax(max_depth, False, MIN, MAX, board)
            if ai_move:
                board.push(ai_move)
                print(f"Black {ai_move.uci()}")
            else:
                legal_moves = list(board.legal_moves)
                ai_move = random.choice(legal_moves)
                board.push(ai_move)
                print(f"Black (random) {ai_move.uci()}")
        stop_move_timer(start_time)  # Stop timing

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

# Print average move time
if move_times:
    average_move_time = sum(move_times) / len(move_times)
    print(f"Average move time: {average_move_time} seconds")
else:
    print("No move times recorded.")
