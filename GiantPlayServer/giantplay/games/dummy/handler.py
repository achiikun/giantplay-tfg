'''
Created on 29 oct. 2018

@author: Achi
'''
import threading
import time

import pygame
from pygame.rect import Rect

from giantplay.games import UserHandler
from giantplay.utils.time import Speedometer


class DummyGameUserHandler(UserHandler):

    def __init__(self, game, user):
        super().__init__(game, user)

        self.show_touch = False
        self.touchx = 0
        self.touchy = 0

        self.aimx = 0
        self.aimy = 0

        self.axisx = 0
        self.axisy = 0

        self.rotation_vector = None

        self.color = (0, 255, 0)

        self.register_event(("tdown", "tmove"), self.tdownmove)
        self.register_event("tup", self.tup)
        self.register_event("rotvec", self.rotvec)
        self.register_event("aim", self.aim)
        self.register_event("axis", self.axis)

    def on_update(self):
        pass

    def tdownmove(self, user_handler, event):
        self.show_touch = True
        self.touchx = event.values[0]
        self.touchy = event.values[1]

    def tup(self, user_handler, event):
        self.show_touch = False
        self.touchx = event.values[0]
        self.touchy = event.values[1]

    def rotvec(self, user_handler, event):
        self.rotation_vector = event.values

        pass

    def aim(self, user_handler, event):
        self.aimx = event.values[0];
        self.aimy = event.values[1];
        pass

    def axis(self, user_handler, event):
        self.axisx = event.values[0];
        self.axisy = event.values[1];
        pass

    def on_render(self, g):
        # Touch
        if self.show_touch:
            pygame.draw.circle(g.surface, self.color, (int(self.touchx), int(self.touchy)), 10)

        rect = Rect(0,0,40,40)
        rect.width = 40
        rect.height = 40
        rect.centerx = self.aimx
        rect.centery = self.aimy

        pygame.draw.arc(g.surface, (0,0,255), rect, 0, 360, 5)

        from giantplay import cfg
        pygame.draw.line(g.surface, (0,0, 255), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2)), (int(cfg.SCREEN_WIDTH/2+self.axisx*100), int(cfg.SCREEN_HEIGHT/2)), 5)
        pygame.draw.line(g.surface, (0,0, 255), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2)), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2+self.axisy*100)), 5)
