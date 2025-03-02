class ChessPiece:
    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type
        self.has_moved = False  # For pawns, kings, and rooks (castling)

    def __repr__(self):
        # 'knight' => 'n'
        if self.type == 'knight':
            return f"{self.color[0]}night"  # e.g. "bn" or "wn"
        elif self.type == 'king':
            return f"{self.color[0]}king"
        else:
            return f"{self.color[0]}{self.type[0]}"

    def copy(self):
        new_piece = ChessPiece(self.color, self.type)
        new_piece.has_moved = self.has_moved
        return new_piece