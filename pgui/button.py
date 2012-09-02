from ui import *
from aarrect import AAfilledRoundedRect
from timer import Timer
from animate import ColorAnimate
from label import Label
from rsimage import RSImage
from focus import Focusable

class Button(UIBase, Focusable):
    ALIGN_CENTER = Label.ALIGN_CENTER
    ALIGN_LEFT = Label.ALIGN_LEFT
    ALIGN_RIGHT = Label.ALIGN_RIGHT

    AllArgs = update_join(UIBase.AllArgs,
            bgcolor='(0x58, 0x58, 0x58, 0xff)',
            hovercolor='(0x88, 0xff, 0x88, 0xff)',
            presscolor='(0x10, 0x2f, 0x10, 0xff)',
            caption='"button%s"%self.id',
            align='self.ALIGN_CENTER',
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['hovercolor', 'presscolor', 'caption', 'align', 'image']
            )

    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)
    rsi = RSImage('button_bg.png', 5, 5)

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, v):
        self._caption = v
        if hasattr(self, 'label'):
            self.label.text = v

    def init(self):
        Focusable.__init__(self)
        self.label = Label(self, text=self.caption, align=self.align, color=self.color, bgcolor=COLOR_TRANS, size=self.size)
        self._underMouse = False
        self.bind(EV_MOUSEOVER, self.on_mouse_over, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEDOWN, self.on_mouse_down, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEOUT, self.on_mouse_out, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEUP, self.on_mouse_up, BLK_PRE_NONBLOCK)

        self.curColor = ColorAnimate((0, 0, 0, 0xff), self.bgcolor)
        Timer.add(Timer(1./FPS, self.animate))
        self.command = None

    def on_focus(self, *args):
        if not self._underMouse:
            self.on_mouse_over(*args)

    def on_lost_focus(self, *args):
        self.on_mouse_out(*args)

    def input(self, e):
        if e.key == K_RETURN:
            if self.command:
                self.command(e)
            self.on_mouse_down()
            Timer.add(Timer(0.2, self.on_mouse_up, 1))
        else:
            return True

    def bind_command(self, command):
        if self.command is not None:
            self.unbind(EV_CLICK, self.command, BLK_PRE_BLOCK)
        self.command = command
        self.bind(EV_CLICK, command, BLK_PRE_BLOCK)

    def resize(self, size):
        super(Button, self).resize(size)
        self.bgImage = self.rsi.generate(size)

    def redraw(self, *args):
        image = self.ownImage
        image.fill(COLOR_TRANS)
        image.blit(self.bgImage, (0, 0))
        image.fill(self.curColor.get(), None, BLEND_RGBA_MULT)
        # AAfilledRoundedRect(image, self.curColor.get(), ((0, 0), self.size), 0.3)
        self._redrawed = 1

    def animate(self, dt):
        if self.curColor.is_end():
            return
        self.mark_redraw()

    def on_mouse_over(self, *args):
        if not self._underMouse:
            # mouse over, change the  color to a lighter one, with animation
            self.curColor = ColorAnimate(self.curColor.get(), self.hovercolor)
            if self != focus.get_focus():
                self.set_as_focus()
        self._underMouse = True

    def on_mouse_out(self, *args):
        if self._underMouse:
            # reset the color to bgcolor, with animation
            self.curColor = ColorAnimate(self.curColor.get(), self.bgcolor)
        self._underMouse = False

    def on_mouse_down(self, *args):
        self.curColor = ColorAnimate(self.curColor.get(), self.presscolor)

    def on_mouse_up(self, *args):
        if self._underMouse:
            self._underMouse = False
            self.on_mouse_over(*args)

class TransButton(Button):
    AllArgs = update_join(Button.AllArgs, 
            caption='""',
            bgcolor='COLOR_TRANS',
            hovercolor='COLOR_TRANS',
            presscolor='COLOR_TRANS',
            )
    def init(self):
        Button.init(self)
        focus.remove_focus_obj(self)
