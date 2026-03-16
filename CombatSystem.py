import pygame
from Bullet import Bullet

class CombatSystem:
    def __init__(self, car, sounds):
        self.car = car
        self.sounds = sounds
        self.bullets = pygame.sprite.Group()
        self.shoot_delay = 400  # ms between shots
        self.last_shot_time = 0
        self.target_range = 200

    def get_nearest_enemy(self, enemies):
        nearest_enemy = None
        min_dist = float('inf')

        for enemy in enemies:
            if getattr(enemy, "is_dead", False):
                continue

            dist_sq = (enemy.pos - self.car.pos).length_squared()
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest_enemy = enemy

        if nearest_enemy and (nearest_enemy.pos - self.car.pos).length() < self.target_range:
            return nearest_enemy
        return None

    def try_shoot(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            target = self.get_nearest_enemy(enemies)
            if target:
                new_bullet = Bullet(self.car.pos, target.pos)
                self.bullets.add(new_bullet)
                self.last_shot_time = current_time
                self.sounds.play_sfx("shoot")

    def update(self, enemies):
        self.bullets.update()

        for bullet in self.bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                if getattr(enemy, "is_dead", False):
                    continue
                enemy.health -= 2 
                bullet.kill()
                if enemy.health > 0:
                    self.sounds.play_sfx("hit")
                else:
                    enemy.die()
                    self.sounds.play_sfx("zombie_die")

    def draw(self, screen, camera):
        for bullet in self.bullets:
            screen.blit(bullet.image, camera.apply(bullet.rect))
