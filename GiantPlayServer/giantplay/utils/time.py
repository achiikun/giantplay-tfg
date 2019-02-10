import logging
from time import time


class Speedometer:

    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.last_counter = 0
        self.current_time = time()
        self.gap = 5
        self._v = "0"

    def __add__(self, other):
        self.counter += other
        t = time()

        den = (t - self.current_time)
        if den:
            self._v = str((self.counter - self.last_counter) / den)

        if t - self.current_time > self.gap:
            logging.info(self.name + ": " + self._v + " iters/sec")
            self.last_counter = self.counter
            self.current_time = t

        return self

    def __str__(self):
        return self._v