'''
Created on 29 oct. 2018

@author: Achi
'''
import math
import random
from random import randint

from pygame.rect import Rect

from giantplay import cfg
from giantplay.games import Game
import pygame

from giantplay.games.simplephysics import CollisionCell, CollisionGrid
from giantplay.games.tanks.layouts import layouts
from giantplay.utils.time import Speedometer

BULLET_LENGTH=10
BULLET_SPEED=7


class TanksCollisionCell(CollisionCell):

    def __init__(self, panel, pos, size, color=(153, 51, 0), object=None):
        super().__init__(panel, pos, size)
        self.color = color
        self.object = object

    def on_render(self, g, rect):
        pygame.draw.rect(g.surface, self.color, rect)


class Bullet:

    def __init__(self, owner, pos, direction):
        self.owner = owner
        self.game = self.owner.game
        self.pos = [pos[0], pos[1]]
        self.direction = [direction[0], direction[1]]
        self.color = (0,0,0)
        self.bounces_left = random.randint(0,3)

        self.rect = Rect(0, 0, 5, 5)

    @property
    def next_pos(self):
        return [self.pos[0] + self.direction[0] * BULLET_SPEED,
                self.pos[1] + self.direction[1] * BULLET_SPEED]

    @property
    def vel(self):
        return [self.direction[0] * BULLET_SPEED,
                self.direction[1] * BULLET_SPEED]

    def on_update(self):
        value, cell = self.game.get_bounce_direction(self)

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

        self.rect.center = self.pos

        if value is not None:
            self.bounces_left -= 1
            if self.bounces_left <= 0:
                self.game.remove_bullet(self)
        else:
            user_handler = self.game.is_user_colliding(self.rect)

            if user_handler is not None:
                user_handler.hit()
                self.game.remove_bullet(self)

    def on_render(self, g):

        pos2 = (self.pos[0] - self.direction[0] * BULLET_LENGTH, self.pos[1] - self.direction[1] * BULLET_LENGTH)
        pygame.draw.line(g.surface, self.color, self.pos, pos2, 6)

        pass


class TanksGame(Game):

    def __init__(self, engine, builder):
        super(TanksGame, self).__init__(engine, builder)
        self.background = None
        self.bullets = []
        self.time_to_reset = -1

    def start(self):
        self.background = CollisionGrid()
        self.background.fill_borders(TanksCollisionCell)

        layouts[random.randint(0, len(layouts)-1)](self, TanksCollisionCell)

        self.time_to_reset = -1

        pass

    def stop(self):
        pass

    def on_user_connected(self, user_handler):
        user_handler.set_at_random_position()
        user_handler.color = self.next_color()
        user_handler.init()
        pass

    def on_user_disconnected(self, user_handler):
        pass

    def is_scenario_colliding(self, rect):
        for cell in self.background.get_colliding_cells(rect):
            if cell:
                return True
        return False

    def is_user_colliding(self, rect, excep=None):
        for user_handler in self.users:
            if user_handler != excep and user_handler.score > 0 and rect.colliderect(user_handler.rect):
                return user_handler
        return None

    def get_bounce_direction(self, bullet):
        return self.background.get_bounce_direction(bullet.pos, bullet.vel)

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)

    def on_update(self):

        alife = 0
        for user in self.users:
            user.on_update()
            if user.score > 0:
                alife += 1

        if alife <= 1 and self.time_to_reset == -1:
            self.time_to_reset = 5*cfg.FPS+1

        for bullet in self.bullets:
            bullet.on_update()

        if self.time_to_reset > 0:
            self.time_to_reset -= 1
            if self.time_to_reset == 0:
                self.engine.set_reset_game()

    def on_render(self, g):

        g.surface.fill((255, 255, 255))

        self.background.on_render(g)

        top = 0
        font = pygame.font.Font(None, 36)

        sorted_users = sorted(self.users, key=lambda u1: -u1.score, reverse=True)

        counter = 1
        for user in sorted_users:

            if counter <= 10:
                text = font.render("%d. %s (%d)" % (counter, user.name, user.score), 1, user.color)

                textpos = text.get_rect()
                textpos.top = top
                textpos.left = 0
                top += text.get_height()
                g.surface.blit(text, textpos)

                counter += 1

        for user in sorted_users:
            user.on_render(g)

        for bullet in self.bullets:
            bullet.on_render(g)