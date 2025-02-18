from src.board.chess_board import ChessBoard
import copy
import random
import time

MATE_VALUE = 100000

class ChessAI:
    def __init__(self, color):
        self.color = color
        self.piece_values = {
            'pawn': 100, 'knight': 320, 'bishop': 330,
            'rook': 500, 'queen': 900, 'king': 20000
        }
        self.position_values = {
            'pawn': [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            'knight': [
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            'bishop': [
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10, 10, 10, 10, 10, 10, 10,-10],
                [-10,  5,  0,  0,  0,  0,  5,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            'rook': [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            'queen': [
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            'king': [
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

        self.DOUBLED_PAWN_PENALTY = -10
        self.ISOLATED_PAWN_PENALTY = -20
        self.BACKWARD_PAWN_PENALTY = -15
        self.PASSED_PAWN_BONUS = 25
        self.MOBILITY_BONUS = 10
        self.CENTER_CONTROL_BONUS = 30
        self.CASTLING_BONUS = 60
        self.ROOK_ON_OPEN_FILE_BONUS = 25
        self.BISHOP_PAIR_BONUS = 50
        self.KNIGHT_OUTPOST_BONUS = 30
        self.center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}

        self.opening_book = [
            [((6, 4), (4, 4)), ((1, 4), (3, 4))],  # e4 e5
            [((6, 3), (4, 3)), ((1, 3), (3, 3))],  # d4 d5
            [((7, 6), (5, 5)), ((0, 1), (2, 2))],  # Nf3 Nc6
            [((6, 2), (4, 2)), ((1, 2), (3, 2))]   # c4 c5
        ]

        self.start_time = 0
        self.max_time = 0
        self.nodes = 0

        self.transposition_table = {}

    def get_best_move(self, board, max_time=3):
        self.start_time = time.time()
        self.max_time = max_time
        self.nodes = 0
        best_move = None
        best_value = float('-inf') if self.color == 'white' else float('inf')

        # Check opening book
        if len(board.move_history) < 2:
            for opening in self.opening_book:
                if len(board.move_history) == 0 and self.color == 'white':
                    return opening[0]
                elif len(board.move_history) == 1 and self.color == 'black':
                    if board.move_history[0] == opening[0]:
                        return opening[1]

        self.move_history = {}

        # Iterative deepening
        try:
            # Start with depth 1 and increase
            for depth in range(1, 5):  # Limit maximum depth to 4
                if self.is_time_up():
                    break
                
                search_board = board.copy()

                current_move = self.minimax(search_board, depth, float('-inf'), float('inf'), self.color == 'white', True)

                if current_move is not None and not self.is_time_up():
                    # Test if move is valid before accepting it
                    test_board = board.copy()
                    if test_board.move_piece(current_move[0], current_move[1], log=False):
                        best_move = current_move
                        print(f"Depth {depth}: Found move {current_move} with value {best_value}")
                    else:
                        print(f"Depth {depth}: Invalid move found {current_move}")

        except TimeoutError:
            pass
        
        if best_move:
            print(f"Final chosen move: {best_move}")
        else:
            print("Fallback Move")
    
        return best_move or self.get_fallback_move(board)
    
    def is_time_up(self):
        return time.time() - self.start_time > self.max_time
    
    def check_time(self):
        if self.is_time_up():
            raise TimeoutError

    def minimax(self, board, depth, alpha, beta, maximizing_player, root=False):
        self.nodes += 1
        
        if self.nodes % 1000 == 0:
            self.check_time()

        board_key = self.board_to_string(board)
        tt_key = (board_key, depth, alpha, beta, maximizing_player)
        if tt_key in self.transposition_table:
            cached_value, cached_move = self.transposition_table[tt_key]
            return cached_move if root else cached_value

        if depth == 0:
            return self.quiescence(board, alpha, beta, maximizing_player, 0)

        moves = self.get_ordered_moves(board, maximizing_player)
        if not moves:
            if self.is_in_check(board, maximizing_player):
                return float('-inf') if maximizing_player else float('inf')
            return 0  

        best_move = None
        best_value = float('-inf') if maximizing_player else float('inf')

        for move in moves:
            
            move_info = board.push_move_in_place(move[0], move[1])
            eval = self.minimax(board, depth - 1, alpha, beta, not maximizing_player)

            board.pop_move_in_place(move_info)
            
            if maximizing_player:
                if eval > best_value:
                    best_value = eval
                    best_move = move
                alpha = max(alpha, eval)
            else:
                if eval < best_value:
                    best_value = eval
                    best_move = move
                beta = min(beta, eval)
            
            if beta <= alpha:
                if maximizing_player and eval >= beta:
                    self.move_history[move] = self.move_history.get(move, 0) + depth * depth
                elif not maximizing_player and eval <= alpha:
                    self.move_history[move] = self.move_history.get(move, 0) + depth * depth
                break
        
        self.transposition_table[tt_key] = (best_value, best_move)

        result = best_move if root else best_value
        return result
        
    def quiescence(self, board, alpha, beta, maximizing_player, depth):

        self.nodes += 1
        if depth > 3 or self.is_time_up():
            return self.evaluate_board(board, depth)
        
        stand_pat = self.evaluate_board(board, depth)
        
        if maximizing_player:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        moves = self.get_ordered_moves(board, maximizing_player, captures_only=False)

        filtered_moves = []
        for move in moves:
            captured_piece = board.get_piece(move[1])
            if captured_piece:
                filtered_moves.append(move)
            else:
                # Temporarily push to see if it gives check
                move_info = board.push_move_in_place(move[0], move[1])
                opponent = 'black' if maximizing_player else 'white'
                if board.game_rules.is_in_check(opponent):
                    filtered_moves.append(move)
                board.pop_move_in_place(move_info)

        if maximizing_player:
            max_eval = stand_pat
            for move in filtered_moves:
                if self.is_time_up():
                    break
                move_info = board.push_move_in_place(move[0], move[1])
                eval_ = self.quiescence(board, alpha, beta, False, depth + 1)
                board.pop_move_in_place(move_info)

                max_eval = max(max_eval, eval_)
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = stand_pat
            for move in filtered_moves:
                if self.is_time_up():
                    break
                move_info = board.push_move_in_place(move[0], move[1])
                eval_ = self.quiescence(board, alpha, beta, True, depth + 1)
                board.pop_move_in_place(move_info)

                min_eval = min(min_eval, eval_)
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_fallback_move(self, board):
        moves = self.get_ordered_moves(board, self.color == 'white')
        if moves:
            return moves[0]
        return None

    def get_ordered_moves(self, board, maximizing_player, captures_only=False):
        moves = []
        color = 'white' if maximizing_player else 'black'

        def move_score(move):
            score = 0
            start, end = move
            moving_piece = board.get_piece(start)
            captured_piece = board.get_piece(end)
            
            # Capture scoring
            if captured_piece:
                score += 10 * self.piece_values[captured_piece.type] - self.piece_values[moving_piece.type]
            
            # Center control
            if end in self.center_squares:
                score += self.CENTER_CONTROL_BONUS
            
            # History heuristic
            score += self.move_history.get(move, 0)
            
            # Promotion potential
            if moving_piece.type == 'pawn' and (end[0] == 0 or end[0] == 7):
                score += self.piece_values['queen']
            
             # Promotion potential
            if moving_piece.type == 'pawn' and (end[0] == 0 or end[0] == 7):
                score += self.piece_values['queen']
                
            # Castling bonus (if move is a castling move)
            if moving_piece.type == 'king' and abs(start[1] - end[1]) == 2:
                score += 50  # Significant bonus for castling

            # En passant
            if moving_piece.type == 'pawn' and abs(start[1] - end[1]) == 1:
                if not captured_piece and board.last_double_pawn_move:
                    if board.last_double_pawn_move[1] == end[1]:  # Valid en passant capture
                        score += 15

            import random
            score += random.uniform(-0.1, 0.1)
            
            return score
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if board.move_validator.is_valid_move((row, col), (end_row, end_col)):
                                move = ((row, col), (end_row, end_col))
                                if not captures_only or board.get_piece((end_row, end_col)):
                                    moves.append(move)

        return sorted(moves, key=move_score, reverse=True)

    def get_all_possible_moves(self, board, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if board.move_validator.is_valid_move((row, col), (end_row, end_col)):
                                moves.append(((row, col), (end_row, end_col)))
        return moves

    def make_move(self, board, move):
        new_board = copy.deepcopy(board)
        new_board.move_piece(move[0], move[1], log=False)
        return new_board

    def is_game_over(self, board):
        return board.game_rules.is_checkmate('white') or board.game_rules.is_checkmate('black') or board.game_rules.is_stalemate('white')

    def evaluate_board(self, board, depth = 0):
        if board.game_rules.is_checkmate('white'):
            return -(999999) + depth
        if board.game_rules.is_checkmate('black'):
            return 999999 - depth

        score = 0
        w_bishops = 0
        b_bishops = 0

        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if not piece:
                    continue

                value = self.piece_values[piece.type]
                is_white = piece.color == 'white'
                multiplier = 1 if is_white else -1

                # Basic material score
                score += value * multiplier

                # Track bishops for bishop pair bonus
                if piece.type == 'bishop':
                    if is_white:
                        w_bishops += 1
                    else:
                        b_bishops += 1

                # Piece-specific bonuses
                if piece.type == 'pawn':
                    score += self.evaluate_pawn(board, row, col, is_white) * multiplier
                elif piece.type == 'knight':
                    score += self.evaluate_knight(board, row, col, is_white) * multiplier
                elif piece.type == 'bishop':
                    score += self.evaluate_bishop(board, row, col, is_white) * multiplier
                elif piece.type == 'rook':
                    score += self.evaluate_rook(board, row, col, is_white) * multiplier
                elif piece.type == 'king':
                    score += self.evaluate_king(board, row, col, is_white) * multiplier

        # Bishop pair bonus
        if w_bishops >= 2:
            score += self.BISHOP_PAIR_BONUS
        if b_bishops >= 2:
            score -= self.BISHOP_PAIR_BONUS

        return score
    
    def evaluate_pawn(self, board, row, col, is_white):
        score = 0
        
        # Check for doubled pawns
        pawns_in_file = 0
        for r in range(8):
            piece = board.get_piece((r, col))
            if piece and piece.type == 'pawn' and piece.color == ('white' if is_white else 'black'):
                pawns_in_file += 1
        if pawns_in_file > 1:
            score += self.DOUBLED_PAWN_PENALTY

        # Check for isolated pawns
        isolated = True
        for adjacent_col in [col-1, col+1]:
            if 0 <= adjacent_col < 8:
                for r in range(8):
                    piece = board.get_piece((r, adjacent_col))
                    if piece and piece.type == 'pawn' and piece.color == ('white' if is_white else 'black'):
                        isolated = False
                        break
        if isolated:
            score += self.ISOLATED_PAWN_PENALTY

        # Passed pawn check
        passed = True
        direction = -1 if is_white else 1
        for r in range(row + direction, 0 if is_white else 7, direction):
            for c in [col-1, col, col+1]:
                if 0 <= c < 8:
                    piece = board.get_piece((r, c))
                    if piece and piece.type == 'pawn' and piece.color != ('white' if is_white else 'black'):
                        passed = False
                        break
        if passed:
            score += self.PASSED_PAWN_BONUS

        return score
    
    def evaluate_knight(self, board, row, col, is_white):
        score = 0
        
        # Outpost: knight protected by pawn, can't be attacked by enemy pawns
        if self.is_outpost(board, row, col, is_white):
            score += self.KNIGHT_OUTPOST_BONUS

        # Mobility
        mobility = len(self.get_knight_moves(board, row, col))
        score += mobility * (self.MOBILITY_BONUS / 8)  # Normalize by max possible moves

        return score
    
    def evaluate_bishop(self, board, row, col, is_white):
        score = 0
        
        # Mobility
        mobility = len(self.get_bishop_moves(board, row, col))
        score += mobility * (self.MOBILITY_BONUS / 13)  # Normalize by max possible moves

        return score
    
    def evaluate_rook(self, board, row, col, is_white):
        score = 0
        
        # Check for open file
        open_file = True
        for r in range(8):
            piece = board.get_piece((r, col))
            if piece and piece.type == 'pawn':
                open_file = False
                break
        if open_file:
            score += self.ROOK_ON_OPEN_FILE_BONUS

        # Mobility
        mobility = len(self.get_rook_moves(board, row, col))
        score += mobility * (self.MOBILITY_BONUS / 14)  # Normalize by max possible moves

        return score
    
    def evaluate_king(self, board, row, col, is_white):
        score = 0
        
        # King safety (simplified)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.get_piece((new_row, new_col))
                    if piece and piece.color == ('white' if is_white else 'black'):
                        score += 5  # Bonus for friendly pieces near king

        return score

    def get_knight_moves(self, board, row, col):
        moves = []
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                moves.append((new_row, new_col))
        return moves

    def get_bishop_moves(self, board, row, col):
        moves = []
        for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                moves.append((new_row, new_col))
                new_row += dr
                new_col += dc
        return moves

    def get_rook_moves(self, board, row, col):
        moves = []
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                moves.append((new_row, new_col))
                new_row += dr
                new_col += dc
        return moves

    def is_outpost(self, board, row, col, is_white):
        # Check if knight is protected by friendly pawn
        pawn_row = row + (1 if is_white else -1)
        for dc in [-1, 1]:
            if 0 <= pawn_row < 8 and 0 <= col + dc < 8:
                piece = board.get_piece((pawn_row, col + dc))
                if piece and piece.type == 'pawn' and piece.color == ('white' if is_white else 'black'):
                    return True
        return False

    def is_in_check(self, board, is_white):
        return board.game_rules.is_in_check('white' if is_white else 'black')

    def is_checkmate(self, board, is_white):
        return board.game_rules.is_checkmate('white' if is_white else 'black')
    
    def evaluate_king_safety(self, board, king_pos, color):
        safety = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = king_pos[0] + dx, king_pos[1] + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    piece = board.get_piece((x, y))
                    if piece and piece.color == color:
                        safety += 5  # Friendly piece near king
        return safety

    def evaluate_pawn_structure(self, board, color):
        score = 0
        for col in range(8):
            pawns = 0
            for row in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.type == 'pawn' and piece.color == color:
                    pawns += 1
            if pawns > 1:
                score -= 5 * (pawns - 1)  # Penalty for doubled pawns
        return score

    def find_king(self, board, color):
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.type == 'king' and piece.color == color:
                    return (row, col)
        return None
    
    def board_to_string(self, board):
        s = []
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    s.append(piece.color[0].upper() if piece.color == 'white' else piece.color[0].lower())
                    s.append(piece.type[0])  # e.g. 'k' for king, 'q' for queen, etc
                else:
                    s.append('.')
        # add side to move
        s.append(board.game_state.get_current_turn()[0])
        return ''.join(s)