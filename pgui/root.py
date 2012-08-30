from ui import *

class Root(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            caption='"UIRoot"',
            size='(200, 200)',
            parent='None',
            )

    def __init__(self, **dargs):
        super(Root, self).__init__(None, **dargs)

        self.image = pg.display.set_mode(self.size, pg.RESIZABLE, 32)
        self.ownImage = self.image.copy()
        pg.display.set_caption(self.caption)
        self.ownImage.fill(self.bgcolor)

        self._quit = False
        self._underMouse = []

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
            types = set()
            underMouse = []
            self.get_all_under_mouse(mouse.pos, underMouse.append)
            # print 'underMouse', underMouse
            for ui in self._underMouse:
                if ui not in underMouse:
                    # mouse move out this ui just now
                    ui.on_event(EV_MOUSEOUT, e)# invoke the handler
                    if mouse.is_draging():
                        # drag out
                        ui.on_event(EV_DRAGOUT, e)# invoke the handler
            # print mouse
            if mouse.is_clicked():
                types.add(EV_CLICK) # click

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == BTN_MOUSERIGHT:
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

    def mainloop(self, FPS=20):
        self._quit = False
        tm = pg.time.Clock()
        self.redraw()
        while not self._quit:
            self.handle_event()
            self.update()
            pg.display.flip()
            tm.tick(FPS)

    def quit(self):
        self._quit = True
