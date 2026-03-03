import pygame
from settings import *

class Car(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()

        self.original = pygame.image.load("assets/santa.png").convert_alpha()
        self.original = pygame.transform.rotozoom(self.original,0,0.10)
        self.image = self.original
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0,0)
        self.angle = 0

        self.acceleration = 0.4
        self.friction = 0.95
        self.max_speed = 6

    def update(self,world):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.angle += 3
        if keys[pygame.K_RIGHT]:
            self.angle -= 3

        if keys[pygame.K_UP]:
            direction = pygame.math.Vector2(0,-1).rotate(self.angle)
            self.vel += direction * self.acceleration

        if keys[pygame.K_DOWN]:
            direction = pygame.math.Vector2(0,-1).rotate(self.angle)
            self.vel -= direction * self.acceleration

        # limit speed
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        # friction
        self.vel *= self.friction

        new_pos = self.pos + self.vel

        # road check
        if world.is_road(new_pos.x,new_pos.y):
            self.pos = new_pos
        else:
            self.vel *= -0.3  # slight bounce

        self.rect.center = self.pos

        self.image = pygame.transform.rotozoom(self.original,self.angle,1)
        self.rect = self.image.get_rect(center=self.rect.center)