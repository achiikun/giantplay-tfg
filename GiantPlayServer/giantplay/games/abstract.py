'''
Created on 27 oct. 2018

@author: Achi
'''
import random

import pygame

from giantplay.event.util import SelectorEventListener
from giantplay.utils.time import Speedometer
from abc import abstractmethod
import binascii

colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
          '#008080', '#e6beff', '#9a6324', '#800000', '#aaffc3', '#808000', '#000075', '#808080',
           '#000000'] # '#fffac8', '#ffd8b1', '#ffffff',


class UserHandler(SelectorEventListener):

    def __init__(self, game, user):
        super(UserHandler, self).__init__()
        self.user = user
        self.game = game

        self.speedometer = Speedometer("UserHandler %s Speedometer" % self.name)

    @property
    def name(self):
        return self.user.name

    def send_event(self, event):
        self.game.send_event(self, event)

    def on_event(self, user_handler, event):
        self.speedometer += 1
        super().on_event(user_handler, event)

    @abstractmethod
    def on_update(self):
        pass


class GameBuilder:

    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def key(self):
        return

    @abstractmethod
    def name(self):
        return

    @abstractmethod
    def build_game(self):
        return

    @abstractmethod
    def build_user_handler(self, game, user):
        return

    @abstractmethod
    def build_event_listener(self, game, user_handler):
        return


class Game:

    def __init__(self, engine, game_builder):
        self.engine = engine
        self.game_builder = game_builder
        self.connected_users = {}
        self.color_counter = random.randint(0, len(colors)-1)

    def next_color(self):
        color = colors[self.color_counter]
        self.color_counter += 1
        if self.color_counter >= len(colors):
            self.color_counter = 0
        return pygame.color.Color(*[x for x in binascii.unhexlify(color[1:])])

    def rand_color(self):
        color = colors[random.randint(0, len(colors)-1)]
        return pygame.color.Color(*[x for x in binascii.unhexlify(color[1:])])

    @abstractmethod
    def start(self):
        """
        Starts the game after connect the initial users.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stops the game.
        """
        pass

    @abstractmethod
    def on_update(self):
        """
        Update the event handlers and the objects.
        """
        pass

    @abstractmethod
    def on_render(self, g):
        """
        Render the screen. Remember that when running this function no event will enter.
        :param g: the GraphixController of the engine.
        """
        pass

    @abstractmethod
    def on_user_connected(self, user_handler):
        """
        Called when a new user is connected even if the game is stopped.
        :param user_handler: The user handler created by the builder of this game.
        """
        pass

    @abstractmethod
    def on_user_disconnected(self, user_handler):
        """
        Called when a user is disconnected even if the game has been stopped
        :param user_handler: The UserHandler created by the builder of this game.
        """
        pass

    @property
    def users(self):
        """
        Returns all connected UserHandlers in form of an iterator.
        :return: the iterable of UserHandler
        """
        for k, v in self.connected_users.items():
            yield v[0]

    def notify_update(self):

        for k, v in self.connected_users.items():
            handler, first_node, update_tuple = v
            for node in update_tuple:
                node.notify_update()
            handler.notify_update()

        self.on_update()

    def notify_render(self, g):
        self.on_render(g)

    def notify_user_connected(self, user):
        """
        Called by the engine to notice of a new user is connected.
        This function creates a game-specific handler and a stack of event handler.
        :param user: the raw User
        """

        handler = self.game_builder.build_user_handler(self, user)
        first_node, update_tuple = self.game_builder.build_event_listener(self, handler)
        self.connected_users[user] = (handler, first_node, update_tuple)
        self.on_user_connected(handler)

        pass

    def notify_user_disconnected(self, user):
        """
        Called by the engine to notice of a user that has been disconnected.
        :param user: the raw User
        :return:
        """
        handler, first_node, update_tuple = self.connected_users[user]
        del self.connected_users[user]
        self.on_user_disconnected(handler)

        pass

    def notify_user_event(self, user, event):
        """
        Called by the engine to notice of an event.
        :param user: the raw User
        :param event: the raw Event
        """
        handler, first_node, update_tuple = self.connected_users[user]
        first_node.notify_event(handler, event)

    def send_event(self, user_handler, event):
        self.engine.send_event(user_handler.user, event)
