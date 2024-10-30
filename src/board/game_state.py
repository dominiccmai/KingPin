class GameState:
    def __init__(self):
        self.white_captures = []
        self.black_captures = []
        self.current_turn = 'white'
        self.move_count = 0

    def add_capture(self, piece):
        if piece.color == 'white':
            self.black_captures.append(piece)
        else:
            self.white_captures.append(piece)

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.move_count += 1

    def get_current_turn(self):
        return self.current_turn

    def get_move_count(self):
        return self.move_count