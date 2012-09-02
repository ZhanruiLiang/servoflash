from ui import *
# using new style class
__metaclass__ = type

class Label(UIBase):
    ALIGN_CENTER = 0
    ALIGN_LEFT = 1
    ALIGN_RIGHT = 2

    AllArgs = update_join(UIBase.AllArgs, 
            align='self.ALIGN_CENTER',
            text='""',
            bgcolor='(0x88, 0x88, 0x88, 0xff)',
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 13)
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['align', 'bgcolor', 'size', 'text']
            )
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new):
        self._text = new
        self.mark_redraw()

    def redraw(self, *args):
        image = self.ownImage
        if not hasattr(self, 'text') or not self.text:
            image.fill(self.bgcolor)
        else:
            txt = self.Font.render(self.text, 1, self.color)
            tw, th = self.Font.size(self.text)
            w, h = self.size
            # draw bg
            image.fill(self.bgcolor)
            if self.align == self.ALIGN_CENTER:
                image.blit(txt, ((w - tw)/2, (h - th)/2))
            elif self.align == self.ALIGN_LEFT:
                image.blit(txt, (2, (h - th)/2))
            else:
                image.blit(txt, (w - 2 - tw, (h - th)/2))
        self._redrawed = 1
