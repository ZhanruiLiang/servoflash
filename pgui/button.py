from ui import *
from aarrect import AAfilledRoundedRect
from timer import Timer
from animate import ColorAnimate
from label import Label

class Button(UIBase):
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
            ['hovercolor', 'presscolor', 'caption', 'align']
            )

    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)

    def init(self):
        self.label = Label(self, text=self.caption, align=self.align, bgcolor=COLOR_TRANS, size=self.size)
        self._underMouse = False
        self.bind(EV_MOUSEOVER, self.on_mouse_over, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEDOWN, self.on_mouse_down, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEOUT, self.on_mouse_out, BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEUP, self.on_mouse_up, BLK_PRE_NONBLOCK)

        self.curColor = ColorAnimate((0, 0, 0, 0xff), self.bgcolor)
        Timer.add(Timer(1./FPS, self.animate))

    def redraw(self, *args):
        image = self.ownImage
        image.fill(COLOR_TRANS)
        AAfilledRoundedRect(image, self.curColor.get(), ((0, 0), self.size), 0.3)
        self._redrawed = 1

    def animate(self, dt):
        if self.curColor.is_end():
            return
        self.mark_redraw()

    def on_mouse_over(self, event):
        if not self._underMouse:
            # mouse over, change the  color to a lighter one, with animation
            self.curColor = ColorAnimate(self.curColor.get(), self.hovercolor)
        self._underMouse = True

    def on_mouse_out(self, event):
        if self._underMouse:
            # reset the color to bgcolor, with animation
            self.curColor = ColorAnimate(self.curColor.get(), self.bgcolor)
        self._underMouse = False

    def on_mouse_down(self, event):
        self.curColor = ColorAnimate(self.curColor.get(), self.presscolor)

    def on_mouse_up(self, event):
        if self._underMouse:
            self._underMouse = False
            self.on_mouse_over(event)

class TransButton(Button):
    AllArgs = update_join(Button.AllArgs, 
            caption='""',
            bgcolor='COLOR_TRANS',
            hovercolor='COLOR_TRANS',
            presscolor='COLOR_TRANS',
            )
