import pygame
from Bullet import Bullet

class CombatSystem:
    # 1. ADDED: 'sounds' must be in the parameters to receive it from main.py
    def __init__(self, car, sounds):
        self.car = car
        self.sounds = sounds
        self.bullets = pygame.sprite.Group()
        self.shoot_delay = 1000  # 0.4 seconds between shots
        self.last_shot_time = 0
        self.target_range = 500 

    def get_nearest_enemy(self, enemies):
        nearest_enemy = None
        min_dist = float('inf')
        
        for enemy in enemies:
            # Skip enemies that are already in their death animation
            if enemy.is_dead:
                continue
                
            dist_sq = (enemy.pos - self.car.pos).length_squared()
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest_enemy = enemy
        
        # Range check using standard length for accuracy
        if nearest_enemy and (nearest_enemy.pos - self.car.pos).length() < self.target_range:
            return nearest_enemy
        return None

    def auto_shoot(self, enemies):
        current_time = pygame.time.get_ticks()
        
        # 2. FIXED: Logic order. Check timer -> Find target -> Shoot
        if current_time - self.last_shot_time > self.shoot_delay:
            target = self.get_nearest_enemy(enemies)
            
            if target:
                new_bullet = Bullet(self.car.pos, target.pos)
                self.bullets.add(new_bullet)
                self.last_shot_time = current_time
                
                # 3. FIXED: This now triggers only when a bullet is actually fired
                self.sounds.play_sfx("shoot")

    def update(self, enemies):
        self.auto_shoot(enemies)
        self.bullets.update()
        
        for bullet in self.bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                # 4. FIXED: Don't damage zombies that are already dying
                if not enemy.is_dead:
                    enemy.health -= 25  
                    bullet.kill()
                    if enemy.health > 0:
                        # Zombie is hurt but still standing
                        self.sounds.play_sfx("hit")
                    else:
                        # Zombie health is 0, trigger death
                        enemy.die()
                        self.sounds.play_sfx("zombie_die")
                    if enemy.health <= 0:
                        enemy.die()    

    def draw(self, screen, camera):
        for bullet in self.bullets:
            screen.blit(bullet.image, camera.apply(bullet.rect))