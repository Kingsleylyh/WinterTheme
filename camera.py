import pygame
from settings import *

class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2()

    def update(self, target):
        self.offset.x = target.rect.centerx - WIDTH // 2
        self.offset.y = target.rect.centery - HEIGHT // 2

        # Clamp camera inside map
        self.offset.x = max(0, min(self.offset.x, MAP_WIDTH - WIDTH))
        self.offset.y = max(0, min(self.offset.y, MAP_HEIGHT - HEIGHT))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)