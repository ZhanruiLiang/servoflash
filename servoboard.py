from pgui.ui import *
from pgui.label import Label
from pgui.root import Root, warn, hint

class KeyFrame:
    def __init__(self, dti, a):
        self.dti = max(1, dti)
        self.a = a
    def __repr__(self):
        return 'frame(a=%d, dti=%d)' % (self.a, self.dti)

class ServoBoard(UIBase):
    LIGHT_COLOR = (204, 178, 181, 0xff)
    LIGHT_COLOR2 = (220, 200, 193, 0x88)
    DARK_COLOR = (000, 00, 000, 0xff)
    POINT_COLOR = (0xff, 0, 0xff, 0xff)
    RULER_COLOR = (230, 230, 230, 255)
    LABEL_COLOR = (170, 170, 170, 120)
    FRAME_WIDTH = 6
    MIN_HEIGHT = 40
    AllArgs = update_join(UIBase.AllArgs, 
            selectcolor='(0, 160, 245, 155)',
            bgcolor='(255, 255, 255, 255)',
            sid='0', # servo id
            label='"servo"',
            bias='0', # servo bias, such that: bias + direction * angle * (1024/360) = actualADValue
            direction='1', 
            viewpos='0', # time index
            min='0', # angle min
            max='200', # angle max
            )

    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['selectcolor', 'label', 'sid', 'bias', 'min', 'max', 'direction', 'viewpos']
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    def __repr__(self):
        return 'servo#%d' % self.sid

    def init(self):
        #  a0    |                              
        #  |     a1                             
        #  |     |                              
        #  0-t0--1--t1----                      
        #                                       
        self.keyFrames = [KeyFrame(5, 0)]
        # add many keyFrames randomly, for test purpose only
        self.keyFrames = [KeyFrame(5, 0)]
        self.playingPos = None

        self.bgImage = self.image.copy()
        self._redraw_bg()
        self._actived = False
        self.selected = 0# the selected frame

        self.labelUI = Label(self, text='%s(%d)' % (self.label, self.sid), 
                bgcolor=self.LABEL_COLOR, color=(0, 0, 0, 255),
                pos=(0, 0), size=(80, 20))
        # self.bind(EV_MOUSEDOWN, self.start_drag)
        # self.bind(EV_MOUSEUP, self.end_drag)
        # self.bind(EV_MOUSEOUT, self.end_drag)
        # self.bind(EV_DRAGOVER, self.on_drag)

    @property
    def sid(self):
        return self._sid

    @sid.setter
    def sid(self, id):
        self._sid = id
        self.label = self.label

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, v):
        self._label = v
        if hasattr(self, 'labelUI'):
            self.labelUI.text = '%s(%d)' % (self._label, self._sid)

    def angle2ad(self, angle):
        return int(self.bias + self.direction * angle * 1024 / 300)

    def ad2angle(self, ad):
        return (ad - self.bias)/self.direction * 300 / 1024

    def is_safe_angle(self, angle):
        return self.min <= angle <= self.max

    def get_a_at(self, ti):
        """
        The the a value at time ti
        """
        i, dti = self.find_ti_pos(ti)
        if i + 1 < len(self.keyFrames):
            f1 = self.keyFrames[i]
            f2 = self.keyFrames[i+1]
            return int(f1.a + (f2.a - f1.a) / f1.dti * dti)
        else:
            return self.keyFrames[-1].a

    def select_at(self, pos):
        ti, a = self.screen_pos_to_ta(pos)
        self.select(ti)

    def select(self, ti):
        self.selected = ti
        hint('frame %d(a=%d, t=%.3fs)' %(ti, self.get_a_at(ti), ti * self.parent.timeStep))

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
        hint('insert %s' % newFrame)
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

    def remove_frame(self, ti):
        i, dti = self.find_ti_pos(ti)
        if i < len(self.keyFrames):
            if dti > 0:
                self.keyFrames[i].dti -= 1
            elif i > 0:
                self.keyFrames[i-1].dti += self.keyFrames[i].dti
                del self.keyFrames[i]
            self.mark_redraw()
            hint('removed frame at %d' % ti)

    def adjust_curframe(self, da):
        if self.selected is not None:
            i, dti = self.find_ti_pos(self.selected)
            if i < len(self.keyFrames):
                a = self.keyFrames[i].a + da
                if self.min <= a <= self.max:
                    self.keyFrames[i].a += da
                    self.mark_redraw()
                    self.select(self.selected)
                else:
                    warn("angle=%d out of range(%s)" %(a, (self.min, self.max)))

    def _redraw_bg(self):
        image = self.bgImage
        image.fill(self.bgcolor)
        w, h = self.size
        w1 = self.FRAME_WIDTH
        # draw the enclosing box rect
        pg.draw.rect(image, self.LIGHT_COLOR, ((0, 0), (w, h)), 1)

        for x in xrange(0, w, w1):
            # draw a vertical line
            # pg.draw.line(image, self.LIGHT_COLOR2, (x - w1/2, 0), (x - w1/2, h), 2)
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
        w1 = self.FRAME_WIDTH

        # draw the ruler
        x0 = (5 - self.viewpos) % 5 * w1
        for x in xrange(x0, w, 5 * w1):
            pg.draw.rect(image, self.RULER_COLOR, ((x - w1/2 + 1, 1), (w1-1, h-2)))

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
            y = self.a_to_screen(frame.a)
            # the current point
            cur = (x, y)
            if prev is not None:
                # draw line, link the prev point with current point
                pg.draw.line(image, self.color, prev, cur, 2)
            # draw the vertical dark line
            pg.draw.line(image, self.DARK_COLOR, (x, 0), (x, y), 1)
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

        (t - viewpos) * FRAME_WIDTH = x
        """
        x, y = pos
        ti = int(x / self.FRAME_WIDTH + self.viewpos)
        a = int(y * 360 / self.size[1])
        return ti, a

    def on_click(self, event):
        pos = self.get_local_pos_at(event.pos)
        ti, a = self.screen_pos_to_ta(pos)
        self.insert_key_frame(ti, a)

    def a_to_screen(self, a):
        """(a - min) * (max - min) / height = y"""
        return int((a - self.min) * self.size[1] / max(self.MIN_HEIGHT, (self.max-self.min))) 

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
            self.viewpos =  max(0, self._viewpos0 - dx / self.FRAME_WIDTH)
            self.mark_redraw()

    def active(self):
        if not self._actived:
            self._actived = True
            self.labelUI.bgcolor=self.selectcolor
            self.labelUI.mark_redraw()
            self.mark_redraw()

    def deactive(self):
        if self._actived:
            self._actived = False
            self.selected = None
            self.labelUI.bgcolor=self.LABEL_COLOR
            self.labelUI.mark_redraw()
            self.mark_redraw()

    def is_actived(self):
        return self._actived;
