from pgui.ui import *
from pgui import Label, InputBox, Root, warn, hint, DragBar, Timer
from servoproxy import InvalidCommandError, CommandProxy
from saveload import SaveLoadManager
from servoboard import ServoBoard, KeyFrame
import string
import random
import os
import math

def raise_(ex): raise ex

class ServoControl(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            bgcolor="(0x08, 0x08, 0x08, 255)",
            color="(0x5f, 0xaf, 0xaf, 255)",
            size="(500, 600)",
            viewpos="(0, 0)",
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd, 
            ['viewpos'])
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    SERVO_ATTRS = ['sid', 'label', 'bias', 'direction', 'min', 'max']
    SERVO_ATTR_EVALS = [
            lambda s: int(s) if 1 <= int(s) <= 255 else raise_(ValueError("out of range[1, 255]")),
            lambda s: s if not any(c for c in s if c not in string.letters + string.digits) else raise_(ValueError("invalid")),
            lambda s: int(s) if 0 <= int(s) <= 1023 else raise_(ValueError("out of range[0, 1024)")),
            lambda s: int(s) if int(s) in (-1, 1) else raise_(ValueError("direction must be 1 or -1")),
            lambda s: int(s) if 0 <= int(s) <= 1023 else raise_(ValueError("out of range[0, 1024)")),
            lambda s: int(s) if 0 <= int(s) <= 1023 else raise_(ValueError("out of range[0, 1024)")),
            ]

    RULER_HEIGHT = 14
    FRAME_WIDTH = ServoBoard.FRAME_WIDTH
    BAR_WIDTH = 20
    MARGIN = 3

    def init(self):
        self.servos = [ServoBoard(self)]
        self.slmgr = SaveLoadManager(self)
        self.bind(EV_KEYPRESS, self.on_keypress, BLK_POST_BLOCK)
        self.ruler = Ruler(self, pos=(self.MARGIN, 0), 
                size=(self.size[0], self.RULER_HEIGHT),
                color=(0, 0, 0, 0xff),
                bgcolor=(0, 0xff, 0, 0xff))
        self.hbar = DragBar(self,
                value=0,
                minvalue=0,
                maxvalue=1,
                size=(self.size[0], self.BAR_WIDTH),
                pos=(self.MARGIN, self.size[1] - self.BAR_WIDTH),
                blockwidth=40,
                )
        self.actived = 0
        self._playing = False
        self._synced = False
        self.playPos = 0
        self.timeStep = 0.1
        self.playFPS = 1./self.timeStep

        self.animateTm = None
        self.set_play_FPS(self.playFPS)
        def hbarCallBack():
            x, y = self.viewpos
            x1 = self.hbar.value
            self.viewpos = x1, y
            x2 = self.get_current_frame()
            if x2 < x1:
                self.goto_frame(x1)
        self.hbar.bind_on_change(hbarCallBack)
        self.bind(EV_CLICK, self.on_click)

    def reset(self):
        if self._playing:
            self.pause()
        if self._synced:
            self.disconnect_robot()
        self.playPos = 0
        self.ruler.mark_redraw()
        self.select_servo(0)

    def set_play_FPS(self, fps):
        try:
            # fps must be integer
            fps = int(fps)
        except ValueError as ex:
            warn(str(ex))
            return
        if self.animateTm:
            Timer.remove(self.animateTm)
        self.animateTm = Timer(1./fps, self.animate)
        Timer.add(self.animateTm)
        self.playFPS = fps
        self.timeStep = 1. / fps

    def set_servo(self):
        proxy = self.proxy
        for servo in self.servos:
            angle = servo.get_a_at(self.playPos)
            speed = 512
            if servo.is_safe_angle(angle):
                adv = servo.angle2ad(angle)
                proxy.set_servo_pos(self.id, adv, speed)
            else:
                interval = self.min, self.max
                warn('%(angle)d out of range, need to be in %(interval)s, in %(self)s' % locals())

    def animate(self, dt):
        if not self._playing: return
        self.playPos += 1
        if self.playPos - self.viewpos[0] > self.size[1]/ServoBoard.FRAME_WIDTH:
            self.move_view(1)
        elif self.playPos < self.viewpos[0]:
            self.move_view(-1)
        self.ruler.mark_redraw()
        if self._synced:
            self.set_servo()

    def on_select(self, servo):
        # stub
        pass

    def on_select_servo(self, servo):
        # stub
        pass

    def play(self):
        self._playing = True

    def pause(self):
        self._playing = False
        self.goto_frame(self.playPos)

    def connect_robot(self):
        if self.proxy is None:
            try:
                self.proxy = CommandProxy()
            except Exception as ex:
                warn('connect proxy failed. %s' % ex)
                self.proxy = None
            else:
                hint('proxy connected')
                self._synced = True

    def disconnect_robot(self):
        self._synced = False

    @property
    def viewpos(self):
        return self._viewpos

    @viewpos.setter
    def viewpos(self, v):
        self._viewpos = v
        x, y = v
        if hasattr(self, 'servos'): 
            for servo in self.servos:
                servo.viewpos = x
                servo.mark_redraw()
            self.mark_redraw()
            self.ruler.mark_redraw()

    def move_view(self, d):
        x, y = self.viewpos
        dx = self.size[1] / ServoBoard.FRAME_WIDTH / 1
        self.viewpos = max(0, x + d * dx), y
        self.move_frame(d*dx)
        self.update_bar()

    def update_bar(self):
        self.hbar.maxvalue = max(s.total_frame() for s in self.servos)
        self.hbar.value = self.viewpos[0]

    def on_keypress(self, event):
        key = event.key
        servo = self.servos[self.actived]
        if key in (K_i,):
            # insert key frame
            ti = servo.selected
            if ti is not None:
                i, dti = servo.find_ti_pos(ti)
                a = servo.get_a_at(ti)
                if event.mod & KMOD_SHIFT:
                    servo.insert_frame(ti)
                else:
                    servo.insert_key_frame(ti, a)
                self.update_bar()
        elif key in (K_d, K_DELETE, K_BACKSPACE):
            ti = servo.selected
            if ti is not None:
                servo.remove_frame(ti)
        elif key in (K_h, K_LEFT) and (event.mod & KMOD_SHIFT):
            # move view left
            self.move_view(-1)
        elif key in (K_h, K_LEFT):
            # select previous frame
            self.move_frame(-1)
        elif key in (K_l, K_RIGHT) and (event.mod & KMOD_SHIFT):
            # move view right
            self.move_view(1)
        elif key in (K_l, K_RIGHT):
            # select next frame
            self.move_frame(1)
        elif key in (K_j, K_DOWN) and event.mod & KMOD_SHIFT:
            # adjust increase angle
            if event.mod & KMOD_ALT:
                servo.adjust_curframe(1)
            else:
                servo.adjust_curframe(5)
        elif key in (K_k, K_UP) and event.mod & KMOD_SHIFT:
            # decrease angle
            if event.mod & KMOD_ALT:
                servo.adjust_curframe(-1)
            else:
                servo.adjust_curframe(-5)
        elif key in (K_j, K_DOWN):
            # select next servo
            self.select_servo(self.actived + 1)
        elif key in (K_k, K_UP):
            # select previous servo
            self.select_servo(self.actived - 1)
        else:
            # did not accept this key
            return True

    def select_servo(self, idx):
        if isinstance(idx, ServoBoard):
            idx = self.servos.index(idx)
        idx = idx % len(self.servos)
        if idx != self.actived:
            self.servos[idx].selected = self.servos[self.actived].selected
            self.servos[self.actived].deactive()
            self.servos[idx].active()
            self.actived = idx
            self.on_select_servo(self.servos[idx])
            self.mark_redraw()

        hint('switch to servo#%d' % self.servos[idx].sid)

    def new_servos(self, n=5):
        self.remove_servo()
        for i in xrange(n):
            self.add_servo()
            servo = self.servos[-1]
            self.servos[-1].keyFrames = ([KeyFrame(5, 0)] + [
                KeyFrame(random.randint(1, 10), 
                    random.randint(servo.min, servo.max)) 
                for i in xrange(500)])
        self.actived = 0
        self.servos[0].active()
        self.reset()
        self.mark_redraw()

    def remove_servo(self, *args):
        if len(args) == 0:
            # remove all
            for servo in self.servos:
                servo.destory()
            self.servos = []
        else:
            for servo in args:
                servo.destory()
            self.servos = [s for s in self.servos if not s._destoryed]
        self.mark_redraw()

    def get_current_frame(self):
        return self.servos[self.actived].selected or 0

    def move_frame(self, d):
        self.goto_frame(self.get_current_frame() + d)

    def goto_frame(self, ti):
        servo = self.servos[self.actived]
        if ti < 0:
            ti += servo.total_frame()
        if ti < self.viewpos[0]:
            x, y = self.viewpos
            self.viewpos = ti, y
        else:
            x, y = self.viewpos
            tw = self.size[0]/self.FRAME_WIDTH
            if ti >= self.viewpos[0] + tw:
                self.viewpos = ti - tw + 1, y

        servo.select(ti)
        if not self._playing:
            self.on_select(servo)
            self.playPos = ti
            self.ruler.mark_redraw()

    def add_servo(self, servo=None):
        if servo is None:
            servo = ServoBoard(self)
        self.servos.append(servo)
        servo.viewpos = self.viewpos[0]
        self.update_bar()
        self.mark_redraw()

    def redraw(self, *args):
        self._redrawed = 1
        bw = self.MARGIN
        w0, h0 = self.size
        w = w0 - 2 * bw
        h = (h0 - bw - self.RULER_HEIGHT) / max(1, len(self.servos)) - bw
        h = max(ServoBoard.MIN_HEIGHT, h)
        x, y = bw, self.RULER_HEIGHT + bw - self.viewpos[1]
        image = self.ownImage
        image.fill(self.bgcolor)
        for servo in self.servos:
            if servo.size != (w, h):
                servo.resize((w, h))
            if servo.pos != (x, y):
                servo.pos = x, y
            if servo.is_actived():
                pg.draw.rect(image, self.color, pg.Rect((0, y-bw), (w0, h+2*bw)))
            y += h + bw

    def on_click(self, event):
        pos = event.pos
        for servo in self.servos:
            if servo.is_under_mouse(pos):
                self.select_servo(servo)
                return
        return True

class RulerHead(UIBase):
    def redraw(self, *args):
        image = self.ownImage
        image.fill(COLOR_TRANS)
        pg.draw.polygon(image, self.color,
                [(0, 1), (self.size[0]-1, 1), ((self.size[0]-1)/2, self.size[1]-1)])
        self._redrawed = 1

class Ruler(UIBase):
    fontr = pg.font.Font(os.path.join(RES_DIR, 'MonospaceTypewriter.ttf'), 10)
    def init(self):
        self.servoc = self.parent
        self.head = RulerHead(self, color=(0xff, 0, 0, 0x88),
                pos=(-20, 0), size=(8, self.size[1]))
        self._drawnViewpos = None

    def redraw(self, *args):
        servoc = self.servoc
        w0 = servoc.FRAME_WIDTH
        viewpos = servoc.viewpos[0]
        if viewpos != self._drawnViewpos:
            image = self.ownImage
            fps = servoc.playFPS
            w, h = self.size
            # start draw from time t0, mark at every second
            t0 = viewpos - (viewpos - 1) % fps + fps - 1
            x = 0
            t = t0
            image.fill(self.bgcolor)
            while x < w:
                x = (t - viewpos) * w0
                # draw vertical ruler
                pg.draw.line(image, self.color, (x, 0), (x, max(2, h-5)))
                # draw the time flag
                image.blit(self.fontr.render('%d' % (t * servoc.timeStep), 1, self.color), (x + 1, 0))
                t += fps
            self._drawnViewpos = viewpos
        # draw the playing head
        self.head.pos = ((servoc.playPos - viewpos) * w0 - w0/2, 0)
        self._redrawed = 1
