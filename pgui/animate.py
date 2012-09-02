from timer import Timer
from ui import *

class ColorAnimate:
    def __init__(self, color1, color2):
        self.curColor = color1
        self.destColor = color2
        self._end = False
        self.timer = Timer.add(Timer(1./FPS, self.step))

    def step(self, dt):
        if not color_eq(self.curColor, self.destColor):
            self.curColor = step_color(self.curColor, self.destColor)
        elif not self._end:
            self._end = True
            Timer.remove(self.timer)

    def get(self):
        return self.curColor

    def is_end(self):
        return self._end
