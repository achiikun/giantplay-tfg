import logging
import math

import numpy as np
import pyquaternion as pyquaternion

from giantplay.event import Event
from giantplay.event.util import EventListenerFilter
from giantplay.utils import vectorutils
from giantplay.utils.quaternion import Quaternion, Quaternion2


class PhoneToScreenTouchEventHandler(EventListenerFilter):

    def __init__(self, delegator, user_handler):
        super().__init__(delegator, user_handler)
        self.screenw = user_handler.user.props['screenw']
        self.screenh = user_handler.user.props['screenh']

    def on_event(self, user_handler, event):
        from giantplay import cfg
        if event.key in ("tdown", "tmove", "tup", "tpdown", "tpmove", "tpup"):
            event.values = (
                event.values[1] * cfg.SCREEN_WIDTH / self.screenh,
                cfg.SCREEN_HEIGHT - event.values[0] * cfg.SCREEN_HEIGHT / self.screenw
            )

            self.delegate_event(user_handler, event)

    def on_update(self):
        pass


class RotationVectorToAimEventHandler(EventListenerFilter):

        def __init__(self, delegator, user_handler):
            super().__init__(delegator, user_handler)
            self.looking = None
            self.offsetQuat = Quaternion(axis=(0, 0, 1), angle=0)

        def on_event(self, user_handler, event):
            self.delegate_event(user_handler, event)

            from giantplay import cfg
            from giantplay.utils.vectorutils import angle
            if event.key in ("rotvec"):

                xmin, xmax, ymin, ymax = -0.3, 0.3, -0.3, 0.3
                qRaw = Quaternion(array=(event.values[3], event.values[0], event.values[1], event.values[2]))
                qRaw = self.offsetQuat.rotate(qRaw)

                lookingRaw = qRaw.rotate(np.array([0, 0, -1]))

                if lookingRaw[1] > 0:

                    aimY = np.interp(-lookingRaw[2], (ymin, ymax), (0, cfg.SCREEN_HEIGHT))
                    aimX = np.interp(lookingRaw[0], (xmin, xmax), (0, cfg.SCREEN_WIDTH))

                    if lookingRaw[0] < xmin:
                        angle = angle([lookingRaw[0], lookingRaw[1]],[xmin, lookingRaw[1]])
                        self.offsetQuat *= Quaternion(axis=[0,0,1], angle=-angle)

                    if lookingRaw[0] > xmax:
                        angle = angle([lookingRaw[0], lookingRaw[1]], [xmax, lookingRaw[1]])
                        self.offsetQuat *= Quaternion(axis=[0, 0, 1], angle=angle)

                    event = Event('aim', (aimX, aimY))
                    self.delegate_event(user_handler, event)

                else:

                    if lookingRaw[0] < 0:
                        a = np.pi/2 - angle([lookingRaw[0], lookingRaw[1]],[xmin, lookingRaw[1]])
                        a = a + angle([lookingRaw[0], lookingRaw[1]],[-1, lookingRaw[1]])
                        self.offsetQuat *= Quaternion(axis=[0,0,1], angle=-a)

                    if lookingRaw[0] > 0:
                        a = np.pi/2 - angle([lookingRaw[0], lookingRaw[1]], [xmax, lookingRaw[1]])
                        a = a + angle([lookingRaw[0], lookingRaw[1]],[1, lookingRaw[1]])
                        self.offsetQuat *= Quaternion(axis=[0, 0, 1], angle=a)

        def on_update(self):
            pass


class RotationVectorToAxisEventHandler(EventListenerFilter):

    def __init__(self, delegator, user_handler):
        super().__init__(delegator, user_handler)
        self.looking = None
        self.offsetQuat = Quaternion(axis=(0, 0, 1), angle=0)

    def on_event(self, user_handler, event):
        self.delegate_event(user_handler, event)

        from giantplay import cfg
        from giantplay.utils.vectorutils import angle
        if event.key in ("rotvec"):

            xmin, xmax, ymin, ymax = -0.5, 0.5, -0.5, 0.5
            qRaw = Quaternion(array=(event.values[3], event.values[0], event.values[1], event.values[2]))

            #lookingRaw1 = qRaw.rotate(np.array([1, 0, 0]))

            a = qRaw.yaw_pitch_roll[0];
            #angle([0,1], [lookingRaw1[0], lookingRaw1[1]])

            #logging.warning("vector: %s %f %f", [lookingRaw1[0], lookingRaw1[1]], a, qRaw.angle)

            lookingRaw = qRaw.rotate(np.array([0, 0, -1]))
            lookingRaw1 =  Quaternion(axis=[0, 0, -1], radians=a).rotate(lookingRaw)

            #logging.warning("looking: %s", [lookingRaw[0], lookingRaw[1], lookingRaw[2]])
            #logging.warning("looking1: %s", [lookingRaw1[0], lookingRaw1[1], lookingRaw1[2]])

            #if True or lookingRaw1[2] < 0:

            aimX = np.interp(lookingRaw1[1], (xmin, xmax), (-1, 1))
            aimY = np.interp(lookingRaw1[0], (ymin, ymax), (-1, 1))

            event = Event('axis', (aimX, aimY))
            self.delegate_event(user_handler, event)

            #else:

            #   event = Event('axis', (0, 0))
            #  self.delegate_event(user_handler, event)

    def on_update(self):
        pass