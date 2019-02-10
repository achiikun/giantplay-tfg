'''
Created on 19 oct. 2018

@author: Achi
'''
import asyncio
import websockets as websockets

from giantplay.comm import Comm

import socket
from threading import Thread

UDP_IP = "0.0.0.0"
UDP_PORT = 6699


class WebSocketComm(Comm):
            
    def __init__(self, engine):
        super(WebSocketComm, self).__init__(engine)
                
        self.udpThread = Thread(target=self._udp_daemon, name="UDP Thread")

        self.tcpThread = Thread(target=self._tcp_daemon, name="TCP Thread")
        self.tcpThread.daemon = True

        self.connections = []

    def start(self):
        print('WifiComm starting')
        self.running = True
        
        self.udpSocket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.udpSocket.bind((UDP_IP, UDP_PORT))
        self.udpThread.start()

        self.tcpThread.start()
        
        self.on_comm_connected()
        
        print('WifiComm started')
        pass
    
    def stop(self):
        print('WifiComm stopping')

        self.running = False
        self.udpSocket.close()
        self.udpThread.join(1)
        self.tcpThread.join(1)
        
        for con in self.connections:
            con.stop()
            
        self.connections.clear()
            
        self.on_comm_disconnected()

        print('WifiComm stopped')
        pass
    
    def send(self, dev, msg):
        asyncio.get_event_loop().run_until_complete(dev.send(msg))

    def on_device_disconnected(self, dev):
        self.connections.remove(dev)
        super().on_device_disconnected(dev)
        
    def _udp_daemon(self):
        
        try:
        
            while self.running:
                data, addr = self.udpSocket.recvfrom(1024) # buffer size is 1024 bytes
                print("received message:", data, addr)
                
                self.udpSocket.sendto(data, addr)
                
                print("sent message:", data, addr)

        except:
            pass

    async def register(self, websocket):
        self.on_device_connected(websocket)

    async def unregister(self, websocket):
        self.on_device_disconnected(websocket)

    async def counter(self, websocket, path):
        # register(websocket) sends user_event() to websocket
        await self.register(websocket)
        try:
            async for message in websocket:
                self.on_device_message(websocket, message)
        finally:
            await self.unregister(websocket)

    def _tcp_daemon(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(self.counter, UDP_IP, UDP_PORT))
        asyncio.get_event_loop().run_forever()