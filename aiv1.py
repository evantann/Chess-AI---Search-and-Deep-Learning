import chess

def evaluate_board(state):
    if state.is_checkmate():
        if state.turn:
            return -9999  # Black wins
        else:
            return 9999  # White wins
    if state.is_stalemate():
        return 0  # Draw

    eval = 0
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

    for (piece, value) in piece_values.items():
        eval += len(state.pieces(piece, chess.WHITE)) * value
        eval -= len(state.pieces(piece, chess.BLACK)) * value

    return eval

def gen_children(state):
    res = []
    for move in state.legal_moves:
        state.push(move)
        next_board = state.copy()
        res.append(next_board)
        state.pop()
    return res

def Max(state, depth, alpha, beta, max_depth):
    if state.is_checkmate() or depth == max_depth:
        return evaluate_board(state), None
    val = -9999
    best_move = None
    children = gen_children(state)
    for child in children:
        next, _ = Min(child, depth+1, alpha, beta, max_depth)
        if next >= val:
            val = next
            best_move = child.peek()
        alpha = max(alpha, val)
        if val > beta:
            break
    return val, best_move

def Min(state, depth, alpha, beta, max_depth):
    if state.is_checkmate() or depth == max_depth:
        return evaluate_board(state), None
    val = 9999
    best_move = None
    children = gen_children(state)
    for child in children:
        next, _ = Max(child, depth+1, alpha, beta, max_depth)
        if next <= val:
            val = next
            best_move = child.peek()
        beta = min(beta, val)
        if val < alpha:
            break
    return val, best_move
