import pygame
from settings import *
from pathfinding import astar

class Mission:
    def __init__(self, world):
        self.world = world
        self.target = pygame.math.Vector2(0, 0)
        self.path = []
        self.new_mission()

    def new_mission(self):
        # Pick a random road node from the world's generated list
        self.target = pygame.math.Vector2(self.world.random_road_position())
        self.path = []

    def generate_path(self, car_pos):
        # CS Tip: Use the tile_size as the grid unit to align with World.map_data
        grid_size = self.world.tile_size
        
        # Convert pixel coordinates to grid coordinates (0-29)
        start = (int(car_pos.x // grid_size), int(car_pos.y // grid_size))
        goal = (int(self.target.x // grid_size), int(self.target.y // grid_size))
        
        # Ensure start and goal are within bounds
        start = (max(0, min(29, start[0])), max(0, min(29, start[1])))
        goal = (max(0, min(29, goal[0])), max(0, min(29, goal[1])))

        # Generate path using tile indices
        self.path = astar(start, goal, self.world)

    def draw(self, screen, camera):
        # 1. Draw Destination (Red Gift Icon)
        # Using a larger rect since tiles are 256px
        target_rect = pygame.Rect(0, 0, 40, 40)
        target_rect.center = self.target
        screen_rect = camera.apply(target_rect)
        pygame.draw.rect(screen, (255, 0, 0), screen_rect)
        pygame.draw.rect(screen, (255, 255, 255), screen_rect, 2) # Border

        # 2. Draw GPS Line (Breadcrumbs)
        if self.path:
            for node in self.path:
                # Convert grid index back to center-of-tile pixel coordinates
                px = node[0] * self.world.tile_size + self.world.tile_size // 2
                py = node[1] * self.world.tile_size + self.world.tile_size // 2
                
                # Apply camera offset
                screen_pos = camera.apply(pygame.Rect(px, py, 0, 0)).topleft
                pygame.draw.circle(screen, (0, 255, 0), screen_pos, 5)

    def check(self, car):
        # Check if car reached target (expanded radius due to large tiles)
        if pygame.Vector2(car.pos).distance_to(self.target) < 100:
            self.new_mission()
            return True
        return False