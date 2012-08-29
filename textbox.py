import pygame as pg
pg.font.init()
pg.display.init()

class NotImplmentedError:
    pass

class TextBox(pg.sprite.Sprite):
    DEFAULT_FONT = 'MonospaceTypewriter.ttf'
    DEFAULT_COLOR = (0, 0, 0, 255)
    DEFAULT_BG = (255,255,255,255)

    def __init__(self, (width, height), text, wrapping=True, color=DEFAULT_COLOR, bgcolor=DEFAULT_BG, font=None,fontsize=14, **args):
        self.boxsize = (width, height)
        self.text = text
        self.fontsize = fontsize
        self.color = color
        self.bgcolor= bgcolor
        font = font or self.DEFAULT_FONT
        self.font = pg.font.Font(font, fontsize)
        self._wrapping = wrapping

        self._viewpos = 0
        self._create_pics()
        self.update()

        for key, value in args.iteritems():
            # if not hasattr(self, key) or getattr(self, key) is None:
            setattr(self, key, value)

    def _create_pics(self):
        """
        create member: 
            _lines
            _linepics
            image
            rect
        """
        font = self.font
        color = self.color
        bgcolor = self.bgcolor
        if self._wrapping:
            lines = []
            width = self.boxsize[0]
            for line in self.text.split('\n'):
                # find max i, font.size(line[:i+1]) <= width
                while line:
                    w = 0
                    for i in xrange(len(line)):
                        w += font.size(line[i])[0]
                        if w > width:
                            break
                    else:
                        lines.append(line)
                        break
                    lines.append(line[:i])
                    line = line[i:]
        else:
            lines = self.text.split('\n')
        self._lines = lines

        self._linepics = [font.render(line, 1, color).convert_alpha() for line in lines]
        self.image = pic = pg.Surface(self.boxsize).convert_alpha()
        self.rect = pic.get_rect()

    def update_line(self, lineID, content):
        pass

    def update(self, *args):
        pic = self.image
        x, y = 0, 0
        height = self.boxsize[1]
        if self.bgcolor is None:
            pic.fill((0, 0, 0, 0))
        else:
            pic.fill(self.bgcolor)
        for linepic in self._linepics[self._viewpos:]:
            # blit the line into the textbox
            pic.blit(linepic, (x, y))
            y += linepic.get_size()[1]
            if y >= height:
                break

    def scroll(self, d):
        self._viewpos = max(min(self._viewpos + d, len(self._lines)), 0)

    def handle_event(self, event):
        "event is in the pygame event type"
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                btn = event.button
                if btn == 1:
                    pass
                elif btn == 2:
                    # TODO: implement copy to clipboard by right click
                    pass
                elif btn == 4:
                    self.scroll(-1)
                elif btn == 5:
                    self.scroll(1)
                return True
        if event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_UP or key == pg.K_k:
                self.scroll(-1)
            elif key == pg.K_DOWN or key == pg.K_j:
                self.scroll(1)
            return True
        return False

if __name__ == '__main__':
    src = (
"""
The textbox works!

This is the third line.
    The fourth line with 4 leading spaces.

    def handle_event(self, event):
        "event is in the pygame event type"
        if event.type == pg.MOUSEBUTTONDOWN:
            btn = event.button
            if btn == 1:
                pass
            elif btn == 2:
                # TODO: implement copy to clipboard by right click
                pass
            elif btn == 4:
                self.scroll(-1)
            elif btn == 5:
                self.scroll(1)
            return True
        if event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_UP:
                self.scroll(-1)
            elif key == pg.K_DOWN:
                self.scroll(1)
        return False
End.
"""
)
    screen = pg.display.set_mode((800, 600), 0, 32)

    textbox = TextBox((700, 400),  src, wraping=True, fontsize=13)
    textbox.rect.topleft = 20, 20
    tm = pg.time.Clock()
    while 1:
        for e in pg.event.get():
            if textbox.handle_event(e):
                textbox.update()
            if e.type == pg.QUIT:
                exit(0)
        screen.fill(0x000011)
        screen.blit(textbox.image, textbox.rect)
        pg.display.flip()
        tm.tick(30)

