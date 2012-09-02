from timer import Timer
from ui import *

class Animate:
    def __init__(self, v1, v2):
        self.v = v1
        self.v1 = v2
        self._end = False
        self.timer = Timer.add(Timer(1./FPS, self.step))

    def step(self, dt):
        pass

    def get(self):
        return self.v

    def is_end(self):
        return self._end

    def finish(self):
        if not self._end:
            self._end = True
            self.v = self.v1
            Timer.remove(self.timer)

class ColorAnimate(Animate):
    def step(self, dt):
        if not color_eq(self.v, self.v1):
            self.v = step_color(self.v, self.v1)
        else:
            self.finish()

def step_value(v, v1, k=0.5):
    return v + (v1 - v) * k

class ValueAnimate(Animate):
    def __init__(self, v1, v2, thredshold=1.):
        Animate.__init__(self, v1, v2)
        self.thredshold = thredshold
    def step(self, dt):
        self.v = step_value(self.v, self.v1)
        if abs(self.v - self.v1) < self.thredshold:
            self.v = self.v1
            self.finish()

class SizeAnimate(Animate):
    def __init__(self, s1, s2):
        Animate.__init__(self, s1, s2)
        w1, h1 = s1
        w2, h2 = s2
        self.aw = ValueAnimate(w1, w2)
        self.ah = ValueAnimate(h1, h2)
        self.v = s1
        self.v1 = s2
    def step(self, dt):
        self.v = self.aw.get(), self.ah.get()

    def is_end(self):
        return self.aw.is_end() and self.ah.is_end()
