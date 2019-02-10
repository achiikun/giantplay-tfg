'''
Created on 29 oct. 2018

@author: Achi
'''
from giantplay.event.util import SelectorEventListener
from giantplay.event.basic import PhoneToScreenTouchEventHandler, RotationVectorToAxisEventHandler
from giantplay.games import GameBuilder
from giantplay.games.tanks.game import TanksGame
from giantplay.games.tanks.handler import TanksGameUserHandler


class TanksGameBuilder(GameBuilder):

    def __init__(self, engine):
        super(TanksGameBuilder, self).__init__(engine)

    def key(self):
        return "tanks"

    def name(self):
        return "Tanks"

    def build_game(self):
        return TanksGame(self.engine, self)

    def build_user_handler(self, game, user):
        return TanksGameUserHandler(game, user)

    def build_event_listener(self, game, user_handler):
        multi = SelectorEventListener()

        multi.register_listener(('tdown', 'tmove', 'tup', 'tpdown'), PhoneToScreenTouchEventHandler(user_handler, user_handler))
        multi.register_listener(('rotvec'), RotationVectorToAxisEventHandler(user_handler, user_handler))

        return multi, ()
