import pygame
import random
from settings import *

class World:
    def __init__(self):
        self.map_image = pygame.image.load(
            "assets/full_city_map.png"
        ).convert()

        self.map_image = pygame.transform.scale(
            self.map_image,
            (MAP_WIDTH, MAP_HEIGHT)
        )

        print("Scanning roads... (one-time process)")
        self.road_nodes = self.generate_road_nodes()
        print("Road nodes:", len(self.road_nodes))

    # ==============================
    # PRE-SCAN ROADS (FAST SYSTEM)
    # ==============================
    # ==============================
# PRE-SCAN ROADS (ROBUST VERSION)
# ==============================
    def generate_road_nodes(self):
        nodes = []

        step = 6   # smaller step = more accurate

        for x in range(0, MAP_WIDTH, step):
            for y in range(0, MAP_HEIGHT, step):

                r, g, b = self.map_image.get_at((x, y))[:3]

                brightness = (r + g + b) / 3

                # Treat DARK pixels as road
                if brightness < 100:
                    nodes.append((x, y))

        return nodes


    # ==============================
    # ROAD CHECK
    # ==============================
    def is_road(self, x, y):

        if x < 0 or y < 0 or x >= MAP_WIDTH or y >= MAP_HEIGHT:
            return False

        r, g, b = self.map_image.get_at((int(x), int(y)))[:3]
        brightness = (r + g + b) / 3

        return brightness < 100

    # ==============================
    # DRAW
    # ==============================
    def draw(self, screen, camera):
        screen.blit(self.map_image,
                    (-camera.offset.x, -camera.offset.y))

    # ==============================
    # INSTANT ROAD SPAWN
    # ==============================
    def random_road_position(self):
        return random.choice(self.road_nodes)