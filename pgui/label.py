from ui import *
# using new style class
__metaclass__ = type

class Label(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            text='"label%s"%self.id',
            bgcolor='(0x88, 0x88, 0x88, 0xff)',
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, new):
        self._text = new
        self.redraw()

    def init(self):
        self.redraw()

    def redraw(self, *args):
        if not hasattr(self, 'ownImage'): return
        image = self.ownImage
        txt = self.Font.render(self.text, 1, self.color)
        txtsize = self.Font.size(self.text)
        # draw bg
        image.fill(self.bgcolor)
        image.blit(txt, (V2I(self.size) - txtsize)/2)
        self._redrawed = 1
        print self, 'redrawed'
