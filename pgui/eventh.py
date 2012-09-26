import pygame as pg
from uiconsts import *
from vec2di import V2I

__metaclass__ = type

class EventHandler:
    def __init__(self):
        " _eventHandlers :: {eventType: [[handler]4])} "
        self._eventHandlers = {}
        self._focusable = False

    def bind(self, eventType, handler, blockMode=BLK_POST_BLOCK):
        """
        Bind an event to this object.
        eventType: event-types starts with EV_ .
        handler: a callback, with a event as the only parameter. 
                 If the handler returns True, then it's considered not executed.
        blockMode: a block mode, all availiable modes are BLK_* in uiconst.py
        """
        if eventType not in self._eventHandlers:
            self._eventHandlers[eventType] = [[] for i in xrange(4)]
        self._eventHandlers[eventType][blockMode].append(handler)

    def bind_key(self, key, handler, mod=0):
        def kcallback(event):
            if event.type == KEYDOWN and event.key == key:
                if mod and (mod & event.mod) or mod == event.mod:
                    handler(event)
                    return None
            return True
        self.bind(EV_KEYPRESS, kcallback, BLK_POST_BLOCK)
        return kcallback

    def unbind(self, eventType, handler, blockMode):
        if handler is None:
            # remove all
            del self._eventHandlers[eventType][blockMode][:]
        else:
            self._eventHandlers[eventType][blockMode].remove(handler)

    _ets0 = (EV_KEYPRESS, EV_MOUSEOUT, EV_DRAGOUT)
    _ets1 = (EV_MOUSEOUT, EV_MOUSEDOWN, EV_CLICK, EV_RCLICK, EV_MOUSEUP, EV_MOUSEOVER, EV_DRAGOVER)

    def invoke(self, eventType, event):
        if eventType in self._eventHandlers:
            for handlers in self._eventHandlers[eventType]:
                for handler in handlers:
                    handler(event)

    def on_event(self, eventType, event):
        """ try handle the event.
        return True if the event is blocked at this object.
        """
        # print 'event at', event, self
        if eventType in self._eventHandlers:
            # test if self should handle the event
            # self should handle iff:
            # * event is keypress.
            # * event is mouse-over, mouse-down, mouse-up, drag-over, mouse-click
            #     and self is under mouse.
            # * event is mouse-out, drag-out(this assumes that self is not under mouse).
            #
            if (eventType in self._ets0
                    or self.is_under_mouse(mouse.pos) and eventType in self._ets1):
                bHandlers = self._eventHandlers[eventType]
                blocked = False
                # invoke the BLK_PRE_BLOCK handlers
                for handler in bHandlers[BLK_PRE_BLOCK]:
                    if not handler(event):
                        blocked = True
                # invoke the BLK_PRE_NONBLOCK handlers
                for handler in bHandlers[BLK_PRE_NONBLOCK]:
                    handler(event)
                if blocked: return True
                # pass the event to childs
                # NOTE: the `any` function on a sequence generator is lazy.
                #       So a child may block its brother. 
                #       And the childs list should be sorted from high level to low.
                blocked = any(child.on_event(eventType, event) for child in self.childs)
                if blocked: return True

                # invoke the BLK_POST_BLOCK handlers
                for handler in bHandlers[BLK_POST_BLOCK]:
                    if not handler(event):
                        blocked = True
                for handler in bHandlers[BLK_POST_NONBLOCK]:
                    handler(event)
                return blocked
        # event not handled by self, pass it to the child
        blocked = any(child.on_event(eventType, event) for child in self.childs)
        return blocked

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
