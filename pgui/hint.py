from ui import update_join
from timer import Timer
from label import Label
from animate import  ValueAnimate
from root import Root
from uiconsts import FPS

class PopupHinter(Label):
    SHOW_TIME = 4.
    SHOWWING = 1
    SHOWN = 2
    HIDING = 3
    HIDED = 0
    AllArgs = update_join(Label.AllArgs, 
            bgcolor="(0xf5, 0xf1, 0x28, 0xff)",
            )

    def init(self):
        self._curPosY = None
        self._timer = None
        self.state = self.HIDED
        self.hide()

    def _animate(self, dt):
        self.pos = self.pos[0], self._curPosY.get()
        if self._curPosY.is_end():
            if self.state == self.HIDING:
                self.state == self.HIDED
                self.hide()
                Timer.remove(self._timer)
                self._timer = None
            elif self.state == self.SHOWWING:
                self.state = self.SHOWN
                self._timer = Timer(self.SHOW_TIME, self.hide_hint, 1)
                Timer.add(self._timer)
            return
        self.mark_redraw()

    def hide_hint(self):
        root = Root.instance
        self._curPosY = ValueAnimate(
                self.pos[1], root.size[1])
        if self._timer: self._timer.finish()
        self._timer = Timer(0.1, self._animate)
        Timer.add(self._timer)
        self.state = self.HIDING

    def show_hint(self, hint):
        root = Root.instance
        self.text = hint
        tsize = self.Font.size(hint)
        self.resize((tsize[0]+6, tsize[1]+4))
        self._curPosY = ValueAnimate(
                self.pos[1], root.size[1] - self.size[1])
        if self._timer: self._timer.finish()
        self._timer = Timer(1./FPS, self._animate)
        Timer.add(self._timer)
        self.show()
        self.state = self.SHOWWING
