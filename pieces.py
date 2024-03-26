import config as cfg
import pygame

class Piece:
    def __init__(
            self, pos: tuple[int, int], color: tuple[int, int, int],
            color_name: str, icon: str, name: str
    ):
        self.pos = pos
        self.color = color
        self.rect = pygame.Rect(
            cfg.HORIZONTAL_BUFFER + pos[0] * cfg.TILE_SIZE,
            cfg.VERTICAL_BUFFER + pos[1] * cfg.TILE_SIZE,
            cfg.TILE_SIZE, cfg.TILE_SIZE
        )
        self.color = color
        self.color_name = color_name
        self.name = name
        self.font = pygame.font.Font(None, cfg.TILE_SIZE)
        self.icon = self.font.render(icon, True, self.color)
        self.is_selected = False
        self.has_moved = None
        self.is_captured = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_captured:
            return

        if not self.is_selected:
            screen.blit(self.icon, self.icon.get_rect(center=self.rect.center))
        else:
            pos = pygame.mouse.get_pos()
            screen.blit(self.icon, self.icon.get_rect(center=pos))

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        if not self.is_captured:
            return self.rect.collidepoint(pos)

    def toggle_selected(self) -> None:
        self.is_selected = not self.is_selected

    def capture(self):
        self.is_captured = True
        self.pos = None

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not (0 <= dest[0] < cfg.COLS and 0 <= dest[1] <= cfg.ROWS):
            return False

        for piece in pieces:
            if piece.pos == dest and piece.color == self.color:
                return False

        return True

    def check_diagonal(self, dest: tuple[int, int], pieces) -> bool:
        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if dx > 0:
            path_x = range(self.pos[0] + 1, dest[0])
        else:
            path_x = range(self.pos[0] - 1, dest[0], -1)

        if dy > 0:
            path_y = range(self.pos[1] + 1, dest[1])
        else:
            path_y = range(self.pos[1] - 1, dest[1], -1)

        for piece in pieces:
            for x, y in zip(path_x, path_y):
                if piece.pos == (x, y):
                    return False

        return True

    def check_horizontal(self, dest: tuple[int, int], pieces) -> bool:
        dx = dest[0] - self.pos[0]

        if dx > 0:
            path_x = range(self.pos[0] + 1, dest[0])
        else:
            path_x = range(self.pos[0] - 1, dest[0], -1)

        for piece in pieces:
            for x in path_x:
                if piece.pos == (x, self.pos[1]):
                    return False

        return True

    def check_vertical(self, dest: tuple[int, int], pieces) -> bool:
        dy = dest[1] - self.pos[1]

        if dy > 0:
            path_y = range(self.pos[1] + 1, dest[1])
        else:
            path_y = range(self.pos[1] - 1, dest[1], -1)

        for piece in pieces:
            for y in path_y:
                if piece.pos == (self.pos[0], y):
                    return False

        return True

    def move_piece(self, pos: tuple[int, int]) -> None:
        self.pos = pos
        self.rect = pygame.Rect(
            cfg.HORIZONTAL_BUFFER + self.pos[0] * cfg.TILE_SIZE,
            cfg.VERTICAL_BUFFER + self.pos[1] * cfg.TILE_SIZE,
            cfg.TILE_SIZE, cfg.TILE_SIZE
        )
        if self.has_moved is False:
            self.has_moved = True

    def __repr__(self) -> str:
        return f"{self.color_name} {self.name}"


class Pawn(Piece):
    def __init__(
            self, pos: tuple[int, int],
            color: tuple[int, int, int], color_name: str
    ):
        super().__init__(pos, color, color_name, cfg.PAWN_ICON, cfg.PAWN)

        self.has_moved = False

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        max_y = 1 if self.has_moved else 2

        if abs(dx) > 1 or abs(dy) > max_y:
            return False
        elif abs(dx) == 1 and abs(dy) != 1:
            return False
        elif abs(dy) == 2 and abs(dx) > 0:
            return False
        elif self.color == cfg.TOP_PLAYER_COLOR and dy < 0:  # no backwards
            return False
        elif self.color == cfg.BOTTOM_PLAYER_COLOR and dy > 0:  # only forwards
            return False
        elif abs(dx) == 1 and abs(dy) == 1:  # capture
            for piece in pieces:
                if piece.pos == dest:  # super() handles capturing own piece
                    return True
            return False

        # check if blocked
        if self.pos[1] < dest[1]:
            path = range(self.pos[1] + 1, dest[1] + 1)
        else:
            path = range(self.pos[1] - 1, dest[1] - 1, -1)

        for piece in pieces:
            for y in path:
                if piece.pos == (self.pos[0], y):
                    return False

        # TODO: Add other logic like en passant

        return True


class Rook(Piece):
    def __init__(
            self, pos: tuple[int, int],
            color: tuple[int, int, int], color_name: str
    ):
        super().__init__(pos, color, color_name, cfg.ROOK_ICON, cfg.ROOK)

        self.has_moved = False

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if abs(dx) > 0 and abs(dy) > 0:
            return False
        elif abs(dx) > 0:
            return self.check_horizontal(dest, pieces)
        else:
            return self.check_vertical(dest, pieces)


class Knight(Piece):
    def __init__(
            self, pos: tuple[int, int],
            color: tuple[int, int, int], color_name: str
    ):
        super().__init__(pos, color, color_name, cfg.KNIGHT_ICON, cfg.KNIGHT)

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if abs(dx) + abs(dy) != 3:
            return False
        elif abs(dx) == 3 or abs(dy) == 3:
            return False

        return True


class Bishop(Piece):
    def __init__(
            self, pos: tuple[int, int],
            color: tuple[int, int, int], color_name: str
    ):
        super().__init__(pos, color, color_name, cfg.BISHOP_ICON, cfg.BISHOP)

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if abs(dx) != abs(dy):
            return False

        return self.check_diagonal(dest, pieces)


class Queen(Piece):
    def __init__(
            self, pos: tuple[int, int],
            color: tuple[int, int, int], color_name: str
    ):
        super().__init__(pos, color, color_name, cfg.QUEEN_ICON, cfg.QUEEN)

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if 0 < abs(dx) != abs(dy) > 0:
            return False
        elif abs(dx) == abs(dy):
            return self.check_diagonal(dest, pieces)
        elif abs(dx) > 0:
            return self.check_horizontal(dest, pieces)
        else:
            return self.check_vertical(dest, pieces)


class King(Piece):
    def __init__(self, pos, color, color_name):
        super().__init__(pos, color, color_name, cfg.KING_ICON, cfg.KING)

        self.has_moved = False

    def is_legal_move(self, dest: tuple[int, int], pieces) -> bool:
        if not super().is_legal_move(dest, pieces):
            return False
        # TODO: add castling, checkmate logic, etc

        dx = dest[0] - self.pos[0]
        dy = dest[1] - self.pos[1]

        if abs(dx) > 1 or abs(dy) > 1:
            return False
        return True
