'''
Created on 29 oct. 2018

@author: Achi
'''
import math
import random

import pygame
from pygame import font
from pygame.rect import Rect

from giantplay import cfg
from giantplay.event import Event
from giantplay.games import UserHandler
from giantplay.games.tanks import game
from giantplay.utils.time import Speedometer

SMASH_TIME = cfg.FPS * 1.5
CANNON_LENGTH=30


class TanksGameUserHandler(UserHandler):

    def __init__(self, game, user):
        super().__init__(game, user)
        self.posx = cfg.SCREEN_WIDTH/2
        self.posy = cfg.SCREEN_HEIGHT/2
        self.velx = 0
        self.vely = 0
        self.canon_angle = 0

        self.pos = (int(self.posx), int(self.posy))
        self.pos_cannon = (int(self.posx + math.cos(self.canon_angle) * CANNON_LENGTH),
                           int(self.posy + math.sin(self.canon_angle) * CANNON_LENGTH))

        self.color = pygame.color.Color(0, 0, 255)

        self.rect = Rect(0, 0, 40, 40)
        self.rect.width = 40
        self.rect.height = 40

        self.smash_time = 0
        self.invencibility = 0

        self.score = 3

        self.register_event(('tdown', 'tmove'), self.aim)
        self.register_event('tpdown', self.shot)
        self.register_event('axis', self.axis)

    def init(self):
        self.send_event(Event("rgb", [self.color.r, self.color.g, self.color.b]))

    def shot(self, user_handler, event):
        if self.smash_time <= 0 and self.score > 0:
            self.smash_time = SMASH_TIME
            self.send_event(Event("light", [1]))
            self.send_event(Event("rgb", [255, 0, 0]))

            bullet = game.Bullet(self, [self.pos_cannon[0], self.pos_cannon[1]], [math.cos(self.canon_angle), math.sin(self.canon_angle)])
            self.game.add_bullet(bullet)

        pass

    def aim(self, user_handler, event):
        self.canon_angle = math.atan2(event.values[1]-cfg.SCREEN_HEIGHT/2, event.values[0]-cfg.SCREEN_WIDTH/2)

    def axis(self, user_handler, event):
        if math.fabs(event.values[0]) > 0.2:
            self.velx = event.values[0]*3
        else:
            self.velx = 0

        if math.fabs(event.values[1]) > 0.2:
            self.vely = event.values[1]*3
        else:
            self.vely = 0

    def set_at_random_position(self):

        self.posx = random.randint(0, cfg.SCREEN_WIDTH)
        self.posy = random.randint(0, cfg.SCREEN_HEIGHT)
        self.rect.centerx = self.posx
        self.rect.centery = self.posy

        while self.game.is_scenario_colliding(self.rect):
            self.posx = random.randint(0, cfg.SCREEN_WIDTH)
            self.posy = random.randint(0, cfg.SCREEN_HEIGHT)
            self.rect.centerx = self.posx
            self.rect.centery = self.posy

    def hit(self):
        if self.invencibility <= 0:
            self.invencibility = 3 * cfg.FPS
            self.score -= 1
            self.send_event(Event("rmbl", [0, 500]))

    def on_update(self):

        posx = self.posx
        posy = self.posy

        self.rect.centerx = posx + self.velx
        self.rect.centery = posy
        if not self.game.is_scenario_colliding(self.rect) and not self.game.is_user_colliding(self.rect, self):
            self.posx += self.velx

        self.rect.centerx = posx
        self.rect.centery = posy + self.vely
        if not self.game.is_scenario_colliding(self.rect) and not self.game.is_user_colliding(self.rect, self):
            self.posy += self.vely

        self.rect.centerx = self.posx
        self.rect.centery = self.posy

        if self.smash_time > 0:
            self.smash_time -= 1
            if self.smash_time <= 0:
                self.send_event(Event("rgb", [self.color.r, self.color.g, self.color.b]))

        self.pos = (int(self.posx), int(self.posy))
        self.pos_cannon = (int(self.posx+math.cos(self.canon_angle)*CANNON_LENGTH), int(self.posy+math.sin(self.canon_angle)*CANNON_LENGTH))

        if self.invencibility > 0:
            self.invencibility -= 1

    def on_render(self, g):

        if self.invencibility == 0 or self.invencibility % 4 == 0 or self.invencibility % 4 == 1:

            color = self.color

            if self.score == 0:
                color = pygame.color.Color(220,220,220, 25)

            pygame.draw.arc(g.surface, color, self.rect, 0, 360, 5)

            pygame.draw.line(g.surface, color, self.pos, self.pos_cannon, 6)
            pygame.draw.circle(g.surface, color, self.pos, int(6+3))
            pygame.draw.circle(g.surface, color, self.pos_cannon, int(6+1))

            if self.smash_time > 0:
                draw_star(g.surface, SMASH_TIME-self.smash_time, position=(self.posx, self.posy), color=color,
                          num_points=20, radius=20)

            heart = "♥" * self.score

            font = pygame.font.SysFont("console", 25)

            text = font.render(heart, 1, (255, 0, 0))

            textpos = text.get_rect()
            textpos.center = self.rect.center
            g.surface.blit(text, textpos)


def draw_star(surface, counter, position=None, color = (255, 255, 0), num_points=8, radius=100):
    point_list = []
    center_x = surface.get_width() // 2 if position is None else position[0]
    center_y = surface.get_height() // 2 if position is None else position[1]
    for i in range(num_points * 2):
        radius2 = radius
        if i % 2 == 0:
            radius2 = radius2 // 2
        ang = i * 3.14159 / num_points + counter * 3.14159 / 60
        x = center_x + int(math.cos(ang) * radius2)
        y = center_y + int(math.sin(ang) * radius2)
        point_list.append((x, y))
    pygame.draw.polygon(surface, color, point_list)