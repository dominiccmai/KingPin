# board/game_rules.py

class GameRules:
    def __init__(self, board):
        self.board = board

    def is_in_check(self, color):
        king_position = self._find_king(color)
        if not king_position:
            return False  # This shouldn't happen in a normal game

        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                if piece and piece.color == opponent_color:
                    if self.board.move_validator.is_valid_move((row, col), king_position):
                        return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        # Check all possible moves for all pieces of the current player
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board.get_piece((start_row, start_col))
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.board.move_validator.is_valid_move((start_row, start_col), (end_row, end_col)):
                                # Try the move
                                original_end_piece = self.board.get_piece((end_row, end_col))
                                self.board.board[end_row][end_col] = piece
                                self.board.board[start_row][start_col] = None

                                # Check if the king is still in check after the move
                                still_in_check = self.is_in_check(color)

                                # Undo the move
                                self.board.board[start_row][start_col] = piece
                                self.board.board[end_row][end_col] = original_end_piece

                                if not still_in_check:
                                    return False  # Found a valid move to escape check
        return True  # No valid moves to escape check
    
    def get_valid_moves_in_check(self, color):
        valid_moves = []
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board.get_piece((start_row, start_col))
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.board.move_validator.is_valid_move((start_row, start_col), (end_row, end_col)):
                                original_end_piece = self.board.get_piece((end_row, end_col))
                                
                                # Try the move
                                self.board.board[end_row][end_col] = piece
                                self.board.board[start_row][start_col] = None

                                # Check if the king is still in check after the move
                                still_in_check = self.is_in_check(color)

                                # Undo the move
                                self.board.board[start_row][start_col] = piece
                                self.board.board[end_row][end_col] = original_end_piece

                                if not still_in_check:
                                    valid_moves.append(((start_row, start_col), (end_row, end_col)))
        return valid_moves

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        # Check if the player has any legal moves
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board.get_piece((start_row, start_col))
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.board.move_validator.is_valid_move((start_row, start_col), (end_row, end_col)):

                                original_end_piece = self.board.get_piece((end_row, end_col))
                                self.board.board[end_row][end_col] = piece
                                self.board.board[start_row][start_col] = None

                                in_check = self.is_in_check(color)

                                self.board.board[start_row][start_col] = piece
                                self.board.board[end_row][end_col] = original_end_piece

                                if not in_check:
                                    return False  # Found a legal move
        return True  

    def _find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                if piece and piece.type == 'king' and piece.color == color:
                    return (row, col)
        return None