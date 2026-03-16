import pygame
from settings import *

class UI:
    def __init__(self):
        # Initialize fonts here so they are ready to use
        self.font = pygame.font.SysFont("arial", 32)
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)

    def draw_hud(self, screen, car, score):
        """Draws the Gameplay UI stacked in the top-left corner."""
        # 1. Score Text
        score_text = self.font.render(f"Presents: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        # --- Health Bar Dimensions ---
        bar_width = 200
        bar_height = 20
        # Positioned below the score (Score is at 20, bar at 60)
        bar_x = 20
        bar_y = 60 
        
        # 2. Health Bar Background (Dark Red)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # 3. Health Bar Foreground (Green)
        ratio = max(0, min(1, car.health / car.max_health))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * ratio), bar_height))
        
        # 4. White Border (Makes it look cleaner)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

        # 5. (Removed label)

    def draw_menu(self, screen, draw_bg=True):
        """Draws the Main Menu screen."""
        if draw_bg:
            screen.fill((10, 20, 40))
        # No title; only a blinking start prompt
        if pygame.time.get_ticks() % 1000 < 500:
            start = self.font.render("Press any key to start", True, (0, 255, 100))
            screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 500))

    def draw_howto_level1(self, screen):
        """Draws the How To Play screen for Level 1."""
        screen.fill((0, 0, 0))
        title = self.title_font.render("HOW TO PLAY", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))

        left_lines = [
            "W - Up",
            "S - Down",
            "A - Left",
            "D - Right",
        ]
        right_lines = [
            "LEFT SHIFT - Boost",
            "Collect gifts",
            "Avoid bombs",
        ]

        left_x = WIDTH // 2 - 260
        right_x = WIDTH // 2 + 40
        y = 260
        for line in left_lines:
            txt = self.font.render(line, True, (200, 200, 200))
            screen.blit(txt, (left_x, y))
            y += 40

        y = 260
        for line in right_lines:
            txt = self.font.render(line, True, (200, 200, 200))
            screen.blit(txt, (right_x, y))
            y += 40

        if pygame.time.get_ticks() % 1000 < 500:
            cont = self.font.render("Press any key to continue", True, (0, 255, 100))
            screen.blit(cont, (WIDTH // 2 - cont.get_width() // 2, 560))

    def draw_howto_level2(self, screen):
        """Draws the How To Play screen for Level 2."""
        screen.fill((0, 0, 0))
        title = self.title_font.render("HOW TO PLAY", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))

        left_lines = [
            "W - Accelerate",
            "S - Brake / Reverse",
            "A / D - Steer",
            "SPACE - Drift",
            "LEFT SHIFT + W - Nitro Boost",
        ]
        right_lines = [
            "Y - Shoot (auto-target)",
            "Blue buffs refuel nitro boost",
            "Green buffs restore health",
            "Eliminate enemies or reach 10 presents",
        ]

        left_x = WIDTH // 2 - 320
        right_x = WIDTH // 2 + 40
        y = 260
        for line in left_lines:
            txt = self.font.render(line, True, (200, 200, 200))
            screen.blit(txt, (left_x, y))
            y += 40

        y = 260
        for line in right_lines:
            txt = self.font.render(line, True, (200, 200, 200))
            screen.blit(txt, (right_x, y))
            y += 40

        if pygame.time.get_ticks() % 1000 < 500:
            cont = self.font.render("Press any key to continue", True, (0, 255, 100))
            screen.blit(cont, (WIDTH // 2 - cont.get_width() // 2, 560))

    def draw_game_over(self, screen, score):
        """Draws the Game Over overlay."""
        screen.fill((255,255,255))
        # Create a surface that supports transparency
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Fill with a semi-transparent dark red (R, G, B, Alpha)
        overlay.fill((40, 0, 0, 180)) 
        screen.blit(overlay, (0, 0))

        msg = self.title_font.render("SLEIGH DESTROYED", True, (255, 50, 50))
        score_msg = self.font.render(f"Final Score: {score}", True, (255, 255, 255))
        retry = self.font.render("Press R to Retry", True, (200, 200, 200))
        
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 200))
        screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, 320))
        screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, 450))


    def draw_nitro_bar(self, screen, car):
        # Padding and dimensions
        x, y = 20, 50  
        width, height = 200, 12
    
        # Background
        pygame.draw.rect(screen, (30, 30, 30), (x, y, width, height))
    
        # Nitro Fill
        fill_width = (car.nitro_charge / 100.0) * width
    
        # Pulse Effect: If boosting, make it flicker slightly
        bar_color = (0, 200, 255)
        if car.is_boosting and pygame.time.get_ticks() % 100 < 50:
            bar_color = (200, 255, 255) 
        
        pygame.draw.rect(screen, bar_color, (x, y, fill_width, height))
    
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 1)
