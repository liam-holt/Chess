import config as cfg
import pieces as p
import pygame
from tile import Tile

class Chess:
    def __init__(self):
        pygame.init()
        self.screen_size = (cfg.WIDTH, cfg.HEIGHT)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.tiles = [
            Tile(
                (col, row),
                cfg.BOARD_COLOR1 if (row + col) % 2 == 0 else cfg.BOARD_COLOR2
            )
            for col in range(cfg.COLS)
            for row in range(cfg.ROWS)
        ]
        self.tile_highlight = pygame.Surface((cfg.TILE_SIZE, cfg.TILE_SIZE))
        self.tile_highlight.set_alpha(100)
        self.tile_highlight.fill(cfg.HIGHLIGHT_COLOR)
        self.top_player_pieces = self.initialize_pieces(is_top_player=True)
        self.bottom_player_pieces = self.initialize_pieces(is_top_player=False)
        self.pieces = self.top_player_pieces + self.bottom_player_pieces
        self.selected_piece = None
        self.running = True

    def initialize_pieces(self, is_top_player: bool) -> list[p.Piece]:
        pawn_row = cfg.TOP_PAWN_ROW if is_top_player else cfg.BOTTOM_PAWN_ROW
        main_row = cfg.TOP_MAIN_ROW if is_top_player else cfg.BOTTOM_MAIN_ROW
        color = cfg.TOP_PLAYER_COLOR if is_top_player else cfg.BOTTOM_PLAYER_COLOR
        player = cfg.TOP_PLAYER if is_top_player else cfg.BOTTOM_PLAYER

        pawns = [
            p.Pawn((col, pawn_row), color, player)
            for col in range(cfg.COLS)
        ]
        rooks = [
            p.Rook((col, main_row), color, player)
            for col in cfg.ROOK_COLS
        ]
        knights = [
            p.Knight((col, main_row), color, player)
            for col in cfg.KNIGHT_COLS
        ]
        bishops = [
            p.Bishop((col, main_row), color, player)
            for col in cfg.BISHOP_COLS
        ]
        queen = [p.Queen((cfg.QUEEN_COL, main_row), color, player)]
        king = [p.King((cfg.KING_COL, main_row), color, player)]

        pieces = pawns + rooks + knights + bishops + queen + king

        return pieces

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown()

    def handle_mousebuttondown(self) -> None:
        pos = pygame.mouse.get_pos()
        if self.selected_piece is None:
            self.select_piece(pos)
        else:
            self.move_piece(pos)

    def select_piece(self, pos: tuple[int, int]) -> None:
        for piece in self.pieces:
            if piece.is_clicked(pos):
                self.selected_piece = piece
                piece.toggle_selected()
                break

    def move_piece(self, pos: tuple[int, int]) -> None:
        dest = self.get_tile_pos(pos)
        if dest is not None:
            if self.selected_piece.is_legal_move(dest, self.pieces):
                if isinstance(self.selected_piece, p.King):
                    self.check_castle_rook(self.selected_piece.pos, dest)
                self.selected_piece.move_piece(dest)

                for piece in self.pieces:
                    if piece.pos == dest \
                            and piece.color != self.selected_piece.color:
                        piece.capture()
                        break

                for piece in self.pieces:
                    if isinstance(piece, p.King):
                        piece.is_in_check = self.is_in_check(piece.color)


        self.selected_piece.toggle_selected()
        self.selected_piece = None

    def check_castle_rook(self, pos: tuple[int, int], dest: tuple[int, int]) -> None:
        dx = dest[0] - pos[0]
        dy = dest[1] - pos[1]
        if abs(dx) != 2 or abs(dy) != 0:
            return

        rook_x = cfg.ROOK_COLS[0] if dx < 0 else cfg.ROOK_COLS[1]
        rook_pos = (rook_x, pos[1])

        for piece in self.pieces:
            if piece.pos == rook_pos and isinstance(piece, p.Rook):
                piece.move_piece((pos[0] + dx // 2, pos[1]))
                break

    def is_in_check(self, color: tuple[int, int, int]) -> bool:
        king_pos = None
        for piece in self.pieces:
            if isinstance(piece, p.King) and piece.color == color:
                king_pos = piece.pos
                break

        for piece in self.pieces:
            if piece.color != color and piece.is_legal_move(king_pos, self.pieces):
                return True

        return False

    def is_in_checkmate(self, color: tuple[int, int, int]) -> bool:
        if not self.is_in_check(color):
            return False

        for piece in self.pieces:
            if piece.color == color:
                for tile in self.tiles:
                    if piece.is_legal_move(tile.pos, self.pieces) \
                            and not self.would_be_in_check(piece, tile.pos):
                        return False

        return True

    def would_be_in_check(self, piece: p.Piece, dest: tuple[int, int]) -> bool:
        initial_pos = piece.pos
        captured_piece = None
        captured_piece_pos = None

        for p in self.pieces:
            if p.pos == dest:
                captured_piece = p
                captured_piece_pos = p.pos
                p.capture()

        piece.move_piece(dest)
        check = self.is_in_check(piece.color)

        piece.move_piece(initial_pos)
        if captured_piece is not None:
            captured_piece.is_captured = False
            captured_piece.pos = captured_piece_pos

        return check

    def get_tile_pos(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        for tile in self.tiles:
            if tile.is_clicked(pos):
                return tile.pos
        return None

    def update(self):
        dt = self.clock.tick(60)

        if self.is_in_checkmate(cfg.TOP_PLAYER_COLOR):
            pass
        elif self.is_in_checkmate(cfg.BOTTOM_PLAYER_COLOR):
            pass

    def draw(self):
        self.screen.fill(cfg.BACKGROUND_COLOR)
        self.draw_board()
        self.draw_pieces()
        pygame.display.flip()

    def draw_board(self):
        for tile in self.tiles:
            tile.draw(self.screen)
            if self.selected_piece is not None and \
                    self.selected_piece.is_legal_move(tile.pos, self.pieces):
                self.screen.blit(self.tile_highlight, tile.rect)

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw(self.screen)


if __name__ == '__main__':
    game = Chess()
    game.run()
