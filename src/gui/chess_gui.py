import pygame
import math
import os
import threading
import time
from src.board.chess_board import ChessBoard
from src.utils.helpers import parse_position
from src.chess_ai import ChessAI


class ChessGUI:
    def __init__(self, board_size=800):
        pygame.init()
        pygame.mixer.init() 
        self.board_size = board_size
        self.square_size = board_size // 8
        self.screen = pygame.display.set_mode((board_size, board_size + 50))
        pygame.display.set_caption("Chess Game")
        self.chess_board = ChessBoard()
        self.highlighted_square = None 
        self.last_dragged_piece = None
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT = (255, 255, 0, 128)
        self.HIGHLIGHT = (255, 255, 0, 128) 
        self.VALID_MOVE = (128, 128, 128, 180) 
        self.ARROW_COLOR = (0, 200, 0, 200)
        self.CAPTURABLE_PIECE = (255, 0, 0, 100)
        self.MENU_BG = (200, 200, 200)
        self.BUTTON_COLOR = (150, 150, 150)
        self.BUTTON_HOVER = (180, 180, 180)

        # Load assets
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.pieces_images = self.load_pieces()
        self.move_sound = pygame.mixer.Sound(os.path.join(self.base_path, 'assets', 'sounds', 'chess_move.wav'))
        self.capture_sound = pygame.mixer.Sound(os.path.join(self.base_path, 'assets', 'sounds', 'chess_capture.wav'))

        # Mouse interaction variables
        self.selected_piece = None
        self.dragging = False
        self.drag_pos = (0, 0)
        self.valid_moves = []
        self.arrow_start = None
        self.arrows = []

        # Menu buttons
        self.buttons = [
            {'text': 'Undo', 'rect': pygame.Rect(10, board_size + 10, 100, 30)},
            {'text': 'Redo', 'rect': pygame.Rect(120, board_size + 10, 100, 30)},
            {'text': 'Restart', 'rect': pygame.Rect(230, board_size + 10, 100, 30)}
        ]

        self.move_history = [self.chess_board.copy()]
        self.current_move = 0

        self.ai = ChessAI('black')  
        self.ai_thinking = False
        self.ai_move = None

    def load_pieces(self):
        pieces = {}
        for color in ['white', 'black']:
            for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
                image_path = os.path.join(
                    self.base_path, 'assets', 'pieces', f'{color}_{piece}.png'
                )
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (self.square_size, self.square_size))
                pieces[f'{color}_{piece}'] = image
        return pieces

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(self.screen, color, (col * self.square_size, row * self.square_size, self.square_size, self.square_size))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.get_piece((row, col))
                if piece and (row, col) != self.selected_piece:
                    image = self.pieces_images[f'{piece.color}_{piece.type}']
                    self.screen.blit(image, (col * self.square_size, row * self.square_size))
        
        if self.dragging and self.selected_piece:
            piece = self.chess_board.get_piece(self.selected_piece)
            image = self.pieces_images[f'{piece.color}_{piece.type}']
            self.screen.blit(image, (self.drag_pos[0] - self.square_size // 2, self.drag_pos[1] - self.square_size // 2))

    def draw_menu(self):
        pygame.draw.rect(self.screen, self.MENU_BG, (0, self.board_size, self.board_size, 50))
        for button in self.buttons:
            color = self.BUTTON_HOVER if button['rect'].collidepoint(pygame.mouse.get_pos()) else self.BUTTON_COLOR
            pygame.draw.rect(self.screen, color, button['rect'])
            font = pygame.font.Font(None, 24)
            text = font.render(button['text'], True, self.BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

    def handle_menu_click(self, pos):
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if button['text'] == 'Undo':
                    self.undo_move()
                elif button['text'] == 'Redo':
                    self.redo_move()
                elif button['text'] == 'Restart':
                    self.restart_game()
                    return True

    def highlight_square(self, pos):
        if pos:
            highlight_surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            highlight_surf.fill(self.HIGHLIGHT)
            self.screen.blit(highlight_surf, (pos[1] * self.square_size, pos[0] * self.square_size))

    def get_square_under_mouse(self):
        x, y = pygame.mouse.get_pos()
        return (y // self.square_size, x // self.square_size)
    
    def highlight_valid_moves(self):
        for move in self.valid_moves:
            center = (move[1] * self.square_size + self.square_size // 2, 
                      move[0] * self.square_size + self.square_size // 2)
            
            if self.chess_board.get_piece(move):
                pygame.draw.circle(self.screen, self.CAPTURABLE_PIECE, center, self.square_size // 2)
            else:
                pygame.draw.circle(self.screen, self.VALID_MOVE, center, self.square_size // 6)
            
    def draw_arrows(self):
        for start, end in self.arrows:
            start_pos = (start[1] * self.square_size + self.square_size // 2, 
                         start[0] * self.square_size + self.square_size // 2)
            end_pos = (end[1] * self.square_size + self.square_size // 2, 
                       end[0] * self.square_size + self.square_size // 2)
            
            # Draw L-shaped arrows for knight moves
            if abs(start[0] - end[0]) == 2 and abs(start[1] - end[1]) == 1 or \
               abs(start[0] - end[0]) == 1 and abs(start[1] - end[1]) == 2:
                mid_pos = (start_pos[0], end_pos[1]) if abs(start[0] - end[0]) == 2 else (end_pos[0], start_pos[1])
                pygame.draw.line(self.screen, self.ARROW_COLOR, start_pos, mid_pos, width=10)
                pygame.draw.line(self.screen, self.ARROW_COLOR, mid_pos, end_pos, width=10)
            else:
                pygame.draw.line(self.screen, self.ARROW_COLOR, start_pos, end_pos, width=10)
            
            # Draw arrowhead
            angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
            pygame.draw.polygon(self.screen, self.ARROW_COLOR, [
                end_pos,
                (end_pos[0] - 30 * math.cos(angle - math.pi/6),
                 end_pos[1] - 30 * math.sin(angle - math.pi/6)),
                (end_pos[0] - 30 * math.cos(angle + math.pi/6),
                 end_pos[1] - 30 * math.sin(angle + math.pi/6))
            ])


    def get_valid_moves(self, pos):
        piece = self.chess_board.get_piece(pos)
        if piece and piece.color == self.chess_board.game_state.get_current_turn():
            return [(r, c) for r in range(8) for c in range(8) 
                    if self.chess_board.move_validator.is_valid_move(pos, (r, c))]
        return []
    
    def check_game_over(self):
        current_turn = self.chess_board.game_state.get_current_turn()
        if self.chess_board.game_rules.is_checkmate(current_turn):
            winner = "Black" if current_turn == "white" else "White"
            print(f"Checkmate! {winner} wins!")
            return "CHECKMATE"
        elif self.chess_board.game_rules.is_stalemate(current_turn):
            print("Stalemate! The game is a draw.")
            return "STALEMATE"
        return None
    
    def undo_move(self):
        if self.current_move > 0:
            self.current_move -= 1
            self.chess_board = self.move_history[self.current_move].copy()
            self.arrows = []
            print(f"Undo move. Current move: {self.current_move}")

    def redo_move(self):
        if self.current_move < len(self.move_history) - 1:
            self.current_move += 1
            self.chess_board = self.move_history[self.current_move].copy()
            self.arrows = []
            print(f"Redo move. Current move: {self.current_move}")

    def restart_game(self):
        self.chess_board = ChessBoard()
        self.move_history = [self.chess_board.copy()]
        self.current_move = 0
        self.arrows = []
        self.selected_piece = None
        self.dragging = False
        self.valid_moves = []

    def draw_game_over_message(self, game_state):
        font = pygame.font.Font(None, 74)
        if game_state == "CHECKMATE":
            winner = "Black" if self.chess_board.game_state.get_current_turn() == "white" else "White"
            text = font.render(f"{winner} wins by checkmate!", True, (255, 0, 0))
        else:
            text = font.render("Stalemate! It's a draw.", True, (0, 0, 255))
        
        text_rect = text.get_rect(center=(self.board_size // 2, self.board_size // 2))
        self.screen.blit(text, text_rect)

    def ai_think(self):
        self.ai_move = self.ai.get_best_move(self.chess_board, max_time=3)
        self.ai_thinking = False

    def run(self):
        running = True
        game_over = False
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.ai_thinking = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        if mouse_pos[1] > self.board_size:
                            if self.handle_menu_click(mouse_pos):
                                game_over = False 
                        elif not game_over and not self.ai_thinking:
                            self.arrows = []  
                            click_pos = self.get_square_under_mouse()
                            piece = self.chess_board.get_piece(click_pos)
                            if piece and piece.color == self.chess_board.game_state.get_current_turn():
                                self.selected_piece = click_pos
                                self.dragging = True
                                self.valid_moves = self.get_valid_moves(click_pos)
                    elif event.button == 3:  # Right mouse button
                        self.arrow_start = self.get_square_under_mouse()
                elif event.type == pygame.MOUSEBUTTONUP and not game_over:
                    if event.button == 1 and self.dragging:
                        end_pos = self.get_square_under_mouse()
                        if self.selected_piece != end_pos:
                            captured_piece = self.chess_board.get_piece(end_pos)
                            move_made = self.chess_board.move_piece(self.selected_piece, end_pos)
                            if move_made:
                                if captured_piece:
                                    self.capture_sound.play()  # Play capture sound
                                else:
                                    self.move_sound.play()  # Play move sound
                                self.current_move += 1
                                self.move_history = self.move_history[:self.current_move]
                                self.move_history.append(self.chess_board.copy())

                                game_state = self.check_game_over()
                                if game_state:
                                    game_over = True
                                elif self.chess_board.game_state.get_current_turn() == 'black':
                                    self.ai_thinking = True
                                    threading.Thread(target=self.ai_think, daemon=True).start()

                        self.selected_piece = None
                        self.dragging = False
                        self.valid_moves = []
                    elif event.button == 3 and self.arrow_start:
                        arrow_end = self.get_square_under_mouse()
                        if self.arrow_start != arrow_end:
                            self.arrows.append((self.arrow_start, arrow_end))
                        self.arrow_start = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.drag_pos = event.pos

            self.screen.fill(self.WHITE)
            self.draw_board()
            self.highlight_valid_moves()
            self.draw_pieces()
            if self.selected_piece:
                self.highlight_square(self.selected_piece)
            self.draw_arrows()
            self.draw_menu()

            if game_over:
                self.draw_game_over_message(game_state)

            pygame.display.flip()

            if not game_over and self.ai_move:
                self.chess_board.move_piece(self.ai_move[0], self.ai_move[1])
                self.move_sound.play()
                print(f"AI Move: {self.ai_move[0]} to {self.ai_move[1]}")
                self.current_move += 1
                self.move_history = self.move_history[:self.current_move]
                self.move_history.append(self.chess_board.copy())
                
                game_state = self.check_game_over()
                if game_state:
                    game_over = True
                
                self.ai_move = None
                self.ai_thinking = False

            pygame.display.flip()
            clock.tick(60)

        self.ai_thinking = False
        pygame.quit()

if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()