import pygame as pg
from vec2di import V2I
from uiconsts import *
from eventh import *
from utils import *
import focus
# using new style class
__metaclass__ = type

pg.display.set_mode((SCREEN_W, SCREEN_H), VFLAG, 32)
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

    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    pg.font.init()
    pg.display.init()
    ID = 0

    def __init__(self, parent, **dargs):
        self.id = UIBase.ID
        UIBase.ID += 1
        self.parent = parent
        self._redrawed = 1
        self._visible = True
        # loop through the ArgsOrd list and assign args
        for attr in self.ArgsOrd:
            if attr in dargs:
                setattr(self, attr, dargs[attr])
                del dargs[attr]
            elif attr in self.AllArgs:
                setattr(self, attr, eval(self.AllArgs[attr]))
        super(UIBase, self).__init__(**dargs)

        self.childs = []
        self._redrawed = 0
        self._destoryed = False
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

    def is_visible(self):
        x = self
        while x:
            if x._visible == False:
                return False
            x = x.parent
        return True

    def hide(self, *args):
        if self._visible:
            self._visible = False
            self.parent.remove_child(self)
            self.parent.mark_redraw()

    def show(self, *args):
        if not self._visible:
            self._visible = True
            self.parent.add_child(self)
            self.parent.mark_redraw()

    def destory(self):
        if not self._destoryed:
            self._destoryed = True
            self.parent.remove_child(self)
            self.parent.mark_redraw()

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
        self.rect = pg.Rect(self.pos, size)
        self.mark_redraw()

    def redraw(self, *args):
        # redraw ownImage
        self.ownImage.fill(self.bgcolor)
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
        # render the lowwer level ones first.
        for child in reversed(self.childs):
            image.blit(child.image, child.rect)
        return True

    def _child_cmp(self, c1, c2):
        return cmp(c2.level, c1.level)

    def add_child(self, child):
        if child in self.childs: return
        self.childs.append(child)
        self.update_childs()

    def update_childs(self): 
        self.childs.sort(cmp=self._child_cmp)

    def remove_child(self, *args):
        if not args:
            args = self.childs[:]
        for child in args:
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
