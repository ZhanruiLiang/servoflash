from pgui.ui import *
from pgui import Label, InputBox, Root, warn, hint, DragBar, Timer
from servoproxy import InvalidCommandError, CommandProxy
from saveload import SaveLoadManager
from servoboard import ServoBoard, KeyFrame
import socket
import string
import random
import os
import math
from config import *

def raise_(ex): raise ex

class RulerHead(UIBase):
    def redraw(self, *args):
        image = self.ownImage
        image.fill(COLOR_TRANS)
        pg.draw.polygon(image, self.color,
                [(0, 1), (self.size[0]-1, 1), ((self.size[0]-1)/2, self.size[1]-1)])
        self._redrawed = 1

class Ruler(UIBase):
    fontr = pg.font.Font(os.path.join(RES_DIR, 'MonospaceTypewriter.ttf'), 12)
    COLOR_PLAYING = (0x9b, 0, 0x9e, 0xff)
    COLOR_MARK = (0x0, 0x88, 0x88, 0x3f)
    def init(self):
        self.servoc = self.parent
        self.head = RulerHead(self, color=(0xff, 0, 0, 0xff),
                pos=(-20, 0), size=(8, self.size[1]))
        self._drawnState = None

    def redraw(self, *args):
        servoc = self.servoc
        image = self.ownImage
        self._redrawed = 1
        w0 = servoc.FRAME_WIDTH
        viewpos = servoc.viewpos[0]
        # move the playing head
        self.head.pos = ((servoc.playPos - viewpos) * w0 - w0/2, 0)
        state = (viewpos, servoc.is_playing(), servoc.loopStart, servoc.loopEnd)
        if state != self._drawnState:
            fps = servoc.playFPS
            w, h = self.size
            # start draw from time t0, mark at every second
            t0 = viewpos - (viewpos - 1) % fps + fps - 1
            x = 0
            t = t0
            if servoc.is_playing():
                image.fill(self.COLOR_PLAYING)
            else:
                image.fill(self.bgcolor)
            while x < w:
                x = (t - viewpos) * w0
                # draw vertical ruler
                pg.draw.line(image, self.color, (x, 0), (x, max(2, h-5)))
                # draw the time flag
                image.blit(self.fontr.render('%d' % (t * servoc.timeStep), 1, self.color), (x + 1, 0))
                t += fps
            # draw loop start mark
            if servoc.loopStart is not None:
                image.blit(self.fontr.render("|>", 1, self.color, self.COLOR_MARK), 
                        ((servoc.loopStart - viewpos)*w0 - 4, 0))
            # draw loop end mark
            if servoc.loopEnd is not None:
                image.blit(self.fontr.render("<|", 1, self.color, self.COLOR_MARK), 
                        ((servoc.loopEnd - viewpos)*w0 - 9, 0))

            self._drawnState = state

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
            lambda s: int(s) if -1024 <= int(s) <= 1023 else raise_(ValueError("out of range[-1024, 1024)")),
            lambda s: int(s) if -1024 <= int(s) <= 1023 else raise_(ValueError("out of range[-1024, 1024)")),
            ]
    BG_IMAGE_PATH = 'shot-2012-09-27-cut.png'

    RULER_HEIGHT = 14
    FRAME_WIDTH = ServoBoard.FRAME_WIDTH
    BAR_WIDTH = 14
    MARGIN = 3

    loopStart = 0
    loopEnd = None
    def init(self):
        self.bgImage = pg.image.load(self.BG_IMAGE_PATH).convert()
        self.servos = [ServoBoard(self)]
        # save/load manager
        self.slmgr = SaveLoadManager(self)
        # ruler, the upper line showing time steps, etc.
        self.ruler = Ruler(self, pos=(self.MARGIN, 0), 
                size=(self.size[0]-2*self.MARGIN, self.RULER_HEIGHT),
                color=(0, 0, 0, 0xff),
                bgcolor=(0, 0xff, 0x92, 0xff))
        # setup bars
        self.hbar = DragBar(self,
                value=0,
                minvalue=0,
                maxvalue=1,
                size=(self.size[0], self.BAR_WIDTH),
                pos=(self.MARGIN, self.size[1] - self.BAR_WIDTH),
                blockwidth=40,
                )
        self.vbar = DragBar(self,
                value=0,
                minvalue=0,
                maxvalue=1,
                size=(self.BAR_WIDTH, self.size[1] - self.RULER_HEIGHT),
                pos=(self.size[0] - self.BAR_WIDTH, self.RULER_HEIGHT),
                vertical=True,
                blockwidth=40,
                )
        def hbarCallBack():
            x, y = self.viewpos
            x1 = self.hbar.value
            self.viewpos = x1, y
            x2 = self.get_current_frame()
            if x2 < x1:
                self.goto_frame(x1)
        def vbarCallBack():
            x, y = self.viewpos
            y1 = self.vbar.value
            self.viewpos = x, y1
        self.hbar.bind_on_change(hbarCallBack)
        self.vbar.bind_on_change(vbarCallBack)
        # playPosHinter, the big vertical line
        self.playPosHinter = UIBase(self, pos=(0, 0), size=(5, self.size[1]), 
                bgcolor=(0xff, 0x0f, 0, 0x25))
        # others
        self.actived = 0
        self._playing = False
        self._synced = False
        self.playPos = 0
        self.timeStep = INIT_TIME_STEP
        self.proxy = None
        self.animateTm = None
        self.set_play_FPS(1./self.timeStep)
        # for debug
        self.loopEnd = 20

        self.bind(EV_CLICK, self.on_click)
        self.bind_keys()

    def reset(self):
        if self._playing:
            self.pause()
        if self._synced:
            self.disconnect_robot()
        self.playPos = 0
        self.ruler.mark_redraw()
        self.select_servo(0)

    def bind_keys(self):
        self.bind_key(K_i, self.insert_key_frame)
        self.bind_key(K_i, self.insert_frame, [KMOD_SHIFT])
        self.bind_key(K_d, self.remove_frame)
        self.bind_key(K_d, 
                lambda e: self.remove_servo(self.servos[self.actived]),
                [KMOD_CTRL, KMOD_ALT])
        self.bind_key(K_c, 
                lambda e: self.clear_servo(self.servos[self.actived]),
                [KMOD_CTRL, KMOD_ALT])
        self.bind_key(K_LEFTBRACKET, self.mark_loop_start)
        self.bind_key(K_RIGHTBRACKET, self.mark_loop_end)
        # move view left
        self.bind_key(K_h, lambda e: self.move_view(-1), [KMOD_SHIFT])
        # move view right
        self.bind_key(K_l, lambda e: self.move_view(1), [KMOD_SHIFT])
        # select previous frame
        self.bind_key(K_h, lambda e: self.move_frame(-1))
        # select next frame
        self.bind_key(K_l, lambda e: self.move_frame(1))
        # select next key frame
        self.bind_key(K_w, lambda e: self.next_key_frame())
        # select previous key frame
        self.bind_key(K_b, lambda e: self.prev_key_frame())
        # adjust
        adjSpeed = 20
        self.bind_key(K_j, 
                lambda e: self.servos[self.actived].adjust_curframe(1),
                [KMOD_ALT])
        self.bind_key(K_j, 
                (lambda e: self.servos[self.actived].adjust_curframe(adjSpeed)),
                [KMOD_SHIFT])
        self.bind_key(K_k, 
                lambda e: self.servos[self.actived].adjust_curframe(-1),
                [KMOD_ALT])
        self.bind_key(K_k, 
                lambda e: self.servos[self.actived].adjust_curframe(-adjSpeed),
                [KMOD_SHIFT])
        # select next servo
        self.bind_key(K_j, lambda e: self.select_servo(self.actived + 1))
        # select previous servo
        self.bind_key(K_k, lambda e: self.select_servo(self.actived - 1))

    def next_key_frame(self):
        servo = self.servos[self.actived]
        ti = servo.selected
        i, dti = servo.find_ti_pos(ti)
        tot1 = sum(frame.dti for frame in servo.keyFrames[:i+1])
        self.goto_frame(tot1)

    def prev_key_frame(self):
        servo = self.servos[self.actived]
        ti = servo.selected
        i, dti = servo.find_ti_pos(ti)
        tot1 = sum(frame.dti for frame in servo.keyFrames[:max(0, i-1+bool(dti))])
        self.goto_frame(tot1)

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

    def send_command(self):
        if not self._synced: return
        proxy = self.proxy
        k = K_SPEED
        if proxy:
            try:
                for servo in self.servos:
                    # angle0 = servo.get_a_at(max(self.playPos - 1, 0))
                    angle = servo.get_a_at(self.playPos)
                    # speed = max(50, int(k * abs(angle - angle0) / self.timeStep))
                    if servo.is_safe_angle(angle):
                        adv = servo.angle2ad(angle)
                        proxy.setPosTime(servo.sid, adv, int(1000*self.timeStep))
                    else:
                        interval = servo.min, servo.max
                        warn('%(angle)d out of range, need to be in %(interval)s, in %(self)s' % locals())
                proxy.action()
            except socket.error as ex:
                self.disconnect_robot()
                warn('connection lost:'+str(ex))
            except Exception as ex:
                warn(str(ex))
        else:
            warn("not connected.")

    def animate(self, dt):
        if not self._playing: return
        if self.playPos < self.servos[self.actived].total_frame() or self.playPos < max(s.total_frame() for s in self.servos):
            self.playPos += 1
            if self.playPos - self.viewpos[0] > self.size[1]/ServoBoard.FRAME_WIDTH:
                self.move_view(1)
            elif self.playPos < self.viewpos[0]:
                self.move_view(-1)
            self.ruler.mark_redraw()
            if self._synced:
                self.send_command()

    def on_select(self, servo):
        # stub
        pass

    def on_select_servo(self, servo):
        # stub
        pass

    def play(self):
        self._playing = True
        self.ruler.mark_redraw()

    def pause(self):
        self._playing = False
        self.goto_frame(self.playPos)
        self.ruler.mark_redraw()

    def connect_robot(self):
        if self.proxy is None:
            try:
                self.proxy = CommandProxy()
            except Exception as ex:
                warn('connect proxy failed. %s' % ex)
                self.proxy = None
            else:
                hint('proxy connected')
        if self.proxy is not None:
            for servo in self.servos:
                self.proxy.setMode(servo.sid, 0)
            self.send_command()
            self._synced = True

    def disconnect_robot(self):
        self._synced = False

    @property
    def viewpos(self):
        return self._viewpos

    @property
    def selected(self):
        return self.servos[self.actived].selected

    @property
    def playPos(self):
        return self._playPos

    @playPos.setter
    def playPos(self, p):
        if p == self.loopEnd and self.loopEnd != self.loopStart:
            p = self.loopStart
        self._playPos = p
        self.playPosHinter.pos = V2I(((p + 0.5 - self.viewpos[0]) * self.FRAME_WIDTH - 3, 0))

    @viewpos.setter
    def viewpos(self, v):
        x, y = v
        if hasattr(self, 'servos'): 
            x0, y0 = self._viewpos
            y1 = self.RULER_HEIGHT + self.MARGIN
            for servo in self.servos:
                if servo.viewpos != x:
                    servo.viewpos = x
                    servo.mark_redraw()
                servo.pos = (servo.pos[0], servo.pos[1] + y0 - y)
            self.ruler.mark_redraw()
            if y0 != y:
                self.mark_redraw()
                if self.vbar.value != y:
                    # self.vbar.value = y
                    self.vbar.set_value(y)
        self._viewpos = v

    def move_view(self, d):
        x, y = self.viewpos
        dx = self.size[1] / ServoBoard.FRAME_WIDTH / 1
        self.viewpos = max(0, x + d * dx), y
        self.move_frame(d*dx)
        self.update_bar()

    def update_bar(self):
        servos = self.servos
        self.hbar.maxvalue = max(s.total_frame() for s in servos)
        self.hbar.value = self.viewpos[0]
        self.vbar.maxvalue = len(servos) * (servos[0].size[1] + self.MARGIN)
        self.vbar.value = self.viewpos[1]

    def mark_loop_start(self, *args):
        ti = self.selected
        if ti == self.loopStart:
            self.loopStart = None
        elif ti != self.loopEnd:
            self.loopStart = ti
        else:
            warn("can not set empty loop")
        self.ruler.mark_redraw()

    def mark_loop_end(self, *args):
        ti = self.selected
        if ti == self.loopEnd:
            self.loopEnd = None
        elif ti != self.loopStart:
            self.loopEnd = ti
        else:
            warn("can not set empty loop")
        self.ruler.mark_redraw()

    def insert_key_frame(self, event):
        if self._playing: 
            warn("can not edit when playing")
            return
        servo = self.servos[self.actived]
        servo.insert_key_frame(servo.selected)
        self.update_bar()

    def insert_frame(self, event):
        if self._playing: 
            warn("can not edit when playing")
            return
        servo = self.servos[self.actived]
        servo.insert_frame(servo.selected)
        self.update_bar()

    def remove_frame(self, event):
        if self._playing: 
            warn("can not edit when playing")
            return
        servo = self.servos[self.actived]
        servo.remove_frame(servo.selected)
        self.update_bar()

    def select_servo(self, idx):
        if isinstance(idx, ServoBoard):
            idx = self.servos.index(idx)
        idx = idx % len(self.servos)
        if idx != self.actived:
            self.servos[idx].select(self.servos[self.actived].selected)
            self.servos[self.actived].deactive()
            self.actived = idx
            self.mark_redraw()
        servo = self.servos[idx]
        y1 = servo.pos[1]
        x, y = self.viewpos
        if y1 < self.RULER_HEIGHT + self.MARGIN:
            self.viewpos = x, y + servo.pos[1] - self.RULER_HEIGHT - self.MARGIN
        elif y1 + servo.size[1] > self.size[1] - self.MARGIN:
            self.viewpos = x, y + y1 + servo.size[1] - self.size[1] + self.MARGIN
        servo.active()
        self.on_select_servo(servo)
        hint('switch to %s' % servo.label)

    def new_servos(self, n=6):
        self.remove_servo()
        for i in xrange(n):
            self.add_servo()
            # servo = self.servos[-1]
            # self.servos[-1].keyFrames = ([KeyFrame(5, 0)] + [
            #     KeyFrame(random.randint(1, 10), 
            #         random.randint(servo.min, servo.max)) 
            #     for i in xrange(500)])
        self.actived = 0
        self.servos[0].active()
        self.reset()
        self.mark_redraw()

    def clear_servo(self, *args):
        if self._playing: return warn("can not edit when playing")
        for servo in self.servos:
            del servo.keyFrames[1:]
            servo.keyFrames[0].dti = 10
            servo.mark_redraw()
        self.reset()

    def remove_servo(self, *args):
        if self._playing: return warn("can not edit when playing")
        if len(args) == 0:
            # remove all
            for servo in self.servos:
                servo.destory()
            self.servos = []
        else:
            cnt = len(self.servos)
            for servo in args:
                if cnt > 1 and servo in self.servos:
                    cnt -= 1
                    servo.destory()
            self.servos = [s for s in self.servos if not s._destoryed]
            if self.actived >= len(self.servos):
                self.actived = len(self.servos) - 1
            self.select_servo(self.actived)
        self.mark_redraw()

    def get_current_frame(self):
        return self.servos[self.actived].selected or 0

    def move_frame(self, d):
        self.goto_frame(self.get_current_frame() + d)

    def goto_frame(self, ti):
        servo = self.servos[self.actived]
        if ti < 0:
            ti = 0
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
        if self._synced:
            self.send_command()

    def add_servo(self, servo=None):
        if servo is None:
            servo = ServoBoard(self)
        self.servos.append(servo)
        servo.viewpos = self.viewpos[0]
        ssize = self._cal_servo_size()
        for idx, servo in enumerate(self.servos):
            servo.resize(ssize)
            servo.pos = self._cal_servo_pos(idx)
        self.update_bar()
        self.mark_redraw()

    def _cal_servo_pos(self, idx):
        bw = self.MARGIN
        w0, h0 = self.size
        w = w0 - 2 * bw
        h = (h0 - bw - self.RULER_HEIGHT) / max(1, len(self.servos)) - bw
        h = max(ServoBoard.MIN_HEIGHT, h)
        # (w, h) is the size of a single servo board
        return bw, self.RULER_HEIGHT + bw + idx * (bw + h)

    def _cal_servo_size(self):
        bw = self.MARGIN
        w0, h0 = self.size
        w = w0 - 2 * bw
        h = (h0 - bw - self.RULER_HEIGHT) / max(1, len(self.servos)) - bw
        h = max(ServoBoard.MIN_HEIGHT, h)
        return w, h

    def is_playing(self):
        return self._playing

    def resize(self, nsize):
        super(ServoControl, self).resize(nsize)
        if hasattr(self, 'servos'):
            ssize = self._cal_servo_size()
            for servo in self.servos:
                servo.resize(ssize)

    def redraw(self, *args):
        # print 'redraw main board'
        self._redrawed = 1
        bw = self.MARGIN
        image = self.ownImage
        image.fill(self.bgcolor)
        image.blit(self.bgImage, (0, 0))
        for servo in self.servos:
            if servo.is_actived():
                pg.draw.rect(image, self.color, 
                        ((0, servo.pos[1]-bw), (servo.size[0] + 2*bw, servo.size[1]+2*bw)))
                break

    def on_click(self, event):
        pos = event.pos
        for servo in self.servos:
            if servo.is_under_mouse(pos):
                self.select_servo(servo)
                return
        return True

    def auto_save(self):
        self.slmgr.save(AUTOSAVE_FILE, False)

    def debug_print(self):
        print 'servos:'
        print '\n'.join('%d(t):' % i + str(s) for i, s in enumerate(self.servos))
        print '\n'.join("%s: %s" % x for x in [
            ('actived', self.actived),
            ('_playing', self._playing),
            ('playPos', self.playPos),
            ('selected', self.selected),
            ])

