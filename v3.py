import pygame
import os
import chess
import chess.syzygy
import chess.polyglot
import random

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

MAX, MIN = 10000, -10000

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
        chess.QUEEN: 900,
        chess.KING: 20000
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
    if piece and piece.color == player_color:
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
        print(f"Human {move.uci()}")
        if board.piece_at(square).piece_type == chess.PAWN and (chess.square_rank(square) == 0 or chess.square_rank(square) == 7):  # Check for pawn promotion
            board.remove_piece_at(square)
            x, y = graphical_coords_to_coords(pygame.mouse.get_pos())
            promotion_piece = prompt_promotion_piece(player_color, x * square_size, y * square_size)
            board.set_piece_at(square, promotion_piece)
    selected_piece = None
    selected_position = None
    dragging = False
    selected_legal_moves = set()

def draw_promotion_options(color, x, y):
    bg_width = 4 * chess_pieces.cell_width
    bg_height = chess_pieces.cell_height
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bg_width, bg_height))
    promotion_options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    option_images = [chess_pieces.spritesheet.subsurface(chess_pieces.cells[chess_pieces.pieces[chess.Piece(pt, color)]]) for pt in promotion_options]
    for i, image in enumerate(option_images):
        screen.blit(image, (x + i * chess_pieces.cell_width, y))

def prompt_promotion_piece(color, x, y):
    promotion_options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    option_rects = [pygame.Rect(x + i * chess_pieces.cell_width, y, chess_pieces.cell_width, chess_pieces.cell_height) for i in range(4)]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        return chess.Piece(promotion_options[i], color)

        draw_board()
        draw_pieces_on_board()
        draw_promotion_options(color, x, y)
        pygame.display.flip()

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

def show_menu():
    global running, player_color
    font = pygame.font.Font(None, 36)
    menu_text = ["Choose who goes first", "1. Human (White)", "2. Human (Black)"]
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
                    player_color = chess.WHITE
                    return
                elif event.key == pygame.K_2:
                    player_color = chess.BLACK
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
selected_piece = None
selected_position = None
selected_legal_moves = set()
dragging = False
mouse_pos = None
max_depth = 4
fps = 60
clock = pygame.time.Clock()

# Show the menu to choose who goes first
player_color = None
show_menu()

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

    if board.turn == player_color:
        clock.tick(fps)
        continue

    if board.turn == chess.BLACK:  # AI plays as Black
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
                ai_move = random.choice(list(board.legal_moves))
                board.push(ai_move)
                print(f"Black (random) {ai_move.uci()}")
    elif board.turn == chess.WHITE:  # AI plays as White
        book_move = get_book_move(board)
        if book_move:
            board.push(book_move)
            print(f"White (book) {book_move.uci()}")
        else:
            _, ai_move = minimax(max_depth, True, MIN, MAX, board)
            if ai_move:
                board.push(ai_move)
                print(f"White {ai_move.uci()}")
            else:
                ai_move = random.choice(list(board.legal_moves))
                board.push(ai_move)
                print(f"White (random) {ai_move.uci()}")

    if board.is_game_over():
        result = board.result()
        if result == '1-0':
            print("Human (White) won" if player_color == chess.WHITE else "AI (White) won")
        elif result == '0-1':
            print("AI (Black) won" if player_color == chess.WHITE else "Human (Black) won")
        else:
            print("The game was a draw")
        board.reset()

    clock.tick(fps)

pygame.quit()
