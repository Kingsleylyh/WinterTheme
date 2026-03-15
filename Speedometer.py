import pygame
import math

def draw_gauge(screen, car_speed, font):
    WIDTH, HEIGHT = screen.get_size()
    GAUGE_CENTER = (WIDTH - 110, HEIGHT - 110)
    GAUGE_RADIUS = 80
    MAX_VAL = 3 # Adjust to your car's max velocity
    
    # 1. Background Circle
    pygame.draw.circle(screen, (20, 20, 20), GAUGE_CENTER, GAUGE_RADIUS)
    pygame.draw.circle(screen, (180, 180, 180), GAUGE_CENTER, GAUGE_RADIUS, 4)

    # 2. Redline Logic
    speed_ratio = min(car_speed / MAX_VAL, 1.0)
    if speed_ratio > 0.8:
        if (pygame.time.get_ticks() // 150) % 2 == 0:
            rect = pygame.Rect(GAUGE_CENTER[0]-GAUGE_RADIUS, GAUGE_CENTER[1]-GAUGE_RADIUS, 
                               GAUGE_RADIUS*2, GAUGE_RADIUS*2)
            # Draw red arc from -45 to 0 degrees
            pygame.draw.arc(screen, (255, 0, 0), rect, math.radians(-45), math.radians(5), 12)

    # 3. Needle Trigonometry
    # Map 0-1.0 to -225 to 45 degrees
    angle_deg = -225 + (speed_ratio * 270)
    angle_rad = math.radians(angle_deg)
    
    end_x = GAUGE_CENTER[0] + (GAUGE_RADIUS - 15) * math.cos(angle_rad)
    end_y = GAUGE_CENTER[1] + (GAUGE_RADIUS - 15) * math.sin(angle_rad)
    
    # Draw needle
    color = (255, 50, 50) if speed_ratio > 0.8 else (255, 255, 255)
    pygame.draw.line(screen, color, GAUGE_CENTER, (end_x, end_y), 5)
    pygame.draw.circle(screen, (100, 100, 100), GAUGE_CENTER, 10)

    # 4. Digital Text
    txt = font.render(f"{int(car_speed * 10)} KM/H", True, (255, 255, 255))
    screen.blit(txt, (GAUGE_CENTER[0] - txt.get_width()//2, GAUGE_CENTER[1] + 25))