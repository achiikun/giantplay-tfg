from abc import abstractmethod, ABC


class Event:

    def __init__(self, key, values=[]):
        self.key = key
        self.values = values


class EventListener:

    def notify_update(self):
        self.on_update()

    def notify_event(self, user_handler, event):
        self.on_event(user_handler, event)

    @abstractmethod
    def on_update(self):
        """
        Called when a user has thrown an event
        :param user_handler: The UserHandler of the game
        :param event: The Event
        :return:
        """
        pass

    @abstractmethod
    def on_event(self, user_handler, event):
        """
        Called when a user has thrown an event
        :param user_handler: The UserHandler of the game
        :param event: The Event
        :return:
        """
        pass