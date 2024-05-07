import pygame
import os
import chess
import regex as re
import numpy as np

running = True
selected_piece = None
selected_position = None
selected_legal_moves = set()
dragging = False
mouse_pos = None
fps = 60
clock = pygame.time.Clock()


# Define the Piece class as you have it above
class Piece(pygame.sprite.Sprite):
    def __init__(self, filename, cols, rows):
        pygame.sprite.Sprite.__init__(self)
        self.pieces = {}
        index = 0
        for color in (chess.WHITE, chess.BLACK):
            for piece_type in (chess.KING, chess.QUEEN, chess.BISHOP, chess.KNIGHT, chess.ROOK, chess.PAWN):
                piece = chess.Piece(piece_type, color)
                # Map each piece to its corresponding cell index based on its type and color
                # print(piece, index)
                self.pieces[piece] = index
                index = (index + 1)
        # print(self.pieces)

        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.cols = cols
        self.rows = rows
        self.cell_count = cols * rows
        self.rect = self.spritesheet.get_rect()
        w = self.cell_width = self.rect.width // self.cols
        h = self.cell_height = self.rect.height // self.rows
        self.cells = [(i % cols * w, i // cols * h, w, h) for i in range(self.cell_count)]

    def draw(self, surface, piece, coords):
        if piece in self.pieces:
            piece_index = self.pieces[piece]
            surface.blit(self.spritesheet, coords, self.cells[piece_index])

# Maps graphical coordinates (ie. (200, 300)) to coordinate pair (ie. (1, 2))
def graphical_coords_to_coords(graphical_coords):
    graphical_x = graphical_coords[0]
    graphical_y = graphical_coords[1]
    x = (int)(graphical_x / 100)
    y = (int)(graphical_y / 100)
    return (x, y)

# Maps array coords (x, y) to chess square
def coords_to_square(x, y):
    return chess.square(x, 7 - y)

def square_to_coords(square):
    return (chess.square_file(square), 7 - chess.square_rank(square))

# Gets all legal moves for selected piece
def update_selected_legal_moves():
    selected_square = coords_to_square(selected_position[0], selected_position[1])
    for move in board.legal_moves:
        if move.from_square == selected_square:
            # selected_legal_moves.add(move)
            selected_legal_moves.add(move.to_square)

# ---------- LOGIC FUNCTIONS ------------

def start_piece_drag():
    global selected_piece, selected_position, dragging

    mouse_pos = pygame.mouse.get_pos()
    # print(mouse_pos)
    col, row = graphical_coords_to_coords(mouse_pos)
    square = coords_to_square(col, row)
    piece = board.piece_at(square)
    if piece:
        selected_piece = piece
        selected_position = (col, row)
        dragging = True
        update_selected_legal_moves()
        # print(selected_legal_moves)

# def update_piece_drag():
#     global mouse_pos
#     mouse_pos = pygame.mouse.get_pos()

def finish_piece_drag():
    global selected_piece, selected_position, dragging, selected_legal_moves
    mouse_pos = pygame.mouse.get_pos()
    col, row = graphical_coords_to_coords(mouse_pos)

    # Update board if move is valid.
    square = coords_to_square(col, row)
    if square in selected_legal_moves:
        from_square = coords_to_square(selected_position[0], selected_position[1])
        to_square = square
        print(chess.SQUARE_NAMES[from_square], chess.SQUARE_NAMES[to_square])
        move = chess.Move(from_square, to_square)
        board.push(move)

    selected_piece = None
    selected_position = None
    dragging = False
    selected_legal_moves = set()


# ---------- DRAWING FUNCTIONS ----------

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))
    if selected_legal_moves:
        for move in selected_legal_moves:
            # to_sq = move.to_square
            col, row = square_to_coords(move)
            pygame.draw.rect(screen, (255, 255, 0), (col * square_size, row * square_size, square_size, square_size))
def draw_pieces_on_board():
    for row in range(8):
        for col in range(8):
            square = coords_to_square(col, row)
            piece = board.piece_at(square)
            if piece:
                centered_x = col * square_size + (square_size - chess_pieces.cell_width) // 2
                centered_y = row * square_size + (square_size - chess_pieces.cell_height) // 2

                if not (dragging and (col, row) == selected_position):
                    chess_pieces.draw(screen, piece, (centered_x, centered_y))

def draw_piece_dragged():
    mouse_pos = pygame.mouse.get_pos()
    # print(mouse_pos)
    if mouse_pos:
        centered_x = mouse_pos[0] - chess_pieces.cell_width // 2
        centered_y = mouse_pos[1] - chess_pieces.cell_height // 2
        # print(screen, selected_piece, centered_x, centered_y)
        chess_pieces.draw(screen, selected_piece, (centered_x, centered_y))
        
def best_move(board, depth):
    best_eval = -float('inf') if board.turn else float('inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, -float('inf'), float('inf'), not board.turn)
        board.pop()
        if board.turn and eval > best_eval:  # White is maximizing player
            best_eval = eval
            best_move = move
        elif not board.turn and eval < best_eval:  # Black is minimizing player
            best_eval = eval
            best_move = move
    return best_move

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval
    
def evaluate_board(board):
    if board.is_checkmate():
        if board.turn:
            return -float('inf')  # Black wins
        else:
            return float('inf')  # White wins
    if board.is_stalemate():
        return 0  # Draw
    
    str_rep = board_to_rep(board)
    position_eval = str_rep * piece_square_table if board.turn else str_rep * opponent_piece_square_table
    eval = sum_3d_array(position_eval)

    piece_values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
    
    for (piece, value) in piece_values.items():
        eval += len(board.pieces(piece, chess.WHITE)) * value
        eval -= len(board.pieces(piece, chess.BLACK)) * value

    return eval

# creates a binary representation of the board 
# 3D matrix where each layer represents a piece type
# 1 if the piece is white, -1 if the piece is black, 0 if the square is empty
def board_to_rep(board):
    pieces = ['p', 'r', 'n', 'b', 'q', 'k']
    layers = []
    for piece in pieces:
        layers.append(create_rep_layer(board, piece))
    board_rep = np.stack(layers)
    return board_rep

# helper function of board_to_rep;
def create_rep_layer(board, type):
    s = str(board)
    s = re.sub(f'[^ {type} {type.upper()} \n]', '.', s)
    s = re.sub(f'{type}', '-1', s)
    s = re.sub (f'{type.upper ()}', '1', s)
    s = re.sub (f'\.', '0', s)

    board_mat = []
    for row in s.split('\n'):
        row = row.split(' ')
        row = [int(x) for x in row]
        board_mat.append(row)
    return np.array(board_mat)

# sums all positional values of the board
def sum_3d_array(arr):
    total = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            for k in range(len(arr[i][j])):
                total += arr[i][j][k]
    return total

piece_square_table = [
# pawn
[[0,  0,  0,  0,  0,  0,  0,  0],
[50, 50, 50, 50, 50, 50, 50, 50],
[10, 10, 20, 30, 30, 20, 10, 10],
[5,  5, 10, 25, 25, 10,  5,  5],
[0,  0,  0, 20, 20,  0,  0,  0],
[5, -5,-10,  0,  0,-10, -5,  5],
[5, 10, 10,-20,-20, 10, 10,  5],
[0,  0,  0,  0,  0,  0,  0,  0]],
 
#  knight
[[-50,-40,-30,-30,-30,-30,-40,-50],
[-40,-20,  0,  0,  0,  0,-20,-40],
[-30,  0, 10, 15, 15, 10,  0,-30],
[-30,  5, 15, 20, 20, 15,  5,-30],
[-30,  0, 15, 20, 20, 15,  0,-30],
[-30,  5, 10, 15, 15, 10,  5,-30],
[-40,-20,  0,  5,  5,  0,-20,-40],
[-50,-40,-30,-30,-30,-30,-40,-50]],
 
#  bishop
[[-20,-10,-10,-10,-10,-10,-10,-20],
[-10,  0,  0,  0,  0,  0,  0,-10],
[-10,  0,  5, 10, 10,  5,  0,-10],
[-10,  5,  5, 10, 10,  5,  5,-10],
[-10,  0, 10, 10, 10, 10,  0,-10],
[-10, 10, 10, 10, 10, 10, 10,-10],
[-10,  5,  0,  0,  0,  0,  5,-10],
[-20,-10,-10,-10,-10,-10,-10,-20]],
 
#  rook
[[0,  0,  0,  0,  0,  0,  0,  0],
[5, 10, 10, 10, 10, 10, 10,  5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[0,  0,  0,  5,  5,  0,  0,  0]],

#  queen
[[-20,-10,-10, -5, -5,-10,-10,-20],
[-10,  0,  0,  0,  0,  0,  0,-10],
[-10,  0,  5,  5,  5,  5,  0,-10],
[-5,  0,  5,  5,  5,  5,  0, -5],
[0,  0,  5,  5,  5,  5,  0, -5],
[-10,  5,  5,  5,  5,  5,  0,-10],
[-10,  0,  5,  0,  0,  0,  0,-10],
[-20,-10,-10, -5, -5,-10,-10,-20]],

#  king
[[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-20,-30,-30,-40,-40,-30,-30,-20],
[-10,-20,-20,-20,-20,-20,-20,-10],
[20, 20,  0,  0,  0,  0, 20, 20],
[20, 30, 10,  0,  0, 10, 30, 20]]
]

# reverses the matrices in the piece-square table to create the opponent piece-square table
def generate_opp_ps_table(matrices):
    pst = []
    for matrix in matrices:
        matrix[::-1]
        pst.append(matrix)
    return pst

opponent_piece_square_table = generate_opp_ps_table(piece_square_table)

# Initialize Pygame
pygame.init()

# Set up the display
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Chess Board")

# Load the chess pieces
filename = os.path.join('res', 'pieces.png')
chess_pieces = Piece(filename, 6, 2)

# Define chess.com-like green colors
DARK_GREEN = (118, 150, 86)  # A muted, dark green
LIGHT_GREEN = (238, 238, 210)  # A soft, light green

# Size of squares
square_size = screen_size[0] // 8

board = chess.Board()

# Game loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_piece_drag()
        # elif event.type == pygame.MOUSEMOTION and dragging:
        #     update_piece_drag()
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            finish_piece_drag()
            if board.turn == chess.BLACK:  # Let's assume the AI plays as Black
                ai_move = best_move(board, 3)  # Depth is 3 for example
                if ai_move:
                    board.push(ai_move)

    draw_board()
    draw_pieces_on_board()

    if dragging:
        draw_piece_dragged()
    
    pygame.display.flip()

    clock.tick(fps)


pygame.quit()