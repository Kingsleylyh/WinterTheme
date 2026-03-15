import pygame
import random
import math

class Buff(pygame.sprite.Sprite):
    def __init__(self, pos, buff_type):
        super().__init__()
        self.type = buff_type
        self.pos = pygame.math.Vector2(pos)
        
        # 1. Setup Colors
        colors = {"NITRO": (0, 255, 255), "REPAIR": (0, 255, 0), "SHIELD": (255, 215, 0)}
        self.color = colors.get(self.type, (255, 255, 255))
        
        # 2. OPTIMIZATION: Pre-render the image once in __init__
        # We use a larger surface (64x64) so the glow doesn't get cut off
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # Draw the "Glow" (Layered circles with decreasing alpha)
        for r in range(3):
            alpha = 70 - (r * 20) # Outer layers are more transparent
            pygame.draw.circle(self.image, (*self.color, alpha), (32, 32), 20 + (r * 5))
            
        # Draw the Core Buff
        pygame.draw.circle(self.image, self.color, (32, 32), 12)
        pygame.draw.circle(self.image, (255, 255, 255), (32, 32), 12, 2)
        
        # 3. Setup Physics/Animation Variables
        self.rect = self.image.get_rect(center=self.pos)
        self.bounce = random.uniform(0, 6.28) # Random starting position in the "wave"
        self.bounce_speed = 0.05             # FIXED: Re-adding the missing attribute

    def update(self):
        # Update the math phase
        self.bounce += self.bounce_speed
        
        # Move the rect based on the sine wave
        # We use the original pos.y so the offset doesn't "drift" away over time
        offset = math.sin(self.bounce) * 15
        self.rect.centery = self.pos.y + offset

    def apply(self, car):
        if self.type == "NITRO":
            car.nitro_charge = min(car.max_nitro, car.nitro_charge + 50)
        elif self.type == "REPAIR":
            car.health = min(car.max_health, car.health + 30)
        elif self.type == "SHIELD":
            car.health = car.max_health