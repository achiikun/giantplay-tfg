'''
Created on 29 oct. 2018

@author: Achi
'''
from giantplay.event.util import SelectorEventListener
from giantplay.event.basic import PhoneToScreenTouchEventHandler, RotationVectorToAxisEventHandler
from giantplay.games import GameBuilder
from giantplay.games.bricks.game import BricksGame
from giantplay.games.bricks.handler import BricksGameUserHandler


class BricksGameBuilder(GameBuilder):

    def __init__(self, engine):
        super(BricksGameBuilder, self).__init__(engine)

    def key(self):
        return "brick"

    def name(self):
        return "Bricks"

    def build_game(self):
        return BricksGame(self.engine, self)

    def build_user_handler(self, game, user):
        return BricksGameUserHandler(game, user)

    def build_event_listener(self, game, user_handler):
        multi = SelectorEventListener()

        multi.register_listener(('tdown'), PhoneToScreenTouchEventHandler(user_handler, user_handler))
        multi.register_listener(('rotvec'), RotationVectorToAxisEventHandler(user_handler, user_handler))

        return multi, ()
