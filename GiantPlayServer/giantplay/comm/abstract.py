'''
Created on 27 oct. 2018

@author: Achi
'''
from abc import abstractmethod

class Comm:
    
    def __init__(self, engine):
        self.engine = engine
        
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    @abstractmethod
    def send(self, dev, msg):
        pass
    
    def on_comm_connected(self):
        pass
    
    def on_comm_disconnected(self):
        pass
    
    def on_device_connected(self, dev):
        self.engine.manager.on_device_connected(self, dev)
    
    def on_device_disconnected(self, dev):
        self.engine.manager.on_device_disconnected(self, dev)
    
    def on_device_message(self, dev, msg):
        self.engine.manager.on_device_message(self, dev, msg)
