'''
Created on 30 oct. 2018

@author: Achi
'''

import pygame
import sys
from pygame.locals import QUIT

class GraphixController:

    def __init__(self, w, h, fps): 
        self.screen = None
        self.surface = None
        self.fpsClock = None
        self.clock = None
        self.screenw = w
        self.screenh = h
        self.fps = fps


    def init_graphix(self):
        pygame.init()
        self.fpsClock=pygame.time.Clock()
        pygame.display.set_caption('GiantPlay Screen')
        self.screen = pygame.display.set_mode((self.screenw, self.screenh), 0, 32)
        pygame.display.toggle_fullscreen()
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface = self.surface.convert()
        self.surface.fill((255,255,255))
        self.clock = pygame.time.Clock()
        
    def quit_graphix(self):
        pygame.quit()
    
    def handle_graphix_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    print("pressed CTRL-C as an event")
                    return 1
                elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((self.screenw, self.screenh))
                    else:
                        pygame.display.set_mode((self.screenw, self.screenh), pygame.FULLSCREEN)
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    return 2

            
        return 0
                
    def draw_graphix(self):
        #pygame.transform.smoothscale(self.surface, (int(self.screenw / 2), int(self.screenh / 2)))
        self.screen.blit(self.surface, (0,0))
    
        pygame.display.flip()
        pygame.display.update()
        
    def tick_graphix(self):
        self.fpsClock.tick(self.fps)