from ui import *
# using new style class
__metaclass__ = type

class Label(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            text='""',
            bgcolor='(0x88, 0x88, 0x88, 0xff)',
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['bgcolor', 'size', 'text']
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
            txtsize = self.Font.size(self.text)
            # draw bg
            image.fill(self.bgcolor)
            image.blit(txt, (V2I(self.size) - txtsize)/2)
        self._redrawed = 1
