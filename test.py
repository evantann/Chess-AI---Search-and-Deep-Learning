import chess
import chess.polyglot

# Path to the Polyglot opening book file
book_path = 'gm2001.bin'

# Function to read moves from the opening book
def read_opening_book(book_path):
    # Create a chess board
    board = chess.Board()

    # Open the Polyglot book
    with chess.polyglot.open_reader(book_path) as reader:
        # Iterate through entries in the opening book
        for entry in reader.find_all(board):
            move = entry.move()
            weight = entry.weight
            learn = entry.learn

            print(f"Move: {move}, Weight: {weight}, Learn: {learn}")

            # Apply the move to the board
            board.push(move)

            # Print the board position
            print(board)
            
            # Reset the board to the initial position
            board.pop()

# Read and print opening moves
read_opening_book(book_path)
