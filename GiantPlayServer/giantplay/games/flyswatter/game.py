'''
Created on 29 oct. 2018

@author: Achi
'''
from random import randint

from pygame.rect import Rect

from giantplay import cfg
from giantplay.games import Game
import pygame
from giantplay.utils.time import Speedometer

MAX_FLIES = 5

MAX_FLY_SPEED = 8
MIN_FLY_SPEED = 4


class Fly:

    def __init__(self, game):

        self.game = game
        self.posx, self.posy = 0, 0
        if randint(0,1):
            self.posx = 0 if randint(0,1) else cfg.SCREEN_WIDTH
            self.posy = randint(0, cfg.SCREEN_HEIGHT)
        else:
            self.posy = 0 if randint(0,1) else cfg.SCREEN_HEIGHT
            self.posx = randint(0, cfg.SCREEN_WIDTH)

        self.next_change = randint(3*cfg.FPS, 12*cfg.FPS)

        self.select_velocity()

        self.rect = None

    def is_out_of_bounds(self):
        return self.posx + self.velx < 0 or \
            self.posx + self.velx > cfg.SCREEN_WIDTH or \
               self.posy + self.vely < 0 or \
               self.posy + self.vely > cfg.SCREEN_HEIGHT

    def select_velocity(self):

        self.velx = randint(MIN_FLY_SPEED,MAX_FLY_SPEED) * 1 if randint(0,1) else -1
        self.vely = randint(MIN_FLY_SPEED,MAX_FLY_SPEED) * 1 if randint(0,1) else -1

        while self.is_out_of_bounds():
            self.velx = randint(MIN_FLY_SPEED, MAX_FLY_SPEED) * 1 if randint(0, 1) else -1
            self.vely = randint(MIN_FLY_SPEED, MAX_FLY_SPEED) * 1 if randint(0, 1) else -1

    def die(self):
        self.game.flyes.remove(self)

    def on_update(self):
        self.next_change -= 1

        if self.next_change <= 0 or self.is_out_of_bounds():
            self.select_velocity()
            self.next_change = randint(3*cfg.FPS, 12*cfg.FPS)

        self.posx += self.velx
        self.posy += self.vely

        self.rect = Rect(0, 0, 40, 40)
        self.rect.width = 20
        self.rect.height = 20
        self.rect.centerx = self.posx
        self.rect.centery = self.posy

    def on_render(self, g):
        pygame.draw.rect(g.surface, (0, 0, 0), self.rect, 5)


class FlyswatterGame(Game):

    def __init__(self, engine, builder):
        super(FlyswatterGame, self).__init__(engine, builder)

        self.next_fly = randint(3*cfg.FPS, 5*cfg.FPS)
        self.flyes = []

    def start(self):
        pass

    def stop(self):
        pass

    def on_user_connected(self, user_handler):
        user_handler.color = self.next_color()
        pass

    def on_user_disconnected(self, user_handler):
        pass

    def smash(self, user_handler):
        die = 0
        for fly in self.flyes:
            if fly.rect.colliderect(user_handler.rect):
                die += 5
                fly.die()

        if die > 0:
            self.next_fly = randint(3 * cfg.FPS, 5 * cfg.FPS)

        return die ** 1.2

    def on_update(self):

        if len(self.flyes) < MAX_FLIES:
            self.next_fly -= 1
            if self.next_fly <= 0:
                self.next_fly = randint(3 * cfg.FPS, 12 * cfg.FPS)

                fly = Fly(self)
                self.flyes.append(fly)

        for fly in self.flyes:
            fly.on_update()

        for user in self.users:
            user.on_update()

    def on_render(self, g):

        g.surface.fill((255, 255, 255))

        for fly in self.flyes:
            fly.on_render(g)

        top = 0
        font = pygame.font.Font(None, 36)

        sorted_users = sorted(self.users, key=lambda u1: u1.score, reverse=True)

        counter = 1;
        for user in sorted_users:
            if counter <= 10:
                text = font.render("%d. %s (%d)" % (counter, user.name, user.score), 1, user.color)

                textpos = text.get_rect()
                textpos.top = top
                textpos.left = 0
                top += text.get_height()
                g.surface.blit(text, textpos)

                counter += 1

            user.on_render(g)