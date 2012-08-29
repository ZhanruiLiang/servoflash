import pygame as pg
from vec2di import V2I
# using new style class
__metaclass__ = type

class Error:
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return msg

# event types
EV_CLICK = 'click'
EV_RCLICK = 'rclick'
EV_MOUSEOVER = 'mouseover'
EV_MOUSEOUT = 'mouseout'
EV_DRAGOVER = 'dragover'
EV_DRAGOUT = 'dragout'
EV_KEYPRESS = 'keypress'

# event flow block mode
BLK_NONE = 0
BLK_PRE = 1
BLK_POST = 2

def update_join(d1, d2=None, **dargs):
    " update d1 with d2 -> d3 "
    d3 = d1.copy()
    if dargs:
        d2 = dargs
    for k, v in d2.iteritems():
        d3[k] = v

class UIBase:
    AllArgs = update_join({},
            parent='None', 
            size='(0 ,0)',
            pos='V2I((0, 0)',
            color='(0, 0 ,0 ,0xff)',
            bgcolor='(0, 0, 0, 0)',
            )
    def __init__(self, parent, **dargs):
        self.parent = parent
        for key in dargs:
            if key in self.AcceptArgs:
                setattr(self, key, dargs[key])
            else:
                raise Error('argument "%s" not recognized' % key)
        for attr, default in self.AllArgs.iteritems():
            if not hasattr(self, attr):
                setattr(self, eval(default))
        self._eventHandlers = {}
        self.childs = []

        self.image = pg.Surface(self.size).convert_alpha()
        self.rect = image.get_rect()
        self.rect.topleft = self.pos
        self._needRedraw = 1

    def on_event(self, eventType, event):
        if eventType in self._eventHandlers:
            handler, blockMode = self._eventHandlers[eventType]
            handler(event)
            if blockMode == BLK_NONE:
                return False
            elif blockMode == BLK_PRE:
                return True
            elif blockMode == BLK_POST:
                pass
            else:
                raise Error("unrecognized event block mode %s" % blockMode)
            return True
        else:
            return False

    def bind(self, eventType, event):
        self._eventHandlers[eventType] = event

    def update(self, view):
        self.rect.topleft = self.pos

    def get_global_pos_at(self, localPos):
        # p0(basic pos) in global
        p0g = self.parent.get_global_pos_at(self.pos)
        return p0g + localPos

    def get_local_pos_at(self, globalPos):
        # p0(basic pos) in local 
        # self.pos + (x, y) = self.parent.get_local_pos_at(globalPos)
        return self.parent.get_local_pos_at(globalPos) - self.pos


class Label(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"label"'
            )
    Font = pg.font.Font('MonospaceTypewriter.ttf', 11)
    def __init__(self, text, **dargs):
        UIBase.__init__(self, **dargs)
        self.text = text
        image = self.image
        txt = self.Font.render(self.text, 1, self.color)
        txtsize = self.Font.size(self.text)
        # draw bg
        image.fill(self.bgcolor)
        image.blit(txt, (self.size - txtsize)/2)

    def update(self, view):
        UIBase.update(self, view)

class Root(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"UIRoot"',
            size='(200, 200)',
            parent='None',
            )
    def __init__(self, **dargs):
        UIBase.update(self, view)
        self.parent = None

        pg.display.init()
        pg.font.init()
        self.screen = pg.display.set_mode(self.size, 0, 32)
        pg.display.set_caption(self.caption)
        self.screen.fill(self.bgcolor)
        pg.display.flip()

        self._quit = False

    def mainloop(self):
        pass

    def quit(self):
        self._quit = True
