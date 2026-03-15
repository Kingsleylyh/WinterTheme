import pygame
from settings import *

class MiniMap:
    def __init__(self, world):
        self.tile_size = world.tile_size
        # Calculate world dimensions based on the grid
        self.world_cols = len(world.map_data[0])
        self.world_rows = len(world.map_data)
        self.full_world_width = self.world_cols * self.tile_size
        self.full_world_height = self.world_rows * self.tile_size

        # Create the MiniMap surface
        self.base_map = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        self.generate_static_map(world)
        
        # Position (Bottom Left)
        self.offset_x = 20
        self.offset_y = HEIGHT - MINIMAP_SIZE - 20

    def generate_static_map(self, world):
        """Renders a simplified version of the tile grid onto the minimap surface."""
        # Calculate how big one tile is on the minimap
        mini_tile_w = MINIMAP_SIZE / self.world_cols
        mini_tile_h = MINIMAP_SIZE / self.world_rows

        self.base_map.fill((20, 20, 20)) # Background color

        for row_idx, row in enumerate(world.map_data):
            for col_idx, tile_id in enumerate(row):
                if tile_id in world.road_tile_ids:
                    # Draw a small gray square for every road tile
                    rect = (col_idx * mini_tile_w, row_idx * mini_tile_h, 
                            mini_tile_w + 1, mini_tile_h + 1)
                    pygame.draw.rect(self.base_map, (100, 100, 100), rect)

    def draw(self, screen, car, mission, enemies):
        # 1. Draw Border
        pygame.draw.rect(screen, (255, 255, 255), 
                         (self.offset_x - 2, self.offset_y - 2, MINIMAP_SIZE + 4, MINIMAP_SIZE + 4), 2)
        
        # 2. Draw the generated map
        screen.blit(self.base_map, (self.offset_x, self.offset_y))

        # 3. Player Position (Scaling world pos to minimap pos)
        # Formula: (Current Pos / Total World Size) * MiniMap Size
        px = int((car.pos.x / self.full_world_width) * MINIMAP_SIZE)
        py = int((car.pos.y / self.full_world_height) * MINIMAP_SIZE)
        pygame.draw.circle(screen, (0, 255, 255), (self.offset_x + px, self.offset_y + py), 4)

        # 4. Mission Target
        mx = int((mission.target[0] / self.full_world_width) * MINIMAP_SIZE)
        my = int((mission.target[1] / self.full_world_height) * MINIMAP_SIZE)
        pygame.draw.circle(screen, (255, 0, 0), (self.offset_x + mx, self.offset_y + my), 4)

        # 5. Enemies
        for enemy in enemies:
            if getattr(enemy, "is_dead", False):
                continue
            ex = int((enemy.pos.x / self.full_world_width) * MINIMAP_SIZE)
            ey = int((enemy.pos.y / self.full_world_height) * MINIMAP_SIZE)
            pygame.draw.circle(screen, (0, 255, 0), (self.offset_x + ex, self.offset_y + ey), 3)
