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

    TOP_LEVEL = 1000

    instance = None

    def __init__(self, *args, **dargs):
        if Root.instance is not None:
            raise Exception("you cannot has more than one Root instance.")
        super(Root, self).__init__(None, *args, **dargs)
        Root.instance = self

    def init(self):
        import hint
        pg.display.set_caption(self.caption)
        pg.key.set_repeat(400, 50)
        self._quit = False
        self._underMouse = []
        self._timers = []
        self._dialogQueue = []
        self.dialog = None
        self.hinter = hint.PopupHinter(self, pos=(0, self.size[1]), level=self.TOP_LEVEL)
        self.warner= hint.PopupHinter(self, level=self.TOP_LEVEL,
                pos=(500, self.size[1]), 
                bgcolor=(0xff, 0x4f, 0x4c, 0xff))

        self.bind_key(K_q, self.quit)

    def tab_focus(self, event):
        if event.mod & KMOD_SHIFT:
            focus.set_focus(focus.prev_focus())
        else:
            focus.set_focus(focus.next_focus())

    def hide(self):
        pg.display.iconify()

    def show(self):
        pass

    def resize(self, size):
        self.size = size
        # self.image = pg.display.set_mode(self.size, VFLAG, 32)
        self.image=  pg.display.get_surface()
        self.rect = pg.Rect(self.pos, size)
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
            mouse.update(e)

            # start detect eventTypes
            types = set()
            underMouse = []
            self.get_all_under_mouse(mouse.pos, underMouse.append)
            for ui in self._underMouse:
                if ui not in underMouse:
                    # mouse move out of this ui just now
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
                pg.display.set_mode(e.size, VFLAG, 32)
                self.resize(e.size)
                print 'main window resized'
                self.mark_redraw()
            self._underMouse = underMouse
            for t in types:
                flag = 0
                if t == EV_KEYPRESS:
                    if e.key == K_TAB:
                        self.tab_focus(e)
                        flag = 1
                    elif focus.get_focus() is not None and e.key == K_ESCAPE:
                        focus.set_focus(None)
                        flag = 1
                    elif focus.get_focus() is not None:
                        # feed input into focused object
                        if not focus.get_focus().input(e):
                            flag = 1
                if not flag:
                    self.on_event(t, e) # invoke the handler

    def on_loop(self):
        pass

    def show_hint(self, hint):
        print '[HINT]:',hint
        self.hinter.show_hint(hint)

    def show_warn(self, msg):
        print '[WARN!]:', msg
        self.warner.show_hint(msg)

    DIALOG_LEVEL = TOP_LEVEL
    def show_dialog(self, dialog):
        dialog.hide()
        self._dialogQueue.append(dialog)
        self._dialogQueue.sort(cmp=lambda x,y:y.emergency-x.emergency)
        if self.dialog is None:
            self._show_dialog()

    def _show_dialog(self):
        if not self._dialogQueue: return
        # fetch the dialog
        dialog = self._dialogQueue[0]
        del self._dialogQueue[0]
        dialog.show()
        # draw bg
        if not hasattr(self, '_diaglogBG'):
            self._diaglogBG = UIBase(self, 
                    level=self.DIALOG_LEVEL-1, 
                    size=self.size,
                    bgcolor=(0, 0, 0, 0x88))
            self._diaglogBG.bind(EV_MOUSEDOWN, lambda e:None, BLK_PRE_BLOCK)
            self._diaglogBG.bind(EV_KEYPRESS, lambda e:None, BLK_PRE_BLOCK)
        else:
            if self._diaglogBG.size != self.size:
                self._diaglogBG.resize(self.size)
            self._diaglogBG.show()
        self.dialog = dialog

    def hide_dialog(self):
        self.dialog.destory()
        self.dialog = None
        self._diaglogBG.hide()
        self._show_dialog()

    def mainloop(self):
        self._quit = False
        tm = pg.time.Clock()
        while not self._quit:
            self.handle_event()
            #update timers
            Timer.update_all()
            self.on_loop()
            # update graphic
            rect = self.update()
            if rect: 
                pg.display.update(rect)
            # pg.display.flip()
            # delay
            tm.tick(FPS)

    def quit(self, *args):
        print 'quit'
        self._quit = True

def warn(msg):
    Root.instance.show_warn(msg)

def hint(msg):
    Root.instance.show_hint(msg)
