import pygame
import sys

from settings import *
from world import World
from car import Car
from camera import Camera
from minimap import MiniMap
from mission import Mission
from particles import Snow

pygame.init()
pygame.display.set_caption("Santa Winter Delivery")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

world = World()

# Road-only spawn
spawn_pos = world.random_road_position()
car = Car(spawn_pos)

camera = Camera()
mission = Mission(world)
minimap = MiniMap(world)
snow = Snow()

score = 0
font = pygame.font.SysFont("arial", 24)

# Generate first GPS path
mission.generate_path(car.pos)


while True:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    car.update(world)
    camera.update(car)

    # Recalculate GPS path occasionally
    mission.generate_path(car.pos)

    # Check delivery
    if mission.check(car):
        score += 1
        print("🎁 Delivered! Score:", score)

        # New mission destination (road-only)
        mission.generate_path(car.pos)

    snow.update()

    screen.fill((0, 0, 0))

    # Draw world map
    world.draw(screen, camera)

    # Draw GPS + destination
    mission.draw(screen, camera)

    # Draw Santa
    screen.blit(car.image, camera.apply(car.rect))

    # Snow overlay
    snow.draw(screen)

    # Minimap (top-left)
    minimap.draw(screen, car, mission)

    # Score UI
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 150, 20))

    pygame.display.update()