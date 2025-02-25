import copy

from src.pieces.chess_piece import ChessPiece
from src.board.move_validator import MoveValidator
from src.board.game_state import GameState
from src.board.game_rules import GameRules

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.game_state = GameState()
        self.move_validator = MoveValidator(self)
        self.game_rules = GameRules(self)
        self._setup_board()
        self.move_history = []
        self.last_move = None
        self.last_double_pawn_move = None

    def _setup_board(self):
        # Set up pawns
        for col in range(8):
            self.board[6][col] = ChessPiece('white', 'pawn')  # White pawns on row 6
            self.board[1][col] = ChessPiece('black', 'pawn')  # Black pawns on row 1
        
        # Set up other pieces
        back_row = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col, piece in enumerate(back_row):
            self.board[7][col] = ChessPiece('white', piece)   # White pieces on row 7
            self.board[0][col] = ChessPiece('black', piece)   # Black pieces on row 0

    def print_board(self):
        print()
        for row in range(8):
            print(f"{8 - row} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                print(f"{str(piece) if piece else '..'} ", end="")
            print()
        print("  a  b  c  d  e  f  g  h")

        print("\nCaptures:")
        print(f"White: {', '.join(str(piece) for piece in self.game_state.white_captures)}")
        print(f"Black: {', '.join(str(piece) for piece in self.game_state.black_captures)}")
        print(f"\nCurrent turn: {self.game_state.get_current_turn().capitalize()}")
        print(f"Move count: {self.game_state.get_move_count()}")
        print()

        current_turn = self.game_state.get_current_turn()
        if self.game_rules.is_in_check(current_turn):
            print(f"{current_turn.capitalize()} is in check!")

    def move_piece(self, start, end, log=True):
        moving_piece = self.get_piece(start)
        
        if not moving_piece:
            if log:
                print(f"No piece at position {start}")
            return False

        current_turn = self.game_state.get_current_turn()
        if moving_piece.color != current_turn:
            if log:
                print(f"It's not {moving_piece.color}'s turn! Current turn: {current_turn}")
            return False

        if moving_piece.type == 'king' and abs(start[1] - end[1]) == 2:
            if not self._handle_castling(start, end):
                return False
            
        elif moving_piece.type == 'pawn' and abs(start[1] - end[1]) == 1 and self.get_piece(end) is None:
            if not self._handle_en_passant(start, end):
                return False

        # Check if the current player is in check
        if self.game_rules.is_in_check(current_turn):
            valid_moves = self.game_rules.get_valid_moves_in_check(current_turn)
            if (start, end) not in valid_moves:
                if log:
                    print(f"Invalid move: {current_turn} would be in check")
                return False

        if self.move_validator.is_valid_move(start, end):
            captured_piece = self.get_piece(end)

            if moving_piece.type == 'pawn' and abs(start[0] - end[0]) == 2:
                self.last_double_pawn_move = (end[0], end[1])
            else:
                self.last_double_pawn_move = None
            
            # Perform the move  
            self.board[end[0]][end[1]] = moving_piece
            self.board[start[0]][start[1]] = None
            moving_piece.has_moved = True

            if moving_piece.type == 'pawn' and (end[0] == 0 or end[0] == 7):
                self.board[end[0]][end[1]] = ChessPiece(moving_piece.color, 'queen')

            # Check if the move puts the current player in check
            if self.game_rules.is_in_check(current_turn):
                # Undo the move
                self.board[start[0]][start[1]] = moving_piece
                self.board[end[0]][end[1]] = captured_piece
                if log:
                    print(f"Invalid move: {current_turn} would be in check")
                return False
            
            if log:
                # Handle capture
                if captured_piece:
                    print(f"Captured: {captured_piece.color} {captured_piece.type}")
                    self.game_state.add_capture(captured_piece)

                print(f"Move successful: {moving_piece.color} {moving_piece.type} moved from {start} to {end}")

            self.move_history.append((start, end))
            
            # Switch turns
            self.game_state.switch_turn()

            return True
        else:
            if log:
                print(f"Invalid move: {start} to {end}")
            return False

    def _handle_castling(self, start, end):
        king = self.get_piece(start)
        if king.has_moved:
            return False

        # Determine rook position and new positions
        row = start[0]
        if end[1] > start[1]:  # Kingside castling
            rook_start = (row, 7)
            rook_end = (row, 5)
            path_cols = range(5, 7)
        else:  # Queenside castling
            rook_start = (row, 0)
            rook_end = (row, 3)
            path_cols = range(1, 4)

        rook = self.get_piece(rook_start)
        if not rook or rook.type != 'rook' or rook.has_moved:
            return False

        # Check path is clear
        for col in path_cols:
            if self.get_piece((row, col)) is not None:
                return False

        # Check if king passes through check
        king_color = king.color
        for col in [start[1], *path_cols]:
            if self.is_square_attacked((row, col), king_color):
                return False

        # Perform castling
        self.board[rook_end[0]][rook_end[1]] = rook
        self.board[rook_start[0]][rook_start[1]] = None
        rook.has_moved = True
        return True
    
    def _handle_en_passant(self, start, end):
        pawn = self.get_piece(start)
        if not self.last_double_pawn_move:
            return False

        # Check if this is a valid en passant capture
        last_row, last_col = self.last_double_pawn_move
        if last_row == start[0] and abs(last_col - start[1]) == 1:
            # Remove the captured pawn
            self.board[last_row][last_col] = None
            return True

        return False
    
    def get_piece(self, position):
        row, col = position
        piece = self.board[row][col]
        return piece
    
    def is_square_attacked(self, square, defending_color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color != defending_color:
                    if self.move_validator.is_valid_move((row, col), square):
                        return True
        return False
    
    def copy(self):
        new_board = ChessBoard()

        new_board.board = [
            [
                self.board[row][col].copy() if self.board[row][col] else None
                for col in range(8)
            ]
            for row in range(8)
        ]

        new_board.game_state = copy.deepcopy(self.game_state)
        
        from src.board.move_validator import MoveValidator
        from src.board.game_rules import GameRules
        new_board.move_validator = MoveValidator(new_board)
        new_board.game_rules = GameRules(new_board)

        new_board.move_history = copy.deepcopy(self.move_history)
        new_board.last_move = copy.deepcopy(self.last_move)
        new_board.last_double_pawn_move = copy.deepcopy(self.last_double_pawn_move)

        return new_board
    
    def push_move_in_place(self, start, end):

        # Gather info
        moved_piece = self.board[start[0]][start[1]]
        captured_piece = self.board[end[0]][end[1]]

        move_info = {
            'start': start,
            'end': end,
            'moved_piece': moved_piece,
            'captured_piece': captured_piece,
            'old_has_moved': moved_piece.has_moved,

            'old_turn': self.game_state.get_current_turn(),

            'old_move_count': self.game_state.get_move_count(),

            'old_last_double': self.last_double_pawn_move,
        }


        # Perform the move
        self.board[end[0]][end[1]] = moved_piece
        self.board[start[0]][start[1]] = None
        moved_piece.has_moved = True

        if moved_piece.type == 'pawn' and abs(start[0] - end[0]) == 2:
            self.last_double_pawn_move = (end[0], end[1])
        else:
            self.last_double_pawn_move = None

        # Handle pawn promotion if needed
        if moved_piece.type == 'pawn' and (end[0] == 0 or end[0] == 7):
            # We'll store the old type so we can undo it
            move_info['old_type'] = moved_piece.type
            moved_piece.type = 'queen'

        self.game_state.switch_turn()

        return move_info
    
    def pop_move_in_place(self, move_info):
        """
        Reverse the move stored in 'move_info'.
        """
        self.board[move_info['start'][0]][move_info['start'][1]] = move_info['moved_piece']
        self.board[move_info['end'][0]][move_info['end'][1]] = move_info['captured_piece']

        # Undo the move
        move_info['moved_piece'].has_moved = move_info['old_has_moved']

        if 'old_type' in move_info:
            move_info['moved_piece'].type = move_info['old_type']

        # Restore has_moved
        self.last_double_pawn_move = move_info['old_last_double']

        # Undo promotion if it happened
        self.game_state.current_turn = move_info['old_turn']
        self.game_state.move_count = move_info['old_move_count']