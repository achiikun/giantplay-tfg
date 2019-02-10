'''
Created on 29 oct. 2018

@author: Achi
'''
import random
from random import randint

from pygame.rect import Rect

from giantplay import cfg
from giantplay.games import Game
import pygame

from giantplay.games.simplephysics import CollisionCell, CollisionGrid
from giantplay.utils import vectorutils
from giantplay.utils.time import Speedometer

class Brick(CollisionCell):

    def __init__(self, panel, pos, size, color=(153, 51, 0), object=None):
        super().__init__(panel, pos, size)
        self.color = color
        self.object = object

    def on_update(self):
        pass

    def on_render(self, g, rect):
        rect = self.panel.get_rect(self.pos, self.size)
        pygame.draw.rect(g.surface, self.color, rect)


class BricksGame(Game):

    def __init__(self, engine, builder):
        super(BricksGame, self).__init__(engine, builder)
        self.background = None
        self.bricks = []
        self.rect = None
        self.time_to_reset = -1

    def start(self):
        self.background = CollisionGrid()
        self.rect = Rect(0,0, cfg.SCREEN_HEIGHT-20, cfg.SCREEN_HEIGHT-20)
        self.rect.center = (cfg.SCREEN_WIDTH/2, cfg.SCREEN_HEIGHT/2)
        self.time_to_reset = -1

        width = int(self.background.xslices/2)
        xs = width*0.5
        cxs = int((width-xs)/2)

        height = int(self.background.yslices/2)
        ys = height*0.5
        cys = int((height-ys)/2)

        gap = min(xs/3, ys/3)

        counter = 0
        for y in range(cys, height - cys):

            gap2 = 0
            if counter < gap:
                gap2 = gap-counter
            elif (height - cys*2) - counter - 1 < gap:
                gap2 = gap - ((height - cys*2)-counter - 1)

            gap2 = int(gap2)

            for x in range(cxs+gap2, width - cxs - gap2):
                brick = Brick(self.background, (x*2, y*2), (2, 2), self.rand_color())
                self.background.set(x*2, y*2, brick)
                self.background.set(x*2+1, y*2, brick)
                self.background.set(x*2, y*2+1, brick)
                self.background.set(x*2+1, y*2+1, brick)
                self.bricks.append(brick)

            counter += 1

        pass

    def stop(self):
        pass

    def on_user_connected(self, user_handler):
        user_handler.color = self.next_color()
        user_handler.ball.color = user_handler.color
        user_handler.init()
        pass

    def on_user_disconnected(self, user_handler):
        pass

    def get_bounce_direction(self, bullet):
        direction, cell = self.background.get_bounce_direction(bullet.pos, bullet.vel)

        if cell:
            self.background.set(cell.pos[0], cell.pos[1], None)
            self.background.set(cell.pos[0] + 1, cell.pos[1], None)
            self.background.set(cell.pos[0], cell.pos[1] + 1, None)
            self.background.set(cell.pos[0] + 1, cell.pos[1] + 1, None)
            self.bricks.remove(cell)

            if len(self.bricks) == 0:
                self.time_to_reset = 5*cfg.FPS

        return direction

    def is_user_colliding(self, ball):

        rad = ball.ball_rad

        if self.rect.width/2-10 < rad < self.rect.width/2+10:

            angle = ball.ball_angle

            for user2 in self.users:
                diff = vectorutils.calculate_difference_between_angles(angle, user2.angle)
                if abs(diff) < 0.15:
                    return user2

        return None

    def on_update(self):

        for user in self.users:
            user.on_update()

        for brick in self.bricks:
            brick.on_update()

        if self.time_to_reset > 0:
            self.time_to_reset -= 1
            if self.time_to_reset == 0:
                self.engine.set_reset_game()

    def on_render(self, g):

        g.surface.fill((255, 255, 255))

        for brick in self.bricks:
            brick.on_render(g, None)

        top = 0
        font = pygame.font.Font(None, 36)

        sorted_users = self.users #sorted(self.users, key=lambda u1: u1.score, reverse=True)

        counter = 1
        for user in sorted_users:

            if counter <= 10:
                text = font.render("%s" % (user.name), 1, user.color)

                textpos = text.get_rect()
                textpos.top = top
                textpos.left = 0
                top += text.get_height()
                g.surface.blit(text, textpos)

                counter += 1

            user.on_render(g)