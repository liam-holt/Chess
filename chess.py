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
                self.selected_piece.move_piece(dest)

                for piece in self.pieces:
                    if piece.pos == dest \
                            and piece.color != self.selected_piece.color:
                        piece.capture()
                        break

        self.selected_piece.toggle_selected()
        self.selected_piece = None

    def get_tile_pos(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        for tile in self.tiles:
            if tile.is_clicked(pos):
                return tile.pos
        return None

    def update(self):
        dt = self.clock.tick(60)

    def draw(self):
        self.screen.fill(cfg.BACKGROUND_COLOR)
        self.draw_board()
        self.draw_pieces()
        pygame.display.flip()

    def draw_board(self):
        for tile in self.tiles:
            tile.draw(self.screen)

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw(self.screen)


if __name__ == '__main__':
    game = Chess()
    game.run()
