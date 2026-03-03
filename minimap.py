import pygame
from settings import *

class MiniMap:
    def __init__(self, world):
        self.base_map = pygame.transform.scale(
            world.map_image,
            (MINIMAP_SIZE, MINIMAP_SIZE)
        )

    def draw(self,screen,car,mission):
        pygame.draw.rect(screen,(20,20,20),(10,10,MINIMAP_SIZE,MINIMAP_SIZE))
        screen.blit(self.base_map,(10,10))

        # player
        x = int(car.pos.x/MAP_WIDTH*MINIMAP_SIZE)
        y = int(car.pos.y/MAP_HEIGHT*MINIMAP_SIZE)
        pygame.draw.circle(screen,(0,255,255),(10+x,10+y),4)

        # mission
        mx = int(mission.target[0]/MAP_WIDTH*MINIMAP_SIZE)
        my = int(mission.target[1]/MAP_HEIGHT*MINIMAP_SIZE)
        pygame.draw.circle(screen,(255,0,0),(10+mx,10+my),4)