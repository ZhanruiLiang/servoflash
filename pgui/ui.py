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

def func_id(value):
    def func(*args, **dargs):
        return value
    return func

def concat_func(func1, func2):
    def func(*args, **dargs):
        func1(*args, **dargs)
        func2(*args, **dargs)
    return func


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
    ID = 0
    def init(self):
        pass

    def __init__(self, parent, **dargs):
        self.id = UIBase.ID
        UIBase.ID += 1
        self.parent = parent
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
        " _eventHandlers :: {eventType: (handler, blockMode)} "
        self._eventHandlers = {}
        self.childs = []
        self._redrawed = 0

        self.init()
        if parent is not None:
            self.parent.add_child(self)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        self._pos = V2I(v)
        if hasattr(self, 'rect'):
            self.rect.topleft = self._pos
            self._redrawed = 1

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        self._size = s
        self.image = pg.Surface(self._size).convert_alpha()
        self.ownImage = self.image.copy()
        self.rect = self.image.get_rect()

    def __repr__(self, shows=['id', 'pos', 'level']):
        args = ','.join('%s=%s' % (attr, getattr(self, attr)) 
                            for attr in shows if attr != 'parent' and hasattr(self, attr))
        return '%s(%s)' % (self.__class__.__name__, args)

    def on_event(self, eventType, event):
        " try handle the event, return true if the event is blocked at this object "
        if eventType in self._eventHandlers:
            if (eventType in (EV_KEYPRESS, EV_MOUSEOUT, EV_DRAGOUT)
                    or self.is_under_mouse(mouse.pos)):
                # print self, eventType, event
                blocked = False
                for handler, blockMode in self._eventHandlers[eventType]:
                    if blockMode in (BLK_PRE_BLOCK, BLK_PRE_BLOCK):
                        handler(event)
                        if blockMode == BLK_PRE_BLOCK:
                            blocked = True
                if blocked: return True
                # NOTE: the `any` function on a sequence generator is lazy
                blocked = any(child.on_event(eventType, event) for child in self.childs)
                if blocked:
                    return True
                if blockMode in (BLK_POST_BLOCK, BLK_POST_NONBLOCK):
                    handler(event)
                    if blockMode == BLK_POST_BLOCK:
                        return True
        else:
            blocked = any(child.on_event(eventType, event) for child in self.childs)
            return blocked

    def bind(self, eventType, handler, blockMode=BLK_POST_BLOCK):
        """
        Bind an event to this object.
        eventType: event-types starts with EV_ .
        handler: a callback, with a event as the only parameter
        blockMode: a block mode, all availiable modes are BLK_* in uiconst.py
        """
        handlers = self._eventHandlers
        pair = (handler, blockMode)
        if eventType in handlers:
            handlers[eventType].append(pair)
        else:
            handlers[eventType] = [pair]

    def unbind(self, eventType, handler):
        self._eventHandlers[eventType].remove(handler)

    def redraw(self, *args):
        # redraw ownImage
        self._redrawed = 1

    def update(self, *args):
        """ Update the affected area and return the affectedRect,
            relative to parent's coord system 
        """
        image = self.image
        ownImage = self.ownImage
        self.rect.topleft = self.pos

        affected = any([c.update(*args) for c in self.childs])
        affected = affected or self._redrawed
        self._redrawed = 0
        if not affected: 
            return False
        if ownImage:
            image.fill(COLOR_TRANS)
            image.blit(ownImage, (0, 0))
        # sort the childs by their level, render the lowwer level ones first.
        for child in reversed(self.childs):
            image.blit(child.image, child.rect)
        return True

    def _child_cmp(self, c1, c2):
        return cmp(c2.level, c1.level)

    def add_child(self, child):
        self.childs.append(child)
        self.childs.sort(cmp=self._child_cmp)

    def update_child(self): 
        self.childs.sort(cmp=self._child_cmp)

    def remove_child(self, child):
        self.childs.remove(child)

    def get_global_pos_at(self, localPos):
        # p0(basic pos) in global
        p0g = self.parent.get_global_pos_at(self.pos)
        return p0g + localPos

    def get_local_pos_at(self, globalPos):
        # p0(basic pos) in local 
        # self.pos + (x, y) = self.parent.get_local_pos_at(globalPos)
        return self.parent.get_local_pos_at(globalPos) - self.pos

    def get_all_under_mouse(self, mousepos, append):
        # Get all childs(including self) that are under the mouse.
        # Here `append` is a function use to append to the result.
        if not self.is_under_mouse(mousepos):
            return 
        append(self)
        for child in self.childs:
            child.get_all_under_mouse(mousepos, append)

    def is_under_mouse(self, mousepos):
        x, y = self.get_local_pos_at(mousepos)
        w, h = self.size
        return 0 <= x < w and 0 <= y < h


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
            Keys.states[event.button -1 + PG_NUM] = 1
        elif et == pg.MOUSEBUTTONUP:
            Keys.states[event.button -1 + PG_NUM] = 0
    @staticmethod
    def get_pressed():
        pressed = [i for i in xrange(KEY_NUM) if Keys.states[i]]
        return pressed

class Mouse:
    def __init__(self):
        self.buttons = [False] * 6
        self.lastButtons = [False] * 6
        self._draging = False
        self.pos = V2I((0, 0))
        self.lastPos = V2I((0, 0))

    def update(self, e):
        self.lastButtons, self.buttons = self.buttons, self.lastButtons
        for i in xrange(1, 6):
            self.buttons[i] = Keys.get(PG_NUM + i - 1)
        if e.type == pg.MOUSEMOTION:
            self.lastPos = self.pos
            self.pos = V2I(e.pos)

        if self._draging:
            # if left button clickd?
            if not self.buttons[BTN_MOUSELEFT]:
                # stop draging
                self._draging = 0
        else:
            # if mouse moved?
            if (self.buttons[BTN_MOUSELEFT] and self.pos - self.lastPos != (0, 0)):
                # start draging
                self._draging = 1

    def is_clicked(self):
        return (self.lastButtons[BTN_MOUSELEFT] and not self.buttons[BTN_MOUSELEFT])

    def __repr__(self):
        return 'Mouse(left=%d, right=%d, lastLeft=%d, lastRight=%d)' % (
                self.buttons[BTN_MOUSELEFT], self.buttons[BTN_MOUSERIGHT],
                self.lastButtons[BTN_MOUSELEFT], self.lastButtons[BTN_MOUSERIGHT],
                )

    def is_draging(self):
        """
        What's draging?
        - button down, moved, or
        - dragging, mouse down
        """
        return self._draging

mouse = Mouse()
