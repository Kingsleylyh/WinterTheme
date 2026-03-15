import pygame
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(pos)
        direction = pygame.math.Vector2(target_pos) - self.pos
        
        if direction.length() > 0:
            self.vel = direction.normalize() * 10
        else:
            self.vel = pygame.math.Vector2(0, 0)
            
        self.lifetime = 100

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()