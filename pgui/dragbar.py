from ui import *
from button import Button, TransButton

class DragBar(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            minvalue='0',
            maxvalue='100',
            value='0',
            vertical='False',
            bgcolor='(75, 50, 51, 255)',
            hovercolor='(93, 238, 90, 100)',
            color='(97, 127, 100, 255)',
            blockwidth='20',
            size='(150, 20)',
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['color', 'bgcolor', 'hovercolor', 
                'blockwidth', 'minvalue', 'maxvalue','vertical', 'size', 'value']
            )
    @property
    def percent(self):
        return float(self.value - self.minvalue) / (self.maxvalue - self.minvalue)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(self.minvalue, min(self.maxvalue, v))
        bw = self.blockwidth
        self.mark_redraw()
        try:
            for callback in self._on_change_callbacks:
                callback()
        except AttributeError:
            pass

    def init(self):
        self.backButton = back = TransButton(
                self, level=11, size=self.size, hovercolor=self.hovercolor)
        if not self.vertical:
            blockSize = (self.blockwidth, self.size[1])
        else:
            blockSize = (self.size[0], self.blockwidth)
        self.blockButton = block = Button(
                self, level=12, size=blockSize, color=self.color, caption='')
        back.bind(EV_MOUSEDOWN, self.scroll, BLK_POST_BLOCK)
        back.bind(EV_DRAGOVER, self.drag_to, BLK_POST_BLOCK)
        block.bind(EV_MOUSEDOWN, self.start_drag, BLK_PRE_BLOCK)
        block.bind(EV_MOUSEUP, self.stop_drag, BLK_PRE_BLOCK)
        self.redraw()

        self._on_change_callbacks = []
        self._draging = False

    def start_drag(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == BTN_MOUSELEFT:
            if not self._draging:
                self._draging = True
        else:
            return True

    def stop_drag(self, event):
        self._draging = False

    def scroll(self, event):
        vlen = self.maxvalue - self.minvalue
        if event.button == BTN_MOUSEUP:
            self.value -= 1 + vlen / 100
        elif event.button == BTN_MOUSEDOWN: 
            self.value += 1 + vlen / 100
        elif event.button == BTN_MOUSELEFT:
            self._draging = True
            self.drag_to(event)
            self._draging = False
        else:
            return True

    def drag_to(self, event):
        if self._draging:
            w, h = self.size
            x, y = self.get_local_pos_at(event.pos)
            bw2 = self.blockwidth / 2
            if self.vertical:
                h, w = w, h
                x, y = y, x
            if w != 2 * bw2:
                percent = max(0, float(x - bw2) / (w - 2 * bw2))
            else:
                percent = 0
            self.value = int(self.minvalue + (self.maxvalue - self.minvalue) * percent)

    def bind_on_change(self, callback):
        self._on_change_callbacks.append(callback)

    def unbind_on_change(self, callback):
        self._on_change_callbacks.remove(callback)

    def redraw(self, *args):
        p = self.percent
        image = self.ownImage
        image.fill(self.bgcolor)
        bw = self.blockwidth
        bw2 = self.blockwidth / 2
        if self.vertical:
            w = self.size[1]
            self.blockButton.pos = V2I((0, self.percent * (w - bw)))
        else:
            w = self.size[0]
            self.blockButton.pos = V2I((self.percent * (w - bw), 0))
        if not self.vertical:
            len, w = self.size
            wMargin = w/2.8
            image.fill(COLOR_TRANS)
            pg.draw.rect(image, self.bgcolor, pg.Rect((bw2, wMargin), (len - 2*bw2, w - 2*wMargin)), 0)
        else:
            w, len = self.size
            wMargin = w/2.8
            image.fill(COLOR_TRANS)
            pg.draw.rect(image, self.bgcolor, pg.Rect((wMargin, bw2), (w - 2*wMargin, len - 2*bw2)), 0)
        self._redrawed = 1
