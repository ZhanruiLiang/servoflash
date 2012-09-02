class Timer(object):
    timers = []
    @staticmethod
    def add(timer):
        Timer.timers.append(timer)
        return timer

    @staticmethod
    def remove(timer):
        Timer.timers.remove(timer)

    @staticmethod
    def update_all(dt):
        for tm in Timer.timers:
            tm.update(dt)
        Timer.timers = [tm for tm in Timer.timers if not tm.is_finished()]

    def __init__(self, interval, callback, loop=0, delay=0.):
        self.interval = interval
        self.callback = callback
        self.accu = -delay
        self.loop = loop
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
            self.callback(dt)
            if self.loop > 0:
                self.loop -= 1
            elif self.loop == 1:
                self.loop = -1
            self.accu -= self.interval

    def finish(self):
        self.loop = -1

    def is_finished(self):
        return self.loop < 0
