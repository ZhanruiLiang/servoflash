import pygame as pg
from vec2di import V2I
from uiconsts import *
# using new style class
__metaclass__ = type

class Error:
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return msg


def update_join(d1, d2=None, **dargs):
    " update d1 with d2 -> d3 "
    d3 = d1.copy()
    if dargs:
        d2 = dargs
    for k, v in d2.iteritems():
        d3[k] = v
    return d3

class UIBase(pg.sprite.Sprite):
    AllArgs = update_join({},
            parent='None', 
            level='100',
            size='(0 ,0)',
            pos='V2I((0, 0))',
            color='(0, 0 ,0 ,0xff)',
            bgcolor='(0, 0, 0, 0)',
            )
    pg.font.init()
    pg.display.init()
    def __init__(self, parent, **dargs):
        self.parent = parent
        if parent:
            self.parent.childs.append(self)
        dargs1 = {}
        for key in dargs:
            if key in self.AllArgs:
                setattr(self, key, dargs[key])
            else:
                # raise Error('argument "%s" not recognized' % key)
                dargs1[key] = dargs[key]
        super(UIBase, self).__init__(**dargs1)

        for attr, default in self.AllArgs.iteritems():
            if not hasattr(self, attr):
                setattr(self, attr, eval(default))
        self._eventHandlers = {}
        self.childs = []

        try:
            self.image = pg.Surface(self.size).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = self.pos
        except pg.error:
            self.rect = pg.Rect((0, 0), self.size)
        self._needRedraw = 1

    def on_event(self, eventType, event):
        " try handle the event, return true if the event is blocked by this object "
        print self, eventType, event
        if eventType in self._eventHandlers:
            if (eventType in (EV_KEYPRESS, EV_MOUSEOUT, EV_DRAGOUT)
                    or self.is_under_mouse(mouse.pos)):
                handler, blockMode = self._eventHandlers[eventType]
                if blockMode in (BLK_PRE_BLOCK, BLK_PRE_BLOCK):
                    handler(event)
                    if blockMode == BLK_PRE_BLOCK:
                        return True
                blocked = any(child.on_event(eventType, event) for child in self.childs)
                if blocked:
                    return True
                if blockMode in (BLK_POST_BLOCK, BLK_POST_NONBLOCK):
                    handler(event)
                    if blockMode == BLK_POST_BLOCK:
                        return True
        return False

    def bind(self, eventType, handler, blockMode=BLK_POST_BLOCK):
        self._eventHandlers[eventType] = (handler, blockMode)

    def update(self, view):
        for child in sorted(self.childs, cmp=lambda x, y: x.level < y.level):
            child.update(view)
            self.image.blit(child.image, child.rect)
        self.rect.topleft = self.pos

    def get_global_pos_at(self, localPos):
        # p0(basic pos) in global
        p0g = self.parent.get_global_pos_at(self.pos)
        return p0g + localPos

    def get_local_pos_at(self, globalPos):
        # p0(basic pos) in local 
        # self.pos + (x, y) = self.parent.get_local_pos_at(globalPos)
        return self.parent.get_local_pos_at(globalPos) - self.pos

    def get_all_under_mouse(self, mousepos, append):
        if not self.is_under_mouse(mousepos):
            return 
        append(self)
        for child in self.childs:
            child.get_all_under_mouse(mousepos, append)

    def is_under_mouse(self, mousepos):
        x, y = self.get_local_pos_at(mousepos)
        w, h = self.size
        return 0 <= x < w and 0 <= y < h

class Label(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"label"',
            bgcolor='(0x88, 0x88, 0x88, 0xff)',
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)
    def __init__(self, parent, text, **dargs):
        UIBase.__init__(self, parent, **dargs)
        self.text = text
        image = self.image
        txt = self.Font.render(self.text, 1, self.color)
        txtsize = self.Font.size(self.text)
        # draw bg
        image.fill(self.bgcolor)
        image.blit(txt, (V2I(self.size) - txtsize)/2)

    def update(self, view):
        UIBase.update(self, view)

class Keys:
    states = [0] * KEY_NUM
    @staticmethod
    def get(key):
        return Keys.states[key]

    @staticmethod
    def update(event):
        et = event.type
        if et == pg.KEYDOWN:
            Keys.states[event.key] = 1
        elif et == pg.KEYUP:
            Keys.states[event.key] = 0
        elif et == pg.MOUSEBUTTONDOWN:
            Keys.states[event.button - PG_NUM] = 1
        elif et == pg.MOUSEBUTTONUP:
            Keys.states[event.button - PG_NUM] = 0

class Mouse:
    def __init__(self):
        self.buttons = [False] * 5
        self.lastButtons = [False] * 5
        self._draging = False
        self.pos = V2I((0, 0))
        self.lastPos = V2I((0, 0))

    def update(self):
        self.lastButtons, self.buttons = self.buttons, self.lastButtons
        for i in xrange(5):
            self.buttons[i] = Keys.get(PG_NUM + i)
        self.lastPos = self.pos
        self.pos = V2I(pg.mouse.get_pos())

        if self._draging:
            # if left button clickd?
            if not self.pos[K_MOUSELEFT - PG_NUM]:
                # stop draging
                self._draging = 0
        else:
            # if mouse moved?
            if self.pos - self.lastPos != (0, 0):
                # start draging
                self._draging = 1

    def is_clicked(self):
        return (self.lastButtons[K_MOUSELEFT - PG_NUM]
                and not self.buttons[K_MOUSELEFT - PG_NUM])

    def is_draging(self):
        """
        What's draging?
        - button down, moved, or
        - dragging, mouse down
        """
        return self._draging

mouse = Mouse()
class Root(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"UIRoot"',
            size='(200, 200)',
            parent='None',
            )

    def __init__(self, **dargs):
        super(Root, self).__init__(None, **dargs)

        self.image = pg.display.set_mode(self.size, 0, 32)
        pg.display.set_caption(self.caption)
        self.image.fill(self.bgcolor)
        pg.display.flip()

        self._quit = False
        self._underMouse = []

    def get_global_pos_at(self, localPos):
        return localPos

    def get_local_pos_at(self, globalPos):
        return globalPos

    def handle_event(self):
        events = pg.event.get()
        for e in events:
            Keys.update(e)
            mouse.update()
            types = set()
            underMouse = []
            self.get_all_under_mouse(mouse.pos, underMouse.append)
            for ui in self._underMouse:
                if ui not in underMouse:
                    # mouse move out this ui just now
                    ui.on_event(EV_MOUSEOUT, e)# invoke the handler
                    if mouse.is_draging():
                        # drag out
                        ui.on_event(EV_DRAGOUT, e)# invoke the handler
            if mouse.is_clicked():
                types.add(EV_CLICK) # click

            if e.type == pg.MOUSEBUTTONDOWN:
                if PG_NUM + e.button == K_MOUSERIGHT:
                    types.add(EV_RCLICK) # right click
                types.add(EV_MOUSEDOWN) # mouse down
            elif e.type == pg.MOUSEBUTTONUP:
                types.add(EV_MOUSEUP) # mouse up
            elif e.type == pg.KEYDOWN:
                types.add(EV_KEYPRESS) # key press
            elif e.type == pg.MOUSEMOTION:
                types.add(EV_MOUSEOVER) # mouse over
                if mouse.is_draging():
                    types.add(EV_DRAGOVER) # drag over
            elif e.type == pg.QUIT:
                self.quit()
                return
            self._underMouse = underMouse
            for t in types:
                self.on_event(t, e) # invoke the handler

    def update(self, view):
        super(Root, self).update(view)

    def mainloop(self, FPS=30):
        self._quit = False
        tm = pg.time.Clock()
        view = None
        while not self._quit:
            self.handle_event()
            self.update(view)
            pg.display.flip()
            tm.tick(FPS)

    def quit(self):
        self._quit = True

if __name__ == '__main__':
    def barker(msg):
        def bark(*args):
            print msg, args
        return bark
    root = Root(bgcolor=(0xff, 0xff, 0xff, 0xff), size=(800, 600))
    label = Label(root, "hello", pos=(300, 200), size=(100, 30))
    label.bind(EV_MOUSEDOWN, barker('mouse down'))
    root.mainloop()
