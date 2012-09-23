from pgui.ui import *
from pgui import Label, InputBox, Root
import config

class AttrBoard(UIBase):
    MARGIN = 5
    ITEM_HEIGHT = 20

    def init(self):
        self.lines = []

    def add_line(self):
        w, h = self.size
        h = self.ITEM_HEIGHT
        x, y = self.MARGIN, len(self.lines) * (h + self.MARGIN) + self.MARGIN
        w1 = int((w - 2 * self.MARGIN) * 0.6)
        w2 = w - w1 - 6 - self.MARGIN
        attr = Label(self, align=Label.ALIGN_RIGHT, size=(w1, h), pos=(x, y))
        value = InputBox(self, size=(w2, h), pos=(x + w1 + 2, y))
        self.lines.append((attr, value))

    def show_info(self, obj, attrs, types):
        while len(self.lines) < len(attrs):
            self.add_line()
        for (label, input) in self.lines[len(attrs):]:
            label.hide()
            input.hide()
        for attr, type, (label, input) in zip(attrs, types, self.lines):
            label.text = attr
            input.text = str(getattr(obj, attr))
            input.mark_redraw()
            input.clear_callbacks()
            input.bind_setter(obj, attr, type)
