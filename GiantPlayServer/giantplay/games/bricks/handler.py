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

BULLET_SPEED=7


class Bullet:

    def __init__(self, owner, pos, direction):
        self.owner = owner
        self.game = self.owner.game
        self.pos = [pos[0], pos[1]]
        self.direction = [direction[0], direction[1]]
        self.color = (0,0,0)
        self.free = False

        self.rect = Rect(0, 0, 5, 5)

    @property
    def next_pos(self):
        return [self.pos[0] + self.direction[0] * BULLET_SPEED,
                self.pos[1] + self.direction[1] * BULLET_SPEED]

    @property
    def vel(self):
        return [self.direction[0] * BULLET_SPEED,
                self.direction[1] * BULLET_SPEED]

    @property
    def ball_rad(self):
        return math.hypot(self.pos[0] - self.game.rect.centerx, self.pos[1] - self.game.rect.centery)

    @property
    def ball_angle(self):
        return math.atan2(-(self.pos[1] - self.game.rect.centery), self.pos[0] - self.game.rect.centerx)

    def shot(self):
        if not self.free:
            self.free = True
            self.select_angle()

    def select_angle(self):
        angle = self.owner.angle + math.pi
        angle += random.randint(-10,10)*0.1
        self.direction = [
            math.cos(angle),
            -math.sin(angle)
        ]

    def on_update(self):

        rad = int(self.game.rect.width / 2) - 10

        if not self.free:

            self.pos = [
                self.game.rect.centerx + int(math.cos(self.owner.angle) * rad),
                self.game.rect.centery + int(-math.sin(self.owner.angle) * rad)
            ]

        else:

            value = self.game.get_bounce_direction(self)

            if value == 'corner':
                self.direction[:] = [-self.direction[0], -self.direction[1]]
            elif value == 'up':
                self.direction[:] = [self.direction[0], -self.direction[1]]
            elif value == 'down':
                self.direction[:] = [self.direction[0], -self.direction[1]]
            elif value == 'right':
                self.direction[:] = [-self.direction[0], self.direction[1]]
            elif value == 'left':
                self.direction[:] = [-self.direction[0], self.direction[1]]

            self.pos[0] += self.direction[0] * BULLET_SPEED
            self.pos[1] += self.direction[1] * BULLET_SPEED

            if value is None and self.game.is_user_colliding(self):
                self.select_angle()
            else:
                rad2 = self.ball_rad

                if rad2 > rad+30:
                    self.free = False

            pass

    def on_render(self, g):

        pygame.draw.circle(g.surface, self.color, (int(self.pos[0]), int(self.pos[1])), 6, 6)

        pass


class BricksGameUserHandler(UserHandler):

    def __init__(self, game, user):
        super().__init__(game, user)

        self.angle = 0

        self.color = pygame.color.Color(0, 0, 255)

        self.register_event(('tdown'), self.shot)
        self.register_event('axis', self.axis)

        self.ball = Bullet(self, [0,0], [0,0])

    def init(self):
        self.send_event(Event("rgb", [self.color.r, self.color.g, self.color.b]))

    def shot(self, user_handler, event):
        self.ball.shot()
        pass

    def axis(self, user_handler, event):

        self.angle = math.atan2(-event.values[1], event.values[0])

        pass

    def set_at_random_position(self):
        self.angle = random.randint(0,359)
        pass

    def on_update(self):
        self.ball.on_update()
        pass

    def on_render(self, g):

        pygame.draw.arc(g.surface, self.color, self.game.rect, self.angle-0.15, self.angle+0.15, 7)
        self.ball.on_render(g)

        pass


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