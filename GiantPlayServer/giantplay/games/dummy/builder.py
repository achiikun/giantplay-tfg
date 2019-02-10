'''
Created on 29 oct. 2018

@author: Achi
'''
from giantplay.event.util import SelectorEventListener, MultiplexerEventListener
from giantplay.event.basic import PhoneToScreenTouchEventHandler, RotationVectorToAxisEventHandler, \
    RotationVectorToAimEventHandler
from giantplay.games import GameBuilder
from giantplay.games.dummy.game import DummyGame
from giantplay.games.flyswatter.game import FlyswatterGame
from giantplay.games.dummy.handler import DummyGameUserHandler


class DummyGameBuilder(GameBuilder):

    def __init__(self, engine):
        super(DummyGameBuilder, self).__init__(engine)

    def key(self):
        return "dummygame"

    def name(self):
        return "Dummy Game"

    def build_game(self):
        return DummyGame(self.engine, self)

    def build_user_handler(self, game, user):
        return DummyGameUserHandler(game, user)

    def build_event_listener(self, game, user_handler):
        multi = SelectorEventListener()
        multi.register_listener(('tdown', 'tmove', 'tup'), PhoneToScreenTouchEventHandler(user_handler, user_handler))

        multiend = MultiplexerEventListener()
        multiend.register_listener(RotationVectorToAimEventHandler(user_handler, user_handler))
        multiend.register_listener(RotationVectorToAxisEventHandler(user_handler, user_handler))

        multi.register_listener(('rotvec'), multiend)

        return multi, ()
