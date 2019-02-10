'''
Created on 20 oct. 2018

@author: Achi
'''
import time
from threading import Thread
import traceback


class WifiPhysicalDevice(Thread):

    def __init__(self, comm, sock):
        super(WifiPhysicalDevice, self).__init__()
        '''
        Constructor
        '''
        self.comm = comm
        self.socket = sock;
        self.connected = False

    def start(self):
        self.connected = True
        Thread.start(self)
        
    def stop(self):
        self.connected = False
        self.socket.close()
        self.join(1)
    
    def send(self, msg):
        
        try:

            totalsent = 0
            msg += '\n'
            msg = msg.encode('utf-8')
            
            while totalsent < len(msg):
                sent = self.socket.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
            
        except Exception:
            traceback.print_exc()

    def on_message(self, msg):
        self.comm.on_device_message(self, msg)
        pass

    '''
    def runOld(self):
        
        self.comm.on_device_connected(self)
        
        try:
            
            buf_size = 4096
            
            chunks = []
            while self.connected:
                chunk = self.socket.recv(buf_size)
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                
                if not chunk:
                    if chunks:
                        self.on_message(b''.join(chunks))
                    break

                if b'\n' not in chunk:
                    chunks.append(chunk)
                    continue

                chunk = chunk.split(b'\n')
                if chunks:
                    self.on_message(b''.join(chunks.append((chunk[0]))))
                else:
                    self.on_message(chunk[0])

                for line in chunk[1:-1]:
                    self.on_message(line)

                if chunk[-1]:
                    chunks = [chunk[-1]]
                else:
                    chunks = []
            
            
        except Exception:
            traceback.print_exc()
        
        self.comm.on_device_disconnected(self)

        pass
    '''

    def run(self):

        self.comm.on_device_connected(self)

        try:

            myfile = self.socket.makefile('r', buffering=None, newline='')

            while self.connected:
                line = myfile.readline()
                if not line:
                    time.sleep(0.05)
                    self.connected = False
                    continue

                self.on_message(line)

        except Exception:
            traceback.print_exc()

        self.comm.on_device_disconnected(self)

        pass
