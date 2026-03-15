import pygame
import random
from settings import *

class Car(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # 1. Load and scale the original once
        raw_image = pygame.image.load("assets/santa.png").convert_alpha()
        # smoothscale provides better quality for the 0.3x reduction
        self.original = pygame.transform.smoothscale(
            raw_image, 
            (int(raw_image.get_width() * 0.30), int(raw_image.get_height() * 0.3))
        )
        
        self.image = self.original
        self.rect = self.image.get_rect(center=pos)
        
        # Vectors & Physics
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.accel = pygame.math.Vector2(0, 0)
        self.forward = pygame.math.Vector2(0, -1)
        self.smooth_speed = 0.0
        self.angle = 0
        
        # Base Constants
        self.engine_power = 0.3
        self.friction = 0.05
        self.grip = 0.15
        self.max_speed = 6
        
        # Health & Nitro System
        self.health = 100
        self.max_health = 100
        self.nitro_charge = 100.0  # Percentage 0-100
        self.max_nitro = 100.0
        self.is_boosting = False

    def update(self, world, particle_manager):
        # Time-based delta could be used here; for now, we use frame-based logic
        dt = 1 # Assuming consistent 60FPS; otherwise use clock.get_time() / 1000
        
        keys = pygame.key.get_pressed()
        self.accel = pygame.math.Vector2(0, 0)
        speed = self.vel.length()
        
        # --- 1. NITRO & BOOST LOGIC ---
        self.is_boosting = False
        current_power = self.engine_power
        current_max_speed = self.max_speed

        # Trigger Nitro with Left Shift
        if keys[pygame.K_LSHIFT] and self.nitro_charge > 0 and keys[pygame.K_w]:
            self.is_boosting = True
            current_power = 0.7        # Significant increase in acceleration
            current_max_speed = 10     # Temporarily higher speed cap
            self.nitro_charge -= 0.8   # Consumption rate per frame
        else:
            # Natural regeneration when not boosting
            if self.nitro_charge < self.max_nitro:
                self.nitro_charge += 0.2

        # --- 2. MOVEMENT INPUTS ---
        if keys[pygame.K_w]:
            self.accel = self.forward * current_power 
        elif keys[pygame.K_s]:
            self.accel = -self.forward * (self.engine_power * 0.5)

        # Drift Logic
        is_drifting = keys[pygame.K_SPACE]
        if is_drifting:
            current_max_speed = self.max_speed * 0.7
        current_grip = 0.03 if is_drifting else self.grip
        rot_mult = 1.6 if is_drifting else 1.0

        # --- 3. ROTATION LOGIC ---
        rot_speed = (3.5 * rot_mult) * min(speed / 4.0, 1.2) if speed > 0.1 else 0
        
        if keys[pygame.K_a]:
            self.angle += rot_speed
            self.forward.rotate_ip(-rot_speed)
        if keys[pygame.K_d]:
            self.angle -= rot_speed
            self.forward.rotate_ip(rot_speed)

        # --- 4. PHYSICS PROCESSING ---
        if speed > 0:
            # Lateral friction (prevents infinite sliding)
            side_vel = self.vel - (self.forward * self.vel.dot(self.forward))
            self.vel -= side_vel * current_grip
        
        self.vel += self.accel
        self.vel *= (1 - self.friction)
        
        # Apply current max speed cap (Normal vs Nitro)
        if self.vel.length() > current_max_speed: 
            self.vel.scale_to_length(current_max_speed)

        # --- 5. COLLISION & EXECUTION ---
        new_pos = self.pos + self.vel
        grid_x = int(new_pos.x // world.tile_size)
        grid_y = int(new_pos.y // world.tile_size)
        
        if 0 <= grid_x < 30 and 0 <= grid_y < 30:
            tile_id = world.map_data[grid_y][grid_x]
            
            if tile_id in world.road_tile_ids:
                self.pos = new_pos
            elif tile_id == 9:
                # Building Hit
                self.vel *= -0.5 
                self.health -= 0.5
            else:
                # Grass Friction
                self.vel *= 0.8
                self.pos += self.vel
        else:
            # Map Boundary
            self.vel *= -1 

        # --- 6. VISUAL RENDERING ---
        target_speed = self.vel.length()
        self.smooth_speed += (target_speed - self.smooth_speed) * 0.1
        
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

        # --- 7. PARTICLES ---
        if speed > 0.5:
            # Calculate offsets for tire/exhaust locations
            side_vec = pygame.math.Vector2(-self.forward.y, self.forward.x) * 12
            back_vec = self.forward * -15
            left_t = self.pos + back_vec - side_vec
            right_t = self.pos + back_vec + side_vec
            center_exhaust = self.pos + (self.forward * -20)

            if self.is_boosting:
                # COMBUSTION: Blue heat with orange sparks
                # Large blue puffs
                particle_manager.add_smoke(center_exhaust, (0, 191, 255), 20)
                # Random sparks
                if random.random() < 0.4:
                    particle_manager.add_smoke(center_exhaust + (random.uniform(-5,5), random.uniform(-5,5)), (255, 140, 0), 10)
            
            elif is_drifting and speed > 2:
                # DRIFT: Puffy dark smoke
                particle_manager.add_smoke(left_t, (100, 100, 100), 40)
                particle_manager.add_smoke(right_t, (100, 100, 100), 40)
            else:
                # NORMAL: Standard snow trails
                particle_manager.add_particle(left_t, (220, 230, 255), 60, self.angle)
                particle_manager.add_particle(right_t, (220, 230, 255), 60, self.angle)