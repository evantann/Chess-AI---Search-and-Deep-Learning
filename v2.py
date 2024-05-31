import pygame
import os
import chess
import random

MAX, MIN = 100000, -100000

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

    material = 0
    positional = 0
    for square, piece in board.piece_map().items():
        piece_value = get_piece_value(piece)
        material += piece_value

        row, col = divmod(square, 8)
        positional_value = piece_square_table[piece.piece_type][row][col]
        positional += positional_value if piece.color == chess.WHITE else -positional_value

    eval_value = material + positional
    return eval_value


def get_piece_value(piece):
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    return values[piece.piece_type] if piece.color == chess.WHITE else -values[piece.piece_type]

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
def graphical_coords_to_coords(graphical_coords):
    return graphical_coords[0] // square_size, graphical_coords[1] // square_size

def coords_to_square(x, y):
    return chess.square(x, 7 - y)

def square_to_coords(square):
    return chess.square_file(square), 7 - chess.square_rank(square)

def update_selected_legal_moves():
    global selected_legal_moves
    selected_legal_moves = set()
    selected_square = coords_to_square(*selected_position)
    for move in board.legal_moves:
        if move.from_square == selected_square:
            selected_legal_moves.add(move.to_square)

def select_piece():
    global selected_piece, selected_position, dragging
    col, row = graphical_coords_to_coords(pygame.mouse.get_pos())
    square = coords_to_square(col, row)
    piece = board.piece_at(square)
    if piece:
        selected_piece = piece
        selected_position = (col, row)
        dragging = True
        update_selected_legal_moves()

def move_piece():
    global selected_piece, selected_position, dragging, selected_legal_moves
    col, row = graphical_coords_to_coords(pygame.mouse.get_pos())
    square = coords_to_square(col, row)
    if square in selected_legal_moves:
        move = chess.Move(coords_to_square(*selected_position), square)
        board.push(move)
        print(f"White {move.uci()}")
        if board.piece_at(square).piece_type == chess.PAWN and (chess.square_rank(square) == 0 or chess.square_rank(square) == 7):  # Check for pawn promotion
            promotion_piece = prompt_promotion_piece()
            board.remove_piece_at(square)
            board.set_piece_at(square, promotion_piece)
    selected_piece = None
    selected_position = None
    dragging = False
    selected_legal_moves = set()

def prompt_promotion_piece():
    while True:
        promotion_piece_str = input("Promote to (Q, R, B, N): ").upper()
        if promotion_piece_str == "Q":
            return chess.Piece(chess.QUEEN, chess.WHITE)
        elif promotion_piece_str == "R":
            return chess.Piece(chess.ROOK, chess.WHITE)
        elif promotion_piece_str == "B":
            return chess.Piece(chess.BISHOP, chess.WHITE)
        elif promotion_piece_str == "N":
            return chess.Piece(chess.KNIGHT, chess.WHITE)
        else:
            print("Invalid choice. Please select one of: Q, R, B, N")



# Drawing functions
def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))
    for move in selected_legal_moves:
        col, row = square_to_coords(move)
        pygame.draw.rect(screen, (255, 255, 0), (col * square_size, row * square_size, square_size, square_size))

def draw_pieces_on_board():
    for row in range(8):
        for col in range(8):
            square = coords_to_square(col, row)
            piece = board.piece_at(square)
            if piece and not (dragging and (col, row) == selected_position):
                chess_pieces.draw(screen, piece, (col * square_size + (square_size - chess_pieces.cell_width) // 2, row * square_size + (square_size - chess_pieces.cell_height) // 2))

def draw_piece_dragged():
    if dragging and selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        chess_pieces.draw(screen, selected_piece, (mouse_pos[0] - chess_pieces.cell_width // 2, mouse_pos[1] - chess_pieces.cell_height // 2))

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
selected_piece = None
selected_position = None
selected_legal_moves = set()
dragging = False
mouse_pos = None
max_depth = 4
fps = 60
clock = pygame.time.Clock()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if selected_piece:
                move_piece()
            else:
                select_piece()
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            move_piece()
        elif event.type == pygame.MOUSEMOTION and dragging:
            mouse_pos = pygame.mouse.get_pos()

    draw_board()
    draw_pieces_on_board()

    if dragging:
        draw_piece_dragged()

    pygame.display.flip()

    if board.turn == chess.BLACK:  # AI plays as Black
        _, ai_move = minimax(max_depth, False, MIN, MAX, board)
        if ai_move:
            board.push(ai_move)
            print(f"Black {ai_move.uci()}")
        else:
            ai_move = random.choice(list(board.legal_moves))
            board.push(ai_move)
            print(f"Black (random) {ai_move.uci()}")

    clock.tick(fps)

pygame.quit()
