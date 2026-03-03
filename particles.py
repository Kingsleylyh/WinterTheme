import pygame,random
from settings import *

class Snow:
    def __init__(self):
        self.particles=[]

    def update(self):
        if random.random()<0.5:
            self.particles.append([
                random.randint(0,WIDTH),
                0,
                random.randint(2,4)
            ])

        for p in self.particles:
            p[1]+=p[2]

        self.particles=[p for p in self.particles if p[1]<HEIGHT]

    def draw(self,screen):
        for p in self.particles:
            pygame.draw.circle(screen,(255,255,255),(p[0],p[1]),2)