'''
Created on 27 oct. 2018

@author: Achi
'''
import math
import queue
import time
from queue import Queue

from giantplay.utils.rwlock import RWLock
from . import controller, cfg
from .utils.graphics import GraphixController

import logging
import threading

class Engine:
    
    def __init__(self):
        self.manager = controller.UserController(self)
        
        self.communication = []
        self.game_builders = []

        self.next_game_builder = None
        self.game_builder = None
        self.game = None
        self.running = False
        
        for comm in cfg.COMMS:
            self.communication.append(comm(self))
        
        for gb in cfg.GAMES:
            builder = gb(self)
            self.game_builders.append(builder)

        self.next_game_builder = self.game_builders[0]

        self.fps_log_file = open("../fpslog.txt","a")

        self.graphics = GraphixController(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT, cfg.FPS)

        self.renderLock = RWLock()

        self.eventQueue = Queue()

    def start(self):

        self.graphics.init_graphix()

        self.running = True

        for comm in self.communication:
            comm.start()

    def run(self):

        time_to_wait = 1. / cfg.FPS

        fpsQueue = []
        minFPS = 100
        maxFPS = 0

        while self.running:

            t = time.time()

            retvalue = self.graphics.handle_graphix_events()

            if retvalue == 1:
                self.running = False
                break
            elif retvalue == 2:
                print("reset " + str(len(self.manager.users)))
                minFPS = 100
                maxFPS = 0
                fpsQueue = []
                self.fps_log_file.write("----------------------- " + str(len(self.manager.users)) + '\n')
                self.fps_log_file.flush()

            self.renderLock.w_acquire()

            if self.next_game_builder is not None:
                self.swap_games()

            if self.game is not None:
                self.game.notify_update()
                self.game.notify_render(self.graphics)

            self.graphics.draw_graphix()

            self.renderLock.w_release()

            t2 = time.time()
            wait = max(time_to_wait - (t2-t), 0)
            #logging.info("wait: " + str(wait))

            tcheck = time.time()

            try:

                user, event = self.eventQueue.get(block=True, timeout=wait)
                while event:
                    if self.game is not None:
                        self.game.notify_user_event(user, event)

                    t2 = time.time()
                    wait = max(time_to_wait - (t2 - t), 0)
                    user, event = self.eventQueue.get(block=True, timeout=wait)

            except queue.Empty:
                #logging.info("TCheck: " + str(time.time()-tcheck))
                pass

            #self.graphics.tick_graphix()

            lastT = time.time()

            if lastT-t > 0:
                realfps = 1./(lastT-t)

                if minFPS > realfps:
                    minFPS = realfps

                if maxFPS < realfps:
                    maxFPS = realfps

                fpsQueue.append(realfps)

                if len(fpsQueue) > 5:
                    sum = 0
                    for q in fpsQueue:
                        sum += q
                    sum /= len(fpsQueue)
                    self.fps_log_file.write(str(sum) + " " + str(minFPS) + " " + str(maxFPS) + '\n')
                    self.fps_log_file.flush()
                    print(str(sum) + " " + str(minFPS) + " " + str(maxFPS))
                    #fpsQueue.pop(0)

        self.next_game_builder = None
        self.swap_games()

    def stop(self):
        
        self.running = False
        self.graphics.quit_graphix()
        
        for comm in self.communication:
            comm.stop()

    def send_event(self, user, event):
        self.manager.send_event(user, event)

    def notify_user_connected(self, user):
        logging.info("User logged in: " + str(user))
        self.renderLock.r_acquire()
        if self.game is not None:
            self.game.notify_user_connected(user)
        self.renderLock.r_release()
        pass 
    
    def notify_user_disconnected(self, user):
        self.renderLock.r_acquire()
        if self.game is not None:
            self.game.notify_user_disconnected(user)
        self.renderLock.r_release()
        pass 
    
    def notify_user_event(self, user, event):
        # self.renderLock.r_acquire()
        # print("put ", time.time())
        self.eventQueue.put((user, event))
        # self.game.notify_user_event(user, event)
        # self.renderLock.r_release()
        pass

    def set_reset_game(self):
        self.next_game_builder = self.game_builder

    def swap_games(self):

        if self.game is not None:
            for user in self.manager.users:
                self.game.notify_user_disconnected(user)

            self.game.stop()
            self.game_builder = None
            self.game = None

        if self.next_game_builder is not None:
            self.game_builder = self.next_game_builder
            self.next_game_builder = None

            self.game = self.game_builder.build_game()
            self.game.start()

            for user in self.manager.users:
                self.game.notify_user_connected(user)

        pass
