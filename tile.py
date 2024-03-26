import config as cfg
import pygame

class Tile:
    def __init__(self, pos: tuple[int, int], color: tuple[int, int, int]):
        self.pos = pos
        self.color = color
        self.rect = pygame.Rect(
            cfg.HORIZONTAL_BUFFER + pos[0] * cfg.TILE_SIZE,
            cfg.VERTICAL_BUFFER + pos[1] * cfg.TILE_SIZE,
            cfg.TILE_SIZE, cfg.TILE_SIZE
        )

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
