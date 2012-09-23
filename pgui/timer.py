import pygame as pg
class Timer(object):
    timers = []
    clock = pg.time.Clock()
    @staticmethod
    def add(timer):
        Timer.timers.append(timer)
        return timer

    @staticmethod
    def remove(timer):
        if timer in Timer.timers:
            Timer.timers.remove(timer)

    @staticmethod
    def update_all():
        dt = Timer.clock.tick()/1000.
        Timer.timers = [tm for tm in Timer.timers if not tm.is_finished()]
        for tm in Timer.timers:
            tm.update(dt)

    def __init__(self, interval, callback, loop=0, delay=0.):
        assert interval > 0, "interval should be positive"
        self.interval = interval
        self.callback = callback
        self.accu = -delay
        self.loop = int(loop)
        self.running = True

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def stop(self):
        self.accu = 0
        self.running = True

    def update(self, dt):
        if not self.running: return
        self.accu += dt
        while self.accu >= self.interval:
            if self.callback.func_code.co_argcount == 2:
                self.callback(dt)
            else:
                self.callback()
            if self.loop == 1:
                self.loop = -1
            elif self.loop > 0:
                self.loop -= 1
            self.accu -= self.interval

    def finish(self):
        self.loop = -1

    def is_finished(self):
        return self.loop < 0
