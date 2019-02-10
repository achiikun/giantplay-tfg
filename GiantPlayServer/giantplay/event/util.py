from abc import abstractmethod

from giantplay.event.abstract import EventListener


class EventListenerFilter(EventListener):

    def __init__(self, delegator, user_handler=None):
        self.delegator = delegator
        self.user_handler = user_handler

    def notify_update(self):
        super().notify_update()

    def delegate_event(self, user_handler, event):
        self.delegator.notify_event(user_handler, event)

    @abstractmethod
    def on_update(self):
        pass

    @abstractmethod
    def on_event(self, user_handler, event):
        pass


class SelectorEventListener(EventListener):

    def __init__(self):
        self.event_listener_map = {}

    def register_listener(self, event_type, listener):
        if isinstance(event_type, str):
            self.event_listener_map[event_type] = listener.notify_event
        else:
            for t in event_type:
                self.event_listener_map[t] = listener.notify_event

    def register_event(self, event_type, listener):
        if isinstance(event_type, str):
            self.event_listener_map[event_type] = listener
        else:
            for t in event_type:
                self.event_listener_map[t] = listener

    def on_event(self, user_handler, event):
        if event.key in self.event_listener_map.keys():
            self.event_listener_map[event.key](user_handler, event)

    @abstractmethod
    def on_update(self):
        pass


class MultiplexerEventListener(EventListener):

    def __init__(self):
        self.event_listeners = []

    def register_listener(self, listener):
        self.event_listeners.append(listener.notify_event)

    def register_event(self, listener):
        self.event_listeners.append(listener)

    def on_event(self, user_handler, event):
        for l in self.event_listeners:
            l(user_handler, event)

    @abstractmethod
    def on_update(self):
        pass
