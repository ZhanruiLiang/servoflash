from ui import *
from timer import Timer
import focus

class Root(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"UIRoot"',
            size='(200, 200)',
            parent='None',
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            ['parent', 'caption', 'size']
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

    def __init__(self, *args, **dargs):
        super(Root, self).__init__(None, *args, **dargs)

    def init(self):
        pg.display.set_caption(self.caption)
        pg.key.set_repeat(400, 50)
        self._quit = False
        self._underMouse = []
        self._timers = []

    def tab_focus(self, event):
        if event.mod & KMOD_SHIFT:
            focus.set_focus(focus.prev_focus())
        else:
            focus.set_focus(focus.next_focus())

    def resize(self, size):
        self.size = size
        self.image = pg.display.set_mode(self.size, VFLAG, 32)
        self.rect = self.image.get_rect()
        self.ownImage = self.image.copy()
        self.mark_redraw()

    def redraw(self):
        self.ownImage.fill(self.bgcolor)
        self._redrawed = 1

    def get_global_pos_at(self, localPos):
        return V2I(localPos)

    def get_local_pos_at(self, globalPos):
        return V2I(globalPos)

    def handle_event(self):
        events = pg.event.get()
        for e in events:
            Keys.update(e)
            # print 'pressed', Keys.get_pressed()
            mouse.update(e)

            # start detect eventTypes
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
                if e.button == BTN_MOUSERIGHT:
                    types.add(EV_RCLICK) # right click
                types.add(EV_MOUSEDOWN) # mouse down
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button not in (BTN_MOUSEUP, BTN_MOUSEDOWN):
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
            elif e.type == pg.VIDEORESIZE:
                self.size = e.size
                print e
            self._underMouse = underMouse
            for t in types:
                if t == EV_KEYPRESS:
                    if e.key == K_TAB:
                        self.tab_focus(e)
                    elif focus.get_focus() is not None:
                        # feed input into focused object
                        focus.get_focus().input(e)
                else:
                    self.on_event(t, e) # invoke the handler

    def mainloop(self):
        self._quit = False
        tm = pg.time.Clock()
        while not self._quit:
            self.handle_event()
            #update timers
            Timer.update_all(1./FPS)
            # update graphic
            self.update()
            pg.display.flip()
            # delay
            tm.tick(FPS)

    def quit(self):
        self._quit = True
