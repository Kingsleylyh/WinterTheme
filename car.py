import pygame
from settings import *

class Car(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original = pygame.image.load("assets/santa.png").convert_alpha()
        self.original = pygame.transform.rotozoom(self.original, 0, 0.10)
        self.image = self.original
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.forward = pygame.math.Vector2(0, -1)
        self.direction = 0
        self.rotation_speed = 2.2
        self.acceleration = 0.25       # slightly up from 0.18
        self.friction = 0.90           # slightly up from 0.80 — a bit more glide
        self.max_speed = 5             # slightly up from 4

    def set_rotation(self):
        speed = self.vel.length()
        effective_rotation = self.rotation_speed * min(speed / 2.0, 1.0)
        if self.direction == 1:
            self.angle -= effective_rotation
        if self.direction == -1:
            self.angle += effective_rotation
        self.image = pygame.transform.rotozoom(self.original, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_rotation(self):
        speed = self.vel.length()
        effective_rotation = self.rotation_speed * min(speed / 2.0, 1.0)
        if self.direction == 1:
            self.forward.rotate_ip(effective_rotation)
        if self.direction == -1:
            self.forward.rotate_ip(-effective_rotation)

    def update(self, world):
        keys = pygame.key.get_pressed()

        self.direction = 0
        if keys[pygame.K_LEFT]:
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.direction = 1

        self.set_rotation()
        self.get_rotation()

        if keys[pygame.K_UP]:
            self.vel += self.forward * self.acceleration
        elif keys[pygame.K_DOWN]:
            self.vel -= self.forward * (self.acceleration * 0.6)

        # Lateral damping — slightly reduced to allow more drift
        if self.vel.length() > 0.1:
            forward_speed = self.vel.dot(self.forward)
            forward_component = self.forward * forward_speed
            lateral_component = self.vel - forward_component
            self.vel -= lateral_component * 0.18   # was 0.25 — more drift

        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        self.vel *= self.friction

        if self.vel.length() < 0.05:
            self.vel = pygame.math.Vector2(0, 0)

        # Wall sliding road check
        new_pos = self.pos + self.vel
        can_move_x = world.is_road(new_pos.x, self.pos.y)
        can_move_y = world.is_road(self.pos.x, new_pos.y)

        if world.is_road(new_pos.x, new_pos.y):
            self.pos = new_pos
        elif can_move_x:
            self.pos.x = new_pos.x
            self.vel.y *= -0.2
        elif can_move_y:
            self.pos.y = new_pos.y
            self.vel.x *= -0.2
        else:
            self.vel *= 0.0

        self.rect.center = self.pos