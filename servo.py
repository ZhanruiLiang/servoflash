from pgui.ui import *
import random
import yaml
import cPickle
import os
import shutil

TIME_STEP = 0.02

class KeyFrame:
    def __init__(self, dti, a):
        self.dti = max(1, dti)
        self.a = a
    def __repr__(self):
        return 'frame(a=%d, dti=%d)' % (self.a, self.dti)

class ServoBoard(UIBase):
    LIGHT_COLOR = (204, 178, 181, 0xff)
    LIGHT_COLOR2 = (220, 200, 193, 0xff)
    DARK_COLOR = (0, 33, 66, 0xff)
    POINT_COLOR = (0xff, 0, 0, 0xff)
    AllArgs = update_join(UIBase.AllArgs, 
            selectcolor='(0, 160, 245, 255)',
            bgcolor='(250, 250, 200, 255)',
            sid='0', # servo id
            bias='0', # servo bias, such that: bias + direction * angle * (1024/360) = actualADValue
            direction='1', 
            viewpos='0', # time index
            interval='(0, 1023)', # the angle interval
            framewidth='10',
            )

    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['selectcolor', 'framewidth', 'sid', 'bias', 'interval', 'direction', 'viewpos']
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    @staticmethod
    def connect():
        #TODO: connect to server
        pass

    def init(self):
        #  a0    |                              
        #  |     a1                             
        #  |     |                              
        #  0-t0--1--t1----                      
        #                                       
        self.keyFrames = [KeyFrame(5, 0)]
        # add many keyFrames randomly, for test purpose only
        self.keyFrames = ([KeyFrame(5, 0)] + [
            KeyFrame(random.randint(1, 10), random.randint(0, 300)) for i in xrange(20)])
        # self.keyFrames = [KeyFrame(5, 0), KeyFrame(3, 120), KeyFrame(4, 50)]
        self.playingPos = None

        self.bgImage = self.image.copy()
        self._redraw_bg()
        self._actived = False
        self.selected = None # the selected frame

        # self.bind(EV_MOUSEDOWN, self.start_drag)
        # self.bind(EV_MOUSEUP, self.end_drag)
        # self.bind(EV_MOUSEOUT, self.end_drag)
        # self.bind(EV_DRAGOVER, self.on_drag)

    def angle2ad(self, angle):
        return int(self.bias + self.direction * angle * 1024 / 300)

    def ad2angle(self, ad):
        return (ad - self.bias)/self.direction * 300 / 1024

    def is_safe_angle(self, angle):
        l, r = self.interval
        return l <= angle <= r 

    def get_a_at(self, ti):
        """
        The the a value at time ti
        """
        i, dti = self.find_ti_pos(ti)
        if i + 1 < len(self.keyFrames):
            f1 = self.keyFrames[i]
            f2 = self.keyFrames[i+1]
            return int(f1.a + (f2.a - f1.a) / f2.dti * dti)
        else:
            print 'warning: time %(ti)s not in range.' % locals()
            return self.keyFrames[i].a

    def select_at(self, pos):
        ti, a = self.screen_pos_to_ta(pos)
        self.selected = ti

    def insert_key_frame(self, ti, a):
        """
        insert key frame at time ti, with value a
        """
        i, dti = self.find_ti_pos(ti)
        keyFrames = self.keyFrames
        if i < len(keyFrames):
            newFrame = KeyFrame(keyFrames[i].dti - dti, a)
            keyFrames[i].dti = max(1, dti)
        else:
            newFrame = KeyFrame(1, a)
            keyFrames[-1].dti += dti
        keyFrames.insert(i + 1, newFrame)
        self.mark_redraw()

    def set_as_key_frame(self, ti):
        """
        set the frame at time ti as key frame
        """
        self.insert_key_frame(ti, self.get_a_at(ti))
        self.remove_frame(ti + 1)
        self.mark_redraw()

    def insert_frame(self, ti, cnt=1):
        i, dti = self.find_ti_pos(ti)
        if i < len(self.keyFrames):
            self.keyFrames[i].dti += cnt
        else:
            self.keyFrames[i-1].dti += dti
        self.mark_redraw()

    def remove_frame(self, ti, cnt=1):
        i, dti = self.find_ti_pos(ti)
        if cnt > 1:
            j, dtj = self.find_ti_pos(ti + cnt - 1)
        if i < len(self.keyFrames):
            self.keyFrames[i].dti = dti
            if cnt > 1:
                if j < len(self.keyFrames):
                    self.keyFrames[i].dti += self.keyFrames[j].dti - dtj
        self.mark_redraw()

    def _redraw_bg(self):
        image = self.bgImage
        image.fill(self.bgcolor)
        w, h = self.size
        w1 = self.framewidth
        # draw the enclosing box rect
        pg.draw.rect(image, self.LIGHT_COLOR2, ((0, 0), (w, h)), 2)
        pg.draw.rect(image, self.LIGHT_COLOR, ((0, 0), (w, h)), 1)
        for x in xrange(0, w, w1):
            # draw a vertical line
            # pg.draw.line(image, self.LIGHT_COLOR2, (x, 0), (x, h), 2)
            pg.draw.line(image, self.LIGHT_COLOR, (x - w1/2, 0), (x - w1/2, h), 1)


    def redraw(self, *args):
        if self.bgImage.get_size() != self.ownImage.get_size():
            self.bgImage = self.ownImage.copy()
            self._redraw_bg()
        image = self.ownImage
        image.fill(COLOR_TRANS)
        image.blit(self.bgImage, (0, 0))
        i0, dti0 = self.find_ti_pos(self.viewpos)
        w, h = self.size
        w1 = self.framewidth

        if self.selected is not None:
            # draw selected
            x = int(w1 * (self.selected - self.viewpos - 0.5))
            pg.draw.rect(image, self.selectcolor, ((x, 1), (max(1, w1), max(1, h-2))))
        t0 = -self.viewpos
        for i in xrange(0, i0):
            t0 += self.keyFrames[i].dti
        # draw vertical lines
        t = t0
        n = len(self.keyFrames)
        prev = None
        for i in xrange(i0, n):
            frame = self.keyFrames[i]
            x = t * w1
            # the current point
            cur = (x, self.a_to_screen(frame.a))
            if prev is not None:
                # link the prev point with current point
                pg.draw.line(image, self.color, prev, cur, 2)
            # draw the vertical dark line
            pg.draw.line(image, self.DARK_COLOR, (x, 0), (x, h), 1)
            t += frame.dti
            prev = cur
            if x > w: break
        # draw dots
        t = t0
        for i in xrange(i0, n):
            frame = self.keyFrames[i]
            x = t * w1
            cur = (x, self.a_to_screen(frame.a))
            rect = pg.Rect((0, 0), (5, 5))
            rect.center = cur
            pg.draw.rect(image, self.POINT_COLOR, rect)
            t += frame.dti
            if x > w: break

        self._redrawed = 1

    def screen_pos_to_ta(self, pos):
        """
        convert the screen pos to (ti, a) pair

        (t - viewpos) * framewidth = x
        a / 360 * height = y
        """
        x, y = pos
        ti = int(x / self.framewidth + self.viewpos)
        a = int(y * 360 / self.size[1])
        return ti, a

    def on_click(self, event):
        pos = self.get_local_pos_at(event.pos)
        ti, a = self.screen_pos_to_ta(pos)
        print 'click at frame', ti, a
        self.insert_key_frame(ti, a)

    def a_to_screen(self, a):
        return int(a * self.size[1] / 360)

    def find_ti_pos(self, ti):
        """ find index i that keyFrames[i] <= ti < keyFrames[i+1]
            if ti > = keyFrames[-1], return (len(keyFrames), ti - t)
            return: (i, tj) that sum(keyFrames[k] for k in [0...i]) + tj = ti
        """
        t = 0
        for i, frame in enumerate(self.keyFrames):
            if ti < t + frame.dti:
                return i, ti - t
            t += frame.dti
        return i + 1, ti - t

    def set_servo(self, angle, speed):
        l, r = self.interval
        if l <= angle <= r:
            adv = self.angle2ad(angle)
            ServoBoard.set_servo_pos(self.id, adv, speed)
        else:
            print '%(angle)d out of range, need to be in %(interval)s, in %(self)s' % locals()

    def play(self):
        pass

    def start_drag(self, event):
        if event.type == MOUSEMOTION or \
                event.type == MOUSEBUTTONDOWN and event.button == BTN_MOUSELEFT:
            # self._dragging = True
            self._dragStartPos = event.pos
            self._viewpos0 = self.viewpos

    def end_drag(self, event):
        # self._dragging = False
        self._dragStartPos = None

    def on_drag(self, event):
        if self._dragStartPos is None: 
            self.start_drag(event)
        else:
            dx, dy = V2I(event.pos) - self._dragStartPos
            self.viewpos =  max(0, self._viewpos0 - dx / self.framewidth)
            self.mark_redraw()

    def active(self):
        if not self._actived:
            self._actived = True
            # TODO: animation
            self.mark_redraw()

    def deactive(self):
        if self._actived:
            self._actived = False
            self.selected = None
            # TODO: animation
            self.mark_redraw()

    def is_actived(self):
        return self._actived;

class ServoControl(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            bgcolor="(0, 0, 0, 255)",
            color="(0, 0xff, 0, 255)",
            size="(500, 600)",
            )
    def init(self):
        self.servos = [ServoBoard(self)]
        self.actived = 0
        self.bind(EV_KEYPRESS, self.on_keypress, BLK_POST_BLOCK)

    def on_keypress(self, event):
        key = event.key
        servo = self.servos[self.actived]
        if key in (K_i,):
            # insert key frame
            ti = servo.selected
            if ti is not None:
                i, dti = self.find_ti_pos(ti)
                a = servo.keyFrames[i].a
                servo.insert_key_frame(ti, a)
        elif key in (K_h, K_LEFT):
            # select previous frame
            ti = servo.selected
            if ti is None:
                ti = sum(f.dti for f in servo.keyFrames) - 1
            else:
                ti = max(0, ti - 1)
            servo.selected = ti
            servo.mark_redraw()
        elif key in (K_l, K_RIGHT):
            # select next frame
            ti = servo.selected
            if ti is None:
                ti = 0
            else:
                ti += 1
            servo.selected = ti
            servo.mark_redraw()
        elif key in (K_j, K_DOWN):
            # select next servo
            self.select_servo(self.actived + 1)
        elif key in (K_k, K_UP):
            self.select_servo(self.actived - 1)
        else:
            # did not accept this key
            return True

    def select_servo(self, idx):
        idx = idx % len(self.servos)
        self.servos[idx].selected = self.servos[self.actived].selected
        self.servos[self.actived].deactive()
        self.servos[idx].active()
        self.actived = idx
        self.mark_redraw()

    def new_servos(self):
        self.remove_servo()
        for i in xrange(6):
            self.add_servo(ServoBoard(self))
        self.actived = 0
        self.servos[0].active()
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

    def load_servos(self, filename):
        with open(filename, 'rb') as f:
            data = cPickle.load(f)
        servosData = data['servos']
        self.remove_servo()
        for adata in servosData:
            keyFrames = adata['keyFrames']
            del adata['keyFrames']
            servo = ServoBoard(self, **adata)
            for a, dti in keyFrames:
                servo.keyFrames.append(KeyFrame(dti, a))
            self.add_servo(servo)
        self.mark_redraw()

    def add_servo(self, servo):
        self.servos.append(servo)

    SAVE_ATTRS = ['sid', 'bias', 'direction', 'interval']
    def save_servos(self, filename):
        if os.path.exists(filename):
            # file exist, backup
            self.backup_file(filename)
        data = {}
        data['servos'] = servosData = []
        for servo in self.servos:
            adata = {}
            for attr in self.SAVE_ATTRS:
                adata[attr] = getattr(servo, attr)
            adata['keyFrames'] = [(kf.a, kf.dti) for kf in servo.keyFrames]
            servosData.append(adata)
        with open(filename, 'wb') as f:
            cPickle.dump(data, f, -1)
            print 'save data to file "%s"' % filename

    def backup_file(self, filename):
        MaxBackupNum = 5
        files = []
        for i in xrange(maxBackupNum):
            backupName = '.%s.~%d~' % (filename, i+1)
            if not os.path.exists(backupName):
                break
            files.append((os.stat(backupName).st_ctime, backupName))
        else:
            files.sort()
            backupName = files[0][1]
        shutil.copyfile(filename, backupName)
        print 'backup "%s" as "%s"' % (filename, backupName)

    def redraw(self, *args):
        self._redrawed = 1
        bw = 4
        w0, h0 = self.size
        w = w0 - 2 * bw
        h = (h0 - bw) / max(1, len(self.servos)) - bw
        x, y = bw, bw
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