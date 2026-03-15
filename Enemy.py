from SpriteSheet import SpriteSheet
import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # 1. Initialize core attributes first
        self.pos = pygame.math.Vector2(pos)
        self.speed = 2.5
        self.health = 100
        self.max_health = 100
        self.is_dead = False
        self.state = "idle"
        self.frame_index = 0
        
        # 2. Setup Animations
        self.animations = {
            "idle": {"sheet": SpriteSheet("assets/enemy/idle.png", 6), "count": 6},
            "walk": {"sheet": SpriteSheet("assets/enemy/walk.png", 6), "count": 6},
            "attack": {"sheet": SpriteSheet("assets/enemy/attack.png", 4), "count": 4},
            "death": {"sheet": SpriteSheet("assets/enemy/death.png", 6), "count": 6}
        }
        
        # 3. Initialize the visual components
        self.image = self.animations[self.state]["sheet"].get_image(0, 2.0)
        self.rect = self.image.get_rect(center=self.pos)

    def die(self):
        # Only trigger death once
        if not self.is_dead:
            self.is_dead = True
            self.set_state("death")
            self.frame_index = 0 

    def chase(self, player_pos):
        direction = player_pos - self.pos
        if direction.length() > 0:
            self.pos += direction.normalize() * self.speed

    def update(self, player_pos):
        # 1. THE FIX: Guard Clause
        if self.is_dead:
            # While dying, we only want to animate and keep the rect in place
            self.animate()
            self.rect.center = self.pos
            return # Exit the function so AI logic below never runs

        # 2. Behavior Logic (Only runs if alive)
        dist = (player_pos - self.pos).length()

        if dist < 50:
            self.set_state("attack")
        elif dist < 450:
            self.set_state("walk")
            self.chase(player_pos)
        else:
            self.set_state("idle")

        self.animate()
        self.rect.center = self.pos

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0

    def animate(self):
        current_data = self.animations[self.state]
        max_frames = current_data["count"]

        self.frame_index += 0.15 
        
        # Handle end of animation
        if self.frame_index >= max_frames:
            if self.state == "death":
                # Freeze on the last frame of death and remove from game
                self.frame_index = max_frames - 1
                self.kill() 
            else:
                self.frame_index = 0
            
        self.image = current_data["sheet"].get_image(int(self.frame_index), 2.0)

    def draw_health(self, screen, camera):
        # Don't draw health bars for dead zombies
        if self.is_dead: return
        
        bar_width = 40
        bar_height = 5
        bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        
        screen_pos = camera.apply(self.rect)
        bar_rect.midbottom = screen_pos.midtop
        bar_rect.y -= 10

        pygame.draw.rect(screen, (200, 0, 0), bar_rect)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 200, 0), (bar_rect.x, bar_rect.y, bar_width * health_ratio, bar_height))