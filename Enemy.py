import pygame


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, pos, image, bomb_explode_image):
        super().__init__()
        self.original = image
        self.image = self.original
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.forward = pygame.math.Vector2(0, -1)
        self.angle = 0
        self.engine_power = 0.30
        self.friction = 0.05
        self.max_speed = 1.7
        self.rot_speed = 2.2
        self.health = 100
        self.max_health = 100
        self.is_dead = False
        self.explode_timer = 0
        self.explode_timer_max = 24
        self.bomb_explode_image = bomb_explode_image

    def _is_driveable_at(self, world, pos):
        grid_x = int(pos.x // world.tile_size)
        grid_y = int(pos.y // world.tile_size)
        if 0 <= grid_x < 30 and 0 <= grid_y < 30:
            tile_id = world.map_data[grid_y][grid_x]
            return tile_id in world.road_tile_ids or tile_id == 0
        return False

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.explode_timer = self.explode_timer_max

    def update(self, target_pos, world, all_enemies):
        if self.is_dead:
            if self.explode_timer > 0:
                progress = 1 - (self.explode_timer / self.explode_timer_max)
                scale = 1.0 + (progress * 0.5)
                size = max(1, int(self.bomb_explode_image.get_width() * scale))
                self.image = pygame.transform.smoothscale(self.bomb_explode_image, (size, size))
                self.rect = self.image.get_rect(center=self.pos)
                self.explode_timer -= 1
            else:
                self.kill()
            return

        desired = pygame.math.Vector2(target_pos) - self.pos
        if desired.length() > 0:
            desired_dir = desired.normalize()
            ahead = self.pos + (self.forward * (world.tile_size * 0.6))
            if not self._is_driveable_at(world, ahead):
                best_dir = None
                best_angle = 999.0
                for ang in (-90, -60, -30, 30, 60, 90):
                    cand = self.forward.rotate(ang)
                    if self._is_driveable_at(world, self.pos + cand * (world.tile_size * 0.6)):
                        angle = abs(cand.angle_to(desired_dir))
                        if angle < best_angle:
                            best_angle = angle
                            best_dir = cand
                if best_dir is not None:
                    desired_dir = best_dir
                else:
                    desired_dir = self.forward.rotate(30)

            angle_to = self.forward.angle_to(desired_dir)
            if abs(angle_to) > 1:
                rot = max(-self.rot_speed, min(self.rot_speed, angle_to))
                self.angle -= rot
                self.forward.rotate_ip(rot)

        self.vel += self.forward * self.engine_power
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.vel *= (1 - self.friction)

        new_pos = self.pos + self.vel
        map_w = world.tile_size * 30
        map_h = world.tile_size * 30
        new_pos.x = max(0, min(map_w, new_pos.x))
        new_pos.y = max(0, min(map_h, new_pos.y))

        grid_x = int(new_pos.x // world.tile_size)
        grid_y = int(new_pos.y // world.tile_size)
        if 0 <= grid_x < 30 and 0 <= grid_y < 30:
            tile_id = world.map_data[grid_y][grid_x]
            if tile_id in world.road_tile_ids:
                self.pos = new_pos
            elif tile_id == 9:
                self.vel *= -0.5
            else:
                self.vel *= 0.8
                self.pos += self.vel
        else:
            self.vel *= -1

        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.resolve_overlap(all_enemies)

    def resolve_overlap(self, all_enemies):
        min_dist = 42
        for other in all_enemies:
            if other is self or other.is_dead:
                continue
            delta = self.pos - other.pos
            dist = delta.length()
            if dist == 0:
                delta = pygame.math.Vector2(1, 0)
                dist = 1
            if dist < min_dist:
                push = (min_dist - dist) * 0.5
                direction = delta.normalize()
                self.pos += direction * push
                other.pos -= direction * push
                self.rect.center = self.pos
                other.rect.center = other.pos

    def draw_health(self, screen, camera):
        if self.is_dead:
            return
        bar_width = 60
        bar_height = 6
        bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        screen_pos = camera.apply(self.rect)
        bar_rect.midbottom = screen_pos.midtop
        bar_rect.y -= 8
        pygame.draw.rect(screen, (0, 200, 0), bar_rect)
        damage_ratio = 1 - max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (200, 0, 0), (bar_rect.x, bar_rect.y, bar_width * damage_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), bar_rect, 1)
