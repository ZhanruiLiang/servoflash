from ui import *
from aarrect import AAfilledRoundedRect
from timer import Timer

class Button(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"button%s"%self.id',
            bgcolor='(0x58, 0x58, 0x58, 0xff)',
            hovercolor='(0x88, 0xff, 0x88, 0xff)',
            presscolor='(0x10, 0x2f, 0x10, 0xff)',
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)

    def init(self):
        self.curColor = (0, 0, 0, 0xff)
        self.destColor = self.bgcolor

        self.txt = self.Font.render(self.caption, 1, self.color)
        self.bind(EV_MOUSEOVER, func_id(False), BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEDOWN, func_id(False), BLK_PRE_NONBLOCK)
        self.bind(EV_MOUSEOUT, func_id(False), BLK_PRE_NONBLOCK)

        self._animateTimer = Timer(0.05, self.animate)
        Timer.add(self._animateTimer)

    def _color_move(self, c1, c2):
        # for x1, x2 in zip(c1, c2):
            # x1' = x1 + (x2 - x1) * t = x1 * (1-t) + x2 * t
            # (x1' - x2) * ( x1 - x2) = (x1 - x2)**2 * (1 - t) > 0, t < 1
        return tuple(int(x1 + (x2 - x1) * 0.30) for x1, x2 in zip(c1, c2))

    def _color_eq(sefl, c1, c2):
        for x1, x2 in zip(c1, c2):
            if abs(x1 - x2) >= 3:
                return False
        return True

    def redraw(self, *args):
        image = self.ownImage
        image.fill(COLOR_TRANS)
        AAfilledRoundedRect(image, self.curColor, ((0, 0), self.size), 0.3)
        image.blit(self.txt, (V2I(self.size) - self.txt.get_size())/2)
        self._redrawed = 1

    def animate(self):
        # print 'animate', self, self.curColor, self.destColor
        if not self._color_eq(self.curColor, self.destColor):
            self.curColor = self._color_move(self.curColor, self.destColor)
            self.redraw()
        else:
            self._animateTimer.stop()

    _ets = (EV_MOUSEOVER, EV_MOUSEDOWN, EV_MOUSEUP)
    def on_event(self, eventType, event):
        r = super(Button, self).on_event(eventType, event)
        changed = True
        if eventType in self._ets and self.is_under_mouse(event.pos):
            if eventType == EV_MOUSEOVER:
                # mouse over, change the  color to a lighter one
                self.destColor = self.hovercolor
            elif eventType == EV_MOUSEDOWN:
                # mosue down, change the color to a darker one
                self.destColor = self.presscolor
            elif eventType == EV_MOUSEUP:
                # reset the color to bgcolor
                self.destColor = self.bgcolor
            else:
                changed = False
        elif eventType == EV_MOUSEOUT:
            # reset the color to bgcolor
            self.destColor = self.bgcolor
        else:
            changed = False
        if changed:
            self._animateTimer.start()
        return r

class TransButton(Button):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='""',
            bgcolor='COLOR_TRANS',
            hovercolor='COLOR_TRANS',
            presscolor='COLOR_TRANS',
            )
