from ui import *
from button import Button
from rsimage import RSImage
from animate import SizeAnimate
from timer import Timer

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

    rsi = RSImage('gradient_bg.png', 20, 20)

    def init(self):
        self.items = []
        if self.vertical:
            self.resize((self.itemsize[0] + 2 * self.margin, self.margin))
        else:
            self.resize((self.margin, self.itemsize[1] + self.margin * 2))
        Timer.add(Timer(1./FPS, self.animate))
        self.bind(EV_KEYPRESS, self.hide, BLK_POST_BLOCK)

    def add_item(self, name, callback):
        wi, hi = self.itemsize
        margin = self.margin
        if not self.vertical:
            y = margin
            x = (self.itemsize[0])* len(self.items)
        else:
            x = margin
            y = (self.itemsize[1]) * len(self.items)
        item = Button(self, caption=name, size=self.itemsize, pos=(x, y), 
                color=self.color, bgcolor=self.bgcolor,
                align=Button.ALIGN_CENTER)
        item.bind_command(callback)
        item.bind(EV_CLICK, self.hide, BLK_PRE_BLOCK)
        self.items.append(item)
        self.resize(self.cal_size())
        self.mark_redraw()

    def cal_size(self):
        wi, hi = self.itemsize
        margin = self.margin
        if not self.vertical:
            return (2 * margin + len(self.items) * wi, self.size[1])
        else:
            return (self.size[0], hi * len(self.items) + margin)

    def animate(self, dt):
        if not hasattr(self, 'curSize') or self.curSize.is_end(): return
        self.resize(self.curSize.get())
        self._redrawed = 1
        self.mark_redraw()

    def show(self, *args):
        super(Menu, self).show(*args)
        self.curSize = SizeAnimate((0, 0), self.cal_size())

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
        image.fill(COLOR_TRANS)
        image.blit(self.rsi.generate(self.size), (0, 0))
        image.fill(self.gapcolor, None, BLEND_RGBA_MULT)
