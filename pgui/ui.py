import pygame as pg
from vec2di import V2I
from uiconsts import *
from eventh import *
import focus
# using new style class
__metaclass__ = type

# class Error(BaseException):
#     def __init__(self, msg):
#         self.msg = msg
#     def __repr__(self):
#         return msg
Error = Exception

pg.display.set_mode((1, 1), VFLAG, 32)

def update_join(d1, d2=None, **dargs):
    " update d1 with d2 -> d3 "
    d3 = d1.copy()
    if dargs:
        d2 = dargs
    for k, v in d2.iteritems():
        d3[k] = v
    return d3

def ord_join(ord1, ord2):
    result = []
    ord1 = ord1[::-1]
    ord2 = ord2[::-1]
    while ord1 and ord2:
        x = ord1[-1]
        if x not in ord2:
            result.append(x)
            del ord1[-1]
        else:
            y = ord2[-1]
            if x == y:
                result.append(x)
                del ord1[-1]
                del ord2[-1]
            elif y not in ord1:
                result.append(y)
                del ord2[-1]
            else:
                raise Error("cyclic order join: joined: %s, left: %s, %s" % (
                    result, ord1[::-1], ord2[::-1]))
    if ord1: result += ord1[::-1]
    else: result += ord2[::-1]
    return result

def concat_func(func1, func2):
    def func(*args, **dargs):
        func1(*args, **dargs)
        func2(*args, **dargs)
    return func

def color_eq(c1, c2):
    d = sum((x1 - x2) ** 2 for x1, x2 in zip(c1, c2))
    return d < 30

# step color c1 to color c2
def step_color(c1, c2, k=0.30):
    return tuple(int(x1 + (x2 - x1) * k) for x1, x2 in zip(c1, c2))

class UIBase(EventHandler, pg.sprite.Sprite):
    AllArgs = update_join({},
            level='100',
            color='(0, 0 ,0 ,0xff)',
            bgcolor='(0, 0, 0, 0)',
            pos='V2I((0, 0))',
            size='(1 ,1)',
            )
    ArgsOrd = ord_join([], 
        ['level', 'color', 'bgcolor', 'pos', 'size']
        )

    pg.font.init()
    pg.display.init()
    ID = 0

    def __init__(self, parent, **dargs):
        self.id = UIBase.ID
        UIBase.ID += 1
        self.parent = parent
        self._redrawed = 1
        # loop through the ArgsOrd list and assign args
        print self.ArgsOrd
        for attr in self.ArgsOrd:
            if attr in dargs:
                setattr(self, attr, dargs[attr])
                del dargs[attr]
            elif attr in self.AllArgs:
                setattr(self, attr, eval(self.AllArgs[attr]))
        super(UIBase, self).__init__(**dargs)

        self.childs = []
        self._redrawed = 0
        self.resize(self.size)
        self.mark_redraw()
        self.init()
        # self.redraw()
        if parent is not None:
            self.parent.add_child(self)
        # bind function to cancal focus when click on empty place
        self.bind(EV_CLICK, lambda e: focus.set_focus(None), BLK_POST_BLOCK)

    def init(self):
        pass

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        self._pos = V2I(v)
        if hasattr(self, 'rect'):
            self.rect.topleft = self._pos
            self._redrawed = 1

    def __repr__(self, shows=['id', 'pos', 'level']):
        args = ','.join('%s=%s' % (attr, getattr(self, attr)) 
                            for attr in shows if attr != 'parent' and hasattr(self, attr))
        return '%s(%s)' % (self.__class__.__name__, args)

    def resize(self, size):
        self.size = size
        self.image = pg.Surface(self.size).convert_alpha()
        self.ownImage = self.image.copy()
        self.rect = self.image.get_rect()
        self.mark_redraw()

    def redraw(self, *args):
        # redraw ownImage
        self._redrawed = 1

    def mark_redraw(self):
        self._needRedraw = 1

    def update(self, *args):
        """ Update the affected area.
            If readlly updated, return True, else False
        """
        if self._needRedraw:
            self.redraw()
            self._needRedraw = 0

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
