import pygame
from settings import *

class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2()

    def update(self, target, world):
        # 1. Center the camera on the target (Santa)
        self.offset.x = target.rect.centerx - WIDTH // 2
        self.offset.y = target.rect.centery - HEIGHT // 2

        # 2. Calculate dynamic map boundaries
        max_x = (len(world.map_data[0]) * world.tile_size) - WIDTH
        max_y = (len(world.map_data) * world.tile_size) - HEIGHT

        # 3. Clamp camera inside map (ensures no black voids)
        self.offset.x = max(0, min(self.offset.x, max_x))
        self.offset.y = max(0, min(self.offset.y, max_y))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)