'''
Created on 30 oct. 2018

@author: Achi
'''

ADMIN_KEY = 'olakease'

## general FPS
FPS = 24 # 10 # 20 # 60 #5

## general game width and height
# SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_WIDTH, SCREEN_HEIGHT = int(640*3/2), int(480*3/2)

import logging

logging.basicConfig(level=logging.INFO)

from giantplay.games.flyswatter.builder import FlyswatterGameBuilder
from giantplay.games.dummy.builder import DummyGameBuilder
from giantplay.games.tanks.builder import TanksGameBuilder
from giantplay.games.bricks.builder import BricksGameBuilder

## List of available game builders
GAMES = BricksGameBuilder, TanksGameBuilder, FlyswatterGameBuilder, DummyGameBuilder,

from .comm.wifi import WifiComm

## List of available communication modules
COMMS = WifiComm, #WebSocketComm, #

