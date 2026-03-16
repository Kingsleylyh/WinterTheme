import pygame
import random
import os
from settings import *

class World:
    def __init__(self, tile_size=128):
        # 1. Basic settings
        self.tile_size = tile_size
        self.tiles = {}
        
        # 2. Road IDs (Including all rotated variations)
        self.road_tile_ids = {1, 2, 3, 4, 5, 33, 34, 101, 102, 103, 201, 202, 203}
        
        # 3. Initialize 30x30 matrix with Grass (0)
        self.map_data = [[0 for _ in range(30)] for _ in range(30)]
        
        # 4. Setup World
        self.carve_road_layout()
        self.load_tiles("assets/tiles")
        
        # 5. Pathfinding/Spawn Nodes
        self.road_nodes = self.generate_road_nodes()

    def carve_road_layout(self):
            # 1. OUTER RING (The Boundary)
            for x in range(1, 29):
                self.map_data[0][x] = 3    
                self.map_data[29][x] = 4   
            for y in range(1, 29):
                self.map_data[y][0] = 33   
                self.map_data[y][29] = 34  

            # 2. THE MAIN CROSS (Horizontal and Vertical Arteries)
            mid = 15
            for i in range(1, 29):
                self.map_data[mid][i] = 3 
                self.map_data[i][mid] = 33

            # 3. INTERNAL ALLEYWAYS (Creating the "Grid" feel)
            for i in range(5, 25):
                self.map_data[8][i] = 3   # Upper Alley
                self.map_data[22][i] = 3  # Lower Alley
                self.map_data[i][8] = 33  # Left Alley
                self.map_data[i][22] = 34 # Right Alley

            # 4. INTERSECTIONS (Placing Tile 5 at every road meeting point)
            intersections = [
                (0, mid), (29, mid), (mid, 0), (mid, 29), (mid, mid), # Main Cross
                (8, 8), (8, 15), (8, 22),                            # Upper Intersections
                (22, 8), (22, 15), (22, 22),                         # Lower Intersections
                (15, 8), (15, 22)                                    # Side Intersections
            ]
            for r, c in intersections:
                self.map_data[r][c] = 5

            # 5. COMPLEX BUILDING CLUSTERS 
            for r_start, c_start in [(3,3), (3,18), (18,3), (18,18)]:
                for dr in range(3):
                    for dc in range(3):
                        # Only place a house if there isn't a road there already
                        if self.map_data[r_start + dr][c_start + dc] == 0:
                            self.map_data[r_start + dr][c_start + dc] = 9

            # 6. CORNERS 
            self.map_data[0][0] = 2        
            self.map_data[0][29] = 102     
            self.map_data[29][29] = 202    
            self.map_data[29][0] = 201    

    def load_tiles(self, path):
        if not os.path.exists(path):
            print(f"Error: Folder {path} not found!")
            return

        for filename in os.listdir(path):
            if filename.endswith(".png"):
                try:
                    tile_id = int(filename.split('.')[0])
                    # .convert() + set_colorkey is the fix for black backgrounds
                    img = pygame.image.load(os.path.join(path, filename)).convert()
                    img.set_colorkey((0, 0, 0)) 
                    
                    scaled = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                    self.tiles[tile_id] = scaled
                    
                    # 1. Rotate Straights (3, 4) -> Vertical (33, 34)
                    if tile_id in [3, 4]:
                        self.tiles[tile_id + 30] = pygame.transform.rotate(scaled, 90)

                    # 2. Rotate Turns (1, 2) -> 4-way rotations
                    if tile_id in [1, 2]:
                        for i in range(1, 4):
                            rotated = pygame.transform.rotate(scaled, i * 90)
                            self.tiles[tile_id * 100 + i] = rotated
                            
                except ValueError:
                    pass

    def is_road(self, x, y):
        """Used for car physics: Checks if a coordinate is a driveable road."""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        if 0 <= grid_y < 30 and 0 <= grid_x < 30:
            return self.map_data[grid_y][grid_x] in self.road_tile_ids
        return False

    def generate_road_nodes(self):
        """Creates a list of pixel centers for all road tiles (useful for AI/Spawning)."""
        nodes = []
        for r, row in enumerate(self.map_data):
            for c, tile_id in enumerate(row):
                if tile_id in self.road_tile_ids:
                    # Calculate center of tile in pixels
                    center_x = c * self.tile_size + self.tile_size // 2
                    center_y = r * self.tile_size + self.tile_size // 2
                    nodes.append((center_x, center_y))
        return nodes

    def random_road_position(self):
        """Returns a random (x, y) pixel coordinate on the road."""
        return random.choice(self.road_nodes) if self.road_nodes else (0,0)

    def draw(self, screen, camera):
        """Double-Pass Rendering: Draws Grass (0) behind everything."""
        start_col = max(0, int(camera.offset.x // self.tile_size))
        end_col = min(30, int((camera.offset.x + WIDTH) // self.tile_size) + 2)
        start_row = max(0, int(camera.offset.y // self.tile_size))
        end_row = min(30, int((camera.offset.y + HEIGHT) // self.tile_size) + 2)

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                tile_id = self.map_data[r][c]
                draw_x = c * self.tile_size - camera.offset.x
                draw_y = r * self.tile_size - camera.offset.y
                
                # --- PASS 1: Base Ground ---
                if 0 in self.tiles:
                    screen.blit(self.tiles[0], (draw_x, draw_y))
                
                # --- PASS 2: Road/Building Overlay ---
                if tile_id != 0 and tile_id in self.tiles:
                    screen.blit(self.tiles[tile_id], (draw_x, draw_y))