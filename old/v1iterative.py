import pygame
import os
import chess
import time

# Constants
SCREEN_SIZE = 800
SQUARE_SIZE = SCREEN_SIZE // 8
DARK_GREEN = (118, 150, 86)
LIGHT_GREEN = (238, 238, 210)
FPS = 60
MAX_DEPTH = 3

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Chess Board")
clock = pygame.time.Clock()

# Load the chess pieces
filename = os.path.join('res', 'pieces.png')

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

chess_pieces = Piece(filename, 6, 2)
board = chess.Board()

# State variables
running = True
selected_piece = None
selected_position = None
selected_legal_moves = set()
dragging = False

def graphical_coords_to_coords(graphical_coords):
    return graphical_coords[0] // SQUARE_SIZE, graphical_coords[1] // SQUARE_SIZE

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
    selected_piece = None
    selected_position = None
    dragging = False
    selected_legal_moves = set()

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    for move in selected_legal_moves:
        col, row = square_to_coords(move)
        pygame.draw.rect(screen, (255, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces_on_board():
    for row in range(8):
        for col in range(8):
            square = coords_to_square(col, row)
            piece = board.piece_at(square)
            if piece:
                chess_pieces.draw(screen, piece, (col * SQUARE_SIZE + (SQUARE_SIZE - chess_pieces.cell_width) // 2, row * SQUARE_SIZE + (SQUARE_SIZE - chess_pieces.cell_height) // 2))

def draw_piece_dragged():
    if dragging and selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        chess_pieces.draw(screen, selected_piece, (mouse_pos[0] - chess_pieces.cell_width // 2, mouse_pos[1] - chess_pieces.cell_height // 2))

def evaluate_board(state):
    if state.is_checkmate():
        return -9999 if state.turn else 9999
    if state.is_stalemate():
        return 0

    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    eval = sum(len(state.pieces(pt, chess.WHITE)) * val for pt, val in piece_values.items())
    eval -= sum(len(state.pieces(pt, chess.BLACK)) * val for pt, val in piece_values.items())

    return eval

def gen_children(state):
    res = []
    for move in state.legal_moves:
        state.push(move)
        next_board = state.copy()
        res.append(next_board)
        state.pop()
    return res
def iterative_deepening(state, max_depth, time_limit):
    start_time = time.time()
    best_move = None

    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break  # Stop if we run out of time

        val, move = Min(state, 0, -9999, 9999, depth)
        if move:
            best_move = move
        print(f"Depth {depth} completed with best move: {best_move}")

    return best_move

def Min(state, depth, alpha, beta, max_depth):
    if state.is_checkmate() or depth == max_depth:
        return evaluate_board(state), None
    val = 9999
    best_move = None
    children = gen_children(state)
    for child in children:
        next, _ = Max(child, depth + 1, alpha, beta, max_depth)
        if next <= val:
            val = next
            best_move = child.peek()
        beta = min(beta, val)
        if val < alpha:
            break
    return val, best_move

def Max(state, depth, alpha, beta, max_depth):
    if state.is_checkmate() or depth == max_depth:
        return evaluate_board(state), None
    val = -9999
    best_move = None
    children = gen_children(state)
    for child in children:
        next, _ = Min(child, depth + 1, alpha, beta, max_depth)
        if next >= val:
            val = next
            best_move = child.peek()
        alpha = max(alpha, val)
        if val > beta:
            break
    return val, best_move

def main():
    global running
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

        draw_board()
        draw_pieces_on_board()
        if dragging:
            draw_piece_dragged()
        pygame.display.flip()

        if board.turn == chess.BLACK:
            ai_move = iterative_deepening(board, MAX_DEPTH, time_limit=1)  # 1 second time limit
            if ai_move:
                board.push(ai_move)

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
