from ui import *

class TextBox(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            text='""',
            wrapping="True",
            color="(0, 0, 0, 255)",
            bgcolor="(255, 255, 255, 100)",
            font="DEFAULT_FONT",
            fontsize="14",
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['color', 'bgcolor', 'font', 'fontsize', 'wrapping', 'text']
            )

    def init(self):
        self.ownImage = None
        self.font = pg.font.Font(self.font, self.fontsize)
        self.wrapping = self.wrapping

        self.curline = 0
        self._create_linepics()
        self.redraw()
        # bind events
        d = 1
        def scroller(e):
            if e.button == BTN_MOUSEUP:
                self.scroll(-d)
            elif e.button == BTN_MOUSEDOWN:
                self.scroll(d)
        self.bind(EV_MOUSEUP, scroller)
        self.bind(EV_MOUSEDOWN, scroller)
        self.bind(EV_MOUSEOVER, func_id(True), BLK_PRE_BLOCK)
        self.bind(EV_CLICK, func_id(True), BLK_PRE_BLOCK)
        self.bind(EV_RCLICK, func_id(True), BLK_PRE_BLOCK)

    def _create_linepics(self):
        """
        create member: 
            lines
            _linepics
        """
        font = self.font
        color = self.color
        bgcolor = self.bgcolor
        if self.wrapping:
            lines = []
            width = self.size[0]
            cw = font.size('a')[0]
            for line in self.text.split('\n'):
                # find max i, font.size(line[:i+1]) <= width
                while line:
                    i = width / cw
                    lines.append(line[:i])
                    line = line[i:]
        else:
            lines = self.text.split('\n')
        self.lines = lines
        self._linepics = [font.render(line, 1, color).convert_alpha() for line in lines]

    def update_line(self, lineIdx, content):
        pass

    def redraw(self, *args):
        pic = self.image
        x, y = 0, 0
        height = self.size[1]
        pic.fill(self.bgcolor)
        for linepic in self._linepics[self.curline:]:
            # blit the line into the textbox
            pic.blit(linepic, (x, y))
            y += linepic.get_size()[1]
            if y >= height:
                break
        self._redrawed = 1

    def scroll(self, d):
        self.curline = max(min(self.curline + d, len(self.lines)), 0)
        self.redraw()

    def scroll_to(self, d):
        self.curline = max(min(d, len(self.lines)), 0)
        self.redraw()

