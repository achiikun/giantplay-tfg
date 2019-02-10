'''
Created on 29 oct. 2018

@author: Achi
'''
import math
import threading
import time

import pygame
from pygame.rect import Rect

from giantplay import cfg
from giantplay.event import Event
from giantplay.games import UserHandler
from giantplay.utils.time import Speedometer

SMASH_TIME = cfg.FPS * 1.5


class FlyswatterGameUserHandler(UserHandler):

    def __init__(self, game, user):
        super().__init__(game, user)
        self.aimx = 0
        self.aimy = 0

        self.color = (0, 0, 255)
        self.rect = None

        self.smash_time = 0
        self.smash_color = (255, 255, 0)
        self.smashpos = 0, 0

        self.score = 0

        self.register_event("tdown", self.shot)
        self.register_event("aim", self.aim)

    def shot(self, user_handler, event):
        if self.smash_time <= 0:
            score = self.game.smash(self)
            self.score += score

            if score > 0:
                self.send_event(Event("rmbl",[0,500]))

            self.smash_color = (255, 0, 0) if score else (255, 255, 0)
            self.smash_time = SMASH_TIME
            self.smashpos = self.aimx, self.aimy

        pass

    def aim(self, user_handler, event):
        self.aimx = event.values[0];
        self.aimy = event.values[1];
        pass

    def on_update(self):
        self.rect = Rect(0,0,40,40)
        self.rect.width = 40
        self.rect.height = 40
        self.rect.centerx = self.aimx
        self.rect.centery = self.aimy

        if self.smash_time > 0:
            self.smash_time -= 1

    def on_render(self, g):

        pygame.draw.arc(g.surface, self.color, self.rect, 0, 360, 5)

        if self.smash_time > 0:
            draw_star(g.surface, SMASH_TIME-self.smash_time, position=self.smashpos, color=self.smash_color, radius=40)


def draw_star(surface, counter, position=None, color = (255, 255, 0), num_points=8, radius=100):
    point_list = []
    center_x = surface.get_width() // 2 if position == None else position[0]
    center_y = surface.get_height() // 2 if position == None else position[1]
    for i in range(num_points * 2):
        radius2 = radius
        if i % 2 == 0:
            radius2 = radius2 // 2
        ang = i * 3.14159 / num_points + counter * 3.14159 / 60
        x = center_x + int(math.cos(ang) * radius2)
        y = center_y + int(math.sin(ang) * radius2)
        point_list.append((x, y))
    pygame.draw.polygon(surface, color, point_list)