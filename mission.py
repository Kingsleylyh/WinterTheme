import pygame
from settings import *
from pathfinding import astar

class Mission:
    def __init__(self,world):
        self.world = world
        self.new_mission()

    def new_mission(self):
        self.start = self.world.random_road_position()
        self.target = self.world.random_road_position()
        self.path = []

    def generate_path(self,car_pos):
        grid = 20
        start = (int(car_pos[0]//grid), int(car_pos[1]//grid))
        goal = (int(self.target[0]//grid), int(self.target[1]//grid))
        self.path = astar(start,goal,self.world,grid)

    def draw(self,screen,camera):
        # draw destination
        rect = pygame.Rect(self.target[0]-10,
                           self.target[1]-10,20,20)
        screen_rect = rect.move(-camera.offset.x,
                                -camera.offset.y)
        pygame.draw.rect(screen,(255,0,0),screen_rect)

        # draw GPS line
        for node in self.path:
            x = node[0]*20 - camera.offset.x
            y = node[1]*20 - camera.offset.y
            pygame.draw.circle(screen,(0,255,0),(x,y),3)

    def check(self,car):
        if pygame.Vector2(car.pos).distance_to(self.target) < 20:
            self.new_mission()
            return True
        return False