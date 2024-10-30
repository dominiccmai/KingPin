# board/move_validator.py

class MoveValidator:
    def __init__(self, board):
        self.board = board

    def is_valid_move(self, start, end):
        piece = self.board.get_piece(start)
        
        if not piece:
            return False
        
        end_piece = self.board.get_piece(end)
        if end_piece and end_piece.color == piece.color:
            return False
        
        if piece.type == 'pawn':
            return self._is_valid_pawn_move(start, end)
        elif piece.type == 'rook':
            return self._is_valid_rook_move(start, end)
        elif piece.type == 'knight':
            return self._is_valid_knight_move(start, end)
        elif piece.type == 'bishop':
            return self._is_valid_bishop_move(start, end)
        elif piece.type == 'queen':
            return self._is_valid_queen_move(start, end)
        elif piece.type == 'king':
            return self._is_valid_king_move(start, end)
        
        return False

    def _is_valid_pawn_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board.get_piece(start)
        
        # Determine direction based on color: White moves up (-1), Black moves down (+1)
        direction = -1 if piece.color == 'white' else 1
        
        # Moving forward (no capture)
        if start_col == end_col:
            if end_row == start_row + direction and self.board.get_piece(end) is None:
                return True
            if not piece.has_moved and end_row == start_row + 2 * direction:
                intermediate = (start_row + direction, start_col)
                if self.board.get_piece(end) is None and self.board.get_piece(intermediate) is None:
                    return True
        
        # Diagonal capture
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if self.board.get_piece(end) is not None and self.board.get_piece(end).color != piece.color:
                return True
            
            if self.board.last_double_pawn_move:
                last_row, last_col = self.board.last_double_pawn_move
                if last_row == start_row and last_col == end_col:
                    return True
        
        return False

    def _is_valid_rook_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if self.board.get_piece((start_row, col)):
                    return False
            return True
        elif start_col == end_col:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if self.board.get_piece((row, start_col)):
                    return False
            return True
        return False

    def _is_valid_knight_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _is_valid_bishop_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        if abs(end_row - start_row) == abs(end_col - start_col):
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            row, col = start_row + row_step, start_col + col_step
            while (row, col) != (end_row, end_col):
                if self.board.get_piece((row, col)):
                    return False
                row += row_step
                col += col_step
            return True
        return False

    def _is_valid_queen_move(self, start, end):
        return self._is_valid_rook_move(start, end) or self._is_valid_bishop_move(start, end)

    def _is_valid_king_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        if max(row_diff, col_diff) == 1:
            return True
            
        if not self.board.get_piece(start).has_moved and row_diff == 0 and abs(col_diff) == 2:
            return True
            
        return False