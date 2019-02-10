'''
Created on 29 oct. 2018

@author: Achi
'''
from giantplay.games import Game
import pygame
from giantplay.utils.time import Speedometer


class DummyGame(Game):

    def __init__(self, engine, builder):
        super(DummyGame, self).__init__(engine, builder)
        self.i = 0
        self.fps = Speedometer("FPS")

    def start(self):
        pass

    def stop(self):
        pass

    def on_user_connected(self, user_handler):
        pass

    def on_user_disconnected(self, user_handler):
        pass

    def on_update(self):
        super().on_update()

    def on_render(self, g):
        from giantplay import cfg

        self.fps += 1

        g.surface.fill((255, 0, 0))

        pygame.draw.circle(g.surface, (0, 0, 255), (self.i, 300), 10)
        self.i += 1
        if self.i > cfg.SCREEN_WIDTH:
            self.i = 0

        top = 0

        font = pygame.font.Font(None, 36)

        text = font.render("FPS: " + str(self.fps), 1, (10, 10, 10))  # str("I'm sexy and you know it")
        textpos = text.get_rect()
        textpos.top = 0
        textpos.left = 0
        top += text.get_height()
        g.surface.blit(text, textpos)

        for user in self.users:
            text = font.render(# user.name \
                                   user.name + (" %.4f %.4f" % (user.aimx, user.aimy)) \
                                   if user.rotation_vector is None else \
                                   (user.name + (" %.4f %.4f %.4f %.4f" % \
                                                 (user.rotation_vector[0],  user.rotation_vector[1], user.rotation_vector[2],
                                                  user.rotation_vector[3])
                                                 )), 1, (10, 10, 10))

            textpos = text.get_rect()
            textpos.top = top
            textpos.left = 0
            top += text.get_height()
            g.surface.blit(text, textpos)

            #if user.rotation_vector is not None:
            #    pygame.draw.line(g.surface, (0,0, 255), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2)), (int(cfg.SCREEN_WIDTH/2+user.rotation_vector[0]*100), int(cfg.SCREEN_HEIGHT/2)), 5)
            #    pygame.draw.line(g.surface, (0,0, 255), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2)), (int(cfg.SCREEN_WIDTH/2), int(cfg.SCREEN_HEIGHT/2-user.rotation_vector[1]*100)), 5)

            user.on_render(g)
