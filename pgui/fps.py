from timer import Timer
from label import Label
from ui import *

class FPSMeter(Label):
    AllArgs = update_join(Label.AllArgs, 
            size="(60, 18)",
            bgcolor="(0, 0, 0, 0x88)",
            color="(0xff, 0xff, 0xff, 0xff)",
            )
    INTERVAL = 1.0
    def init(self):
        self.tm = Timer(self.INTERVAL, self.update_fps, 0, 0.1)
        self.fcnt = 0
        Timer.add(self.tm)

    def update_fps(self, *args):
        self.text = 'FPS:%.1f' % (self.fcnt/self.INTERVAL)
        self.fcnt = 0
        # print self.text

    def count(self):
        self.fcnt += 1

    # def redraw(self, *args):
    #     super(FPSMeter, self).redraw(*args)
    #     self._redrawed = 0
    #     self._needRedraw = 0
