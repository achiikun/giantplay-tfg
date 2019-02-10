'''
Created on 27 oct. 2018

@author: Achi
'''
import json
import logging
import traceback
import time

from giantplay.cfg import ADMIN_KEY
from giantplay.event import Event
from giantplay.utils.time import Speedometer


class User:
    
    def __init__(self, manager, comm, dev, key, name, devtype, props):

        self.manager = manager
        self.comm = comm
        self.dev = dev

        self.key = key
        self.name = name
        self.devtype = devtype
        self.props = props

    def __str__(self):
        return self.name


class UserController(object):

    def __init__(self, engine):

        self.engine = engine
        
        self.connections = {}
        
        self.users = []
        self.user_key_generator = 1

        self.message_speedometer = Speedometer("Message Speedometer")

    def send_event(self, user, event):
        if user.comm not in self.connections.keys():
            logging.error('comm was not in self.connections')
            return

        if user.dev not in self.connections[user.comm].keys():
            logging.error('dev was not in self.connections[comm]')
            return

        if user.key not in self.connections[user.comm][user.dev].keys():
            logging.error('user was not in self.connections')
            return

        msg = [user.key, event.key] + event.values

        msg = json.dumps(msg)
        user.comm.send(user.dev, msg)

    def on_device_connected(self, comm, dev):
        logging.info('Device connected')
        if comm not in self.connections.keys():
            self.connections[comm] = {}
        
        if dev not in self.connections[comm].keys():
            self.connections[comm][dev] = {}

    def on_device_disconnected(self, comm, dev):
        logging.info('Device disconnected')
        
        if comm not in self.connections.keys():
            logging.error('comm was not in self.connections')
            return
        
        if dev not in self.connections[comm].keys():
            logging.error('dev was not in self.connections[comm]')
            return

        users = self.connections[comm][dev].values()

        for user in users:
            self.users.remove(user)

        del self.connections[comm][dev]

        for user in users:
            self.engine.notify_user_disconnected(user)

        
        pass 
    
    def on_device_message(self, comm, dev, msg):
        logging.debug('Device message ' + msg)

        self.message_speedometer += 1

        try:

            msg = json.loads(msg)
            
            if isinstance(msg, list):
                # EVENT
                user_key = msg[0]
                event_type = msg[1]
                event_values = msg[2:]
                self.do_event(comm, dev, user_key, event_type, event_values)
                pass
            else:
                # OBJECT
                if 'action' in msg:
                    if msg['action'] == 'login':
                        if 'name' in msg:
                            name = msg['name']
                            devtype = msg['type']
                            props = msg['props']
                            self.do_login(comm, dev, name, devtype, props)
                    elif msg['action'] == 'logout':
                        if 'key' in msg:
                            key = msg['key']
                            self.do_logout(comm, dev, key)
                    elif msg['action'] == 'admin':
                        if 'adminkey' in msg:
                            key = msg['adminkey']
                            self.do_admin(comm, dev, key, msg)
                                
                else:
                    logging.error('Action not found')

        except Exception as e:
            print("Message: ", msg)
            traceback.print_exc()
        
        pass

    def do_event(self, comm, dev, user_key, event_type, event_values):
        logging.debug('do_event: ' + user_key + ': ' + event_type + ' - ' + str(event_values))

        if not comm in self.connections.keys():
            logging.error('comm was not in self.connections')
            return

        if not dev in self.connections[comm].keys():
            logging.error('dev was not in self.connections[comm]')
            return

        if not user_key in self.connections[comm][dev].keys():
            logging.error('key was not in self.connections[comm][dev]')
            return

        user = self.connections[comm][dev][user_key]
        user.last_event_epoch = time.gmtime()

        self.engine.notify_user_event(user, Event(event_type, event_values))

        pass

    def do_login(self, comm, dev, name, devtype, props):
        logging.debug('doLogin: ' + name)

        if comm not in self.connections.keys():
            logging.error('comm was not in self.connections')
            return
        
        if dev not in self.connections[comm].keys():
            logging.error('dev was not in self.connections[comm]')
            return
        
        user = User(self, comm, dev, str(self.user_key_generator), name, devtype, props)
        user.last_event_epoch = time.gmtime()
        self.user_key_generator += 1
        
        self.connections[comm][dev][user.key] = user
        self.users.append(user)
        self.engine.notify_user_connected(user)
        
        msg = json.dumps({"action": "login", "key": user.key, "name": user.name})
        comm.send(dev, msg)
        
        pass
        
    def do_logout(self, comm, dev, key):
        logging.debug('doLogout: ' + key)

        if not comm in self.connections.keys():
            logging.error('comm was not in self.connections')
            return
        
        if not dev in self.connections[comm].keys():
            logging.error('dev was not in self.connections[comm]')
            return
        
        if not key in self.connections[comm][dev].keys():
            logging.error('key was not in self.connections[comm][dev]')
            return
        
        user = self.connections[comm][dev][key]

        self.users.remove(user)
        del self.connections[comm][dev][key]

        self.engine.notify_user_disconnected(user)

        msg = json.dumps({"action": "logout", "key": user.key})
        comm.send(dev, msg)
        
        pass

    def do_admin(self, comm, dev, adminkey, message):

        if adminkey == ADMIN_KEY:

            gbs = []
            for gb in self.engine.game_builders:
                gbs.append({
                    "key": gb.key(),
                    "name": gb.name()
                })

            if 'game' in message.keys():
                for gb in self.engine.game_builders:
                    if gb.key() == message['game']:
                        self.engine.next_game_builder = gb
                        break;

            msg = json.dumps({
                "action": "admin",
                "games": gbs,
                "game": self.engine.game_builder.key() if self.engine.game_builder is not None else None
            })

            comm.send(dev, msg)
