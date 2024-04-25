import pygame
import os

# Define the Piece class as you have it above
class Piece(pygame.sprite.Sprite):
    def __init__(self, filename, cols, rows):
        pygame.sprite.Sprite.__init__(self)
        self.pieces = {
            "white_pawn":   5, "white_knight": 3, "white_bishop": 2, "white_rook":   4, "white_king":   0, "white_queen":  1,
            "black_pawn":   11, "black_knight": 9, "black_bishop": 8, "black_rook":   10, "black_king":   6, "black_queen":  7
        }
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.cols = cols
        self.rows = rows
        self.cell_count = cols * rows
        self.rect = self.spritesheet.get_rect()
        w = self.cell_width = self.rect.width // self.cols
        h = self.cell_height = self.rect.height // self.rows
        self.cells = [(i % cols * w, i // cols * h, w, h) for i in range(self.cell_count)]

    def draw(self, surface, piece_name, coords):
        piece_index = self.pieces[piece_name]
        surface.blit(self.spritesheet, coords, self.cells[piece_index])

# Maps graphical coordinates (ie. (200, 300)) to coordinate pair (ie. (1, 2))
def graphical_coords_to_coords(graphical_coords):
    graphical_x = graphical_coords[0]
    graphical_y = graphical_coords[1]
    x = (int)(graphical_x / 100)
    y = (int)(graphical_y / 100)
    return (x, y)

def init_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    board[7] = ["white_rook", "white_knight", "white_bishop", "white_queen", 
                "white_king", "white_bishop", "white_knight", "white_rook"]
    board[6] = ["white_pawn"] * 8

    board[0] = ["black_rook", "black_knight", "black_bishop", "black_queen", 
                "black_king", "black_bishop", "black_knight", "black_rook"]
    board[1] = ["black_pawn"] * 8

    return board

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

board = init_board()

# Game loop
running = True
selected_piece = None
selected_position = None
dragging = False
mouse_pos = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # print(mouse_pos)
            col, row = graphical_coords_to_coords(mouse_pos)
            if board[row][col]:
                selected_piece = board[row][col]
                # print(selected_piece)
                selected_position = (col, row)
                dragging = True
        elif event.type == pygame.MOUSEMOTION and dragging:
            mouse_pos = pygame.mouse.get_pos()
            # print(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                col, row = graphical_coords_to_coords(mouse_pos)
                board[selected_position[1]][selected_position[0]] = None
                board[row][col] = selected_piece
                dragging = False


    # Draw the board with new colors
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

    # Draw pieces
    
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                centered_x = col * square_size + (square_size - chess_pieces.cell_width) // 2
                centered_y = row * square_size + (square_size - chess_pieces.cell_height) // 2

                if not (dragging and (col, row) == selected_position):
                    chess_pieces.draw(screen, piece, (centered_x, centered_y))

    if dragging:
        centered_x = mouse_pos[0] - chess_pieces.cell_width // 2
        centered_y = mouse_pos[1] - chess_pieces.cell_height // 2
        chess_pieces.draw(screen, selected_piece, (centered_x, centered_y))
    pygame.display.flip()


pygame.quit()
