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

# Initial positions of the pieces on the board
initial_positions = {
    "a1": "white_rook", "b1": "white_knight", "c1": "white_bishop", "d1": "white_queen",
    "e1": "white_king", "f1": "white_bishop", "g1": "white_knight", "h1": "white_rook",
    "a2": "white_pawn", "b2": "white_pawn", "c2": "white_pawn", "d2": "white_pawn",
    "e2": "white_pawn", "f2": "white_pawn", "g2": "white_pawn", "h2": "white_pawn",
    "a7": "black_pawn", "b7": "black_pawn", "c7": "black_pawn", "d7": "black_pawn",
    "e7": "black_pawn", "f7": "black_pawn", "g7": "black_pawn", "h7": "black_pawn",
    "a8": "black_rook", "b8": "black_knight", "c8": "black_bishop", "d8": "black_queen",
    "e8": "black_king", "f8": "black_bishop", "g8": "black_knight", "h8": "black_rook",
}

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the board with new colors
    for row in range(8):
        for col in range(8):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

    # Draw the pieces, centered in each square
    for position, piece in initial_positions.items():
        x = (ord(position[0]) - ord('a')) * square_size
        y = (8 - int(position[1])) * square_size
        # Centering the piece in the square
        piece_width = chess_pieces.cell_width
        piece_height = chess_pieces.cell_height
        centered_x = x + (square_size - piece_width) // 2
        centered_y = y + (square_size - piece_height) // 2
        chess_pieces.draw(screen, piece, (centered_x, centered_y))

    pygame.display.flip()


pygame.quit()
