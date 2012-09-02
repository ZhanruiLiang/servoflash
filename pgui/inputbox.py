from ui import *
from focus import Focusable
from button import Button, TransButton
from label import Label
from timer import Timer
from animate import ColorAnimate
import string

class InputBox(UIBase, Focusable):
    DEFAULT_CHARS = string.letters + string.digits + r' -=!@#$%^&*()_+|\{}[]`~,./<>?'

    AllArgs = update_join(UIBase.AllArgs, 
            text="''",
            chars="self.DEFAULT_CHARS",
            blinkcolor="(0x9f, 0x9f, 0xff, 0xff)",
            bgcolor="(0xff, 0xff, 0xff, 0xff)",
            color="(0, 0, 0, 0xff)",
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['chars', 'blinkcolor', 'text']
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    def init(self):
        Focusable.__init__(self)
        self.minWidth = self.size[0]
        self.minHeight = self.size[1]

        self.bgLabel = Label(self, level=10, size=self.size, text='', bgcolor=self.bgcolor)
        self.hoverButton = TransButton(self, level=11, size=self.size)
        self.txtLabel = Label(self, level=12, size=self.size, 
                color=self.color, text=self.text, bgcolor=COLOR_TRANS)

        self.redraw()
        self.bind(EV_CLICK, self.set_as_focus, BLK_PRE_BLOCK)

        self._editing = False
        Timer.add(Timer(1./FPS, self.animate))
        self.blinker = ColorAnimate(self.bgcolor, self.bgcolor)

    def start_blink(self):
        self._blinkState = 0
        self.blinker = ColorAnimate(self.bgcolor, self.blinkcolor)

    def on_focus(self):
        self._editing = True
        self.start_blink()

    def on_lost_focus(self):
        self._editing = False
        self.blinker = ColorAnimate(self.blinker.get(), self.bgcolor)

    def input(self, event):
        if event.key in (pg.K_BACKSPACE, pg.K_DELETE, pg.K_LEFT):
            self.text = self.text[:-1]
        elif event.key == pg.K_v and (event.mod & pg.KMOD_CTRL):
            self.paste_from_X()
        elif event.key == pg.K_c and (event.mod & pg.KMOD_CTRL):
            self.copy_to_X()
        elif event.unicode in self.chars:
            self.text = self.text + str(event.unicode)
        self.txtLabel.text = self.text
        self.mark_redraw()

    def animate(self, dt):
        bg = self.bgLabel
        blinker = self.blinker
        if self._editing:
            bg.bgcolor = blinker.get()
            bg.redraw()
            if blinker.is_end():
                if self._blinkState == 0:
                    self.blinker = ColorAnimate(self.blinkcolor, self.bgcolor)
                    self._blinkState = 1
                else:
                    # self.start_blink()
                    self.blinker = ColorAnimate(self.bgcolor, self.blinkcolor)
                    self._blinkState = 0
        elif not color_eq(blinker.get(), self.bgcolor):
            bg.bgcolor = blinker.get()
            bg.redraw()

    def resize(self, s):
        super(InputBox, self).resize(s)
        try:
            self.hoverButton.resize(s)
            self.bgLabel.resize(s)
            self.txtLabel.resize(s)
        except AttributeError:
            pass

    def redraw(self):
        w0, h0 = self.size
        tw, th = self.txtLabel.Font.size(self.text)
        w1 = max(self.minWidth, tw)
        h1 = max(self.minHeight, th)
        if w1 != w0 or h1 != h0:
            self.pos = (self.pos[0] - (w1 - w0)/2, self.pos[1] - (h1 - h0)/2)
            self.resize((w1, h1))

    def copy_to_X(self):
        copy_to_X(self.text)

    def paste_from_X(self):
        self.text = paste_from_X()
        self.txtLabel.text = self.text
        self.mark_redraw()
