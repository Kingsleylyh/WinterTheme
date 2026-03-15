import pygame, random
from settings import *

class Snow:
    def __init__(self):
        self.particles = []

    def update(self):
        # CS Tip: Use a timer or frame count instead of random.random 
        # if you want the snow density to be perfectly consistent.
        if random.random() < 0.5:
            self.particles.append([
                random.randint(0, WIDTH),
                0,
                random.randint(2, 4)
            ])

        for p in self.particles:
            p[1] += p[2]

        self.particles = [p for p in self.particles if p[1] < HEIGHT]
    
    def clear(self):
        self.particles = []

    def draw(self, screen):
        for p in self.particles:
            pygame.draw.circle(screen, (255, 255, 255), (p[0], p[1]), 2)

class SmokeParticle:
    def __init__(self, pos, color, life):
        self.pos = pygame.math.Vector2(pos)
        self.color = color
        self.life = life
        self.max_life = life
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.size = random.randint(4, 8)

    def update(self):
        self.pos += self.vel
        self.life -= 1
        return self.life > 0

    def draw(self, screen, camera):
        progression = self.life / self.max_life
        alpha = int(progression * 150)
        current_size = int(self.size * (2 - progression))
        
        # Performance Tip: If you have hundreds of particles, 
        # draw directly to the screen using a circle if alpha isn't 100% necessary,
        # OR cache the surface if the size doesn't change every frame.
        surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (current_size, current_size), current_size)
        
        rect = surf.get_rect(center=self.pos)
        screen.blit(surf, camera.apply(rect))

class TrailParticle:
    def __init__(self, pos, color, life, angle):
        self.pos = pygame.math.Vector2(pos)
        self.color = color
        self.life = life 
        self.max_life = life
        self.angle = angle

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen, camera):
        alpha = int((self.life / self.max_life) * 255)
        # CS Tip: Pre-calculating a few rotated surfaces and picking one 
        # is faster than transform.rotate() every frame.
        surf = pygame.Surface((4, 8), pygame.SRCALPHA) 
        surf.fill((*self.color, alpha))
        
        rotated_surf = pygame.transform.rotate(surf, self.angle)
        rect = rotated_surf.get_rect(center=self.pos)
        screen.blit(rotated_surf, camera.apply(rect))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add_particle(self, pos, color, life, angle=0):
        self.particles.append(TrailParticle(pos, color, life, angle))

    def add_smoke(self, pos, color, life):
        self.particles.append(SmokeParticle(pos, color, life))

    def update(self):
        # List comprehension is great here (O(n) complexity)
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen, camera):
        for p in self.particles:
            p.draw(screen, camera)
            
    def clear(self):
        self.particles = []