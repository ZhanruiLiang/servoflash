from ui import *
from button import Button

class MenuItem(Button):
    def set_callback(self, callback):
        self.bind(EV_CLICK, callback, BLK_PRE_BLOCK)

class Menu(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            bgcolor="(107, 107, 100, 100)",
            gapcolor="(58, 51, 49, 150)",
            color="(0xff, 0xff, 0xff, 0xff)",
            itemsize="(100, 20)",
            margin="4",
            vertical='True',
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['vertical', 'gapcolor', 'itemsize', 'margin']
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    def init(self):
        self.items = []
        if self.vertical:
            self.resize((self.itemsize[0] + 2 * self.margin, self.margin))
        else:
            self.resize((self.margin, self.itemsize[1] + self.margin * 2))

    def hide(self, *args):
        self._visible = False

    def show(self, *args):
        self._visible = True
        
    def add_item(self, name, callback):
        wi, hi = self.itemsize
        margin = self.margin
        if not self.vertical:
            y = margin
            x = (margin + self.itemsize[0])* len(self.items)
            self.resize((self.size[0] + wi + margin, self.size[1]))
        else:
            x = margin
            y = (margin + self.itemsize[1]) * len(self.items) + margin
            self.resize((self.size[0], self.size[1] + hi + margin))
        item = MenuItem(self, caption=name, size=self.itemsize, pos=(x, y), 
                color=self.color, bgcolor=self.bgcolor,
                align=Button.ALIGN_LEFT)
        item.set_callback(callback)
        self.items.append(item)
        self.mark_redraw()

    def remove_item(self, name):
        for item in self.items:
            if item.caption == name:
                break
        else:
            raise ValueError('%s not in items' % (name))
        self.items.remove(item)
        self.resize((self.size[0], self.size[1] - self.itemsize[1]))
        self.mark_redraw()

    def redraw(self):
        image = self.ownImage
        image.fill(self.gapcolor)

