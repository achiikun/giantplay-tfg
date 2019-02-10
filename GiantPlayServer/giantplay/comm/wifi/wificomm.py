'''
Created on 19 oct. 2018

@author: Achi
'''

from giantplay.comm import Comm
from .physical_device import WifiPhysicalDevice

import socket
from threading import Thread

UDP_IP = "0.0.0.0"
UDP_PORT = 6699


class WifiComm(Comm):
            
    def __init__(self, engine):
        super(WifiComm, self).__init__(engine)
                
        self.udpThread = Thread(target=self._udp_daemon)
        self.tcpThread = Thread(target=self._tcp_daemon)
        self.running = False
        
        self.connections = []

    def start(self):
        print('WifiComm starting')
        self.running = True
        
        self.udpSocket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.udpSocket.bind((UDP_IP, UDP_PORT))
        self.udpThread.start()
        
        self.tcpSocket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_STREAM) # UDP
        self.tcpSocket.bind((UDP_IP, UDP_PORT))
        self.tcpSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.tcpSocket.listen(30)
        self.tcpThread.start()
        
        self.on_comm_connected()
        
        print('WifiComm started')
        pass
    
    def stop(self):
        print('WifiComm stopping')

        self.running = False
        self.udpSocket.close()
        self.udpThread.join(1)
        self.tcpSocket.close()
        self.tcpThread.join(1)
        
        for con in self.connections:
            con.stop()
            
        self.connections.clear()
            
        self.on_comm_disconnected()

        print('WifiComm stopped')
        pass
    
    def send(self, dev, msg):
        dev.send(msg)
        
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
        
    def _tcp_daemon(self):
        
        try:
        
            while self.running:
                sock, addr = self.tcpSocket.accept() # buffer size is 1024 byt
                # sock.setsockopt(  socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                # sock.setblocking(1)
                print("New accept: ", addr)
                
                dev = WifiPhysicalDevice(self, sock)
                self.connections.append(dev)
                
                dev.start()
                                
        except Exception as e:
            print(e)
