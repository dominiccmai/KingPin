class ChessPiece:
    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type
        self.has_moved = False  # For pawns, kings, and rooks (castling)

    def copy(self):
        return ChessPiece(self.color, self.type)
    
    def __repr__(self):
        return f'{self.color[0]}{self.type[0]}'