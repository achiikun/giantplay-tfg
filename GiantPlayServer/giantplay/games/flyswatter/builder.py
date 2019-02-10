'''
Created on 29 oct. 2018

@author: Achi
'''
from giantplay.event.util import SelectorEventListener, MultiplexerEventListener
from giantplay.event.basic import PhoneToScreenTouchEventHandler, RotationVectorToAxisEventHandler, \
    RotationVectorToAimEventHandler
from giantplay.games import GameBuilder
from giantplay.games.flyswatter.handler import FlyswatterGameUserHandler
from .game import FlyswatterGame


class FlyswatterGameBuilder(GameBuilder):

    def __init__(self, engine):
        super(FlyswatterGameBuilder, self).__init__(engine)

    def key(self):
        return "flyswatter"

    def name(self):
        return "Flyswatter"

    def build_game(self):
        return FlyswatterGame(self.engine, self)

    def build_user_handler(self, game, user):
        return FlyswatterGameUserHandler(game, user)

    def build_event_listener(self, game, user_handler):
        multi = SelectorEventListener()

        multi.register_listener(('tdown'), PhoneToScreenTouchEventHandler(user_handler, user_handler))
        multi.register_listener(('rotvec'), RotationVectorToAimEventHandler(user_handler, user_handler))

        return multi, ()
