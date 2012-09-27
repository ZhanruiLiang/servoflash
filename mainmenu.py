import pgui
from pygame.locals import *

class MainMenu(pgui.Menu):
    def __init__(self, root, servoControl, **args):
        """
        items: (according to use frequency)
        - save
        - save as
        - load
        - new
        - help
        """
        super(MainMenu, self).__init__(root, 
                vertical=False, 
                margin=2, itemsize=(60, 22),
                **args)

        self.servoc = servoc = servoControl
        self.add_item('save', self.cb_save)
        self.add_item('save as', self.cb_save_as)
        self.add_item('load', self.cb_load)
        self.add_item('new', self.cb_new)
        self.add_item('add', self.cb_add_servo)
        self.add_item('help', self.cb_help)
        self.add_item('quit', self.cb_quit)

        self.bind_key(K_l, self.cb_load, [KMOD_CTRL])
        self.bind_key(K_s, self.cb_save, [KMOD_CTRL])
        self.bind_key(K_s, self.cb_save_as, [KMOD_CTRL, KMOD_SHIFT])
        self.bind_key(K_q, self.cb_quit)

    def cb_quit(self, *args):
        pgui.Root.instance.quit()

    def cb_save_as(self, *args):
        prompt = "Save as: Type in the file path to save."
        slmgr = self.servoc.slmgr
        pgui.Root.instance.show_dialog(pgui.Dialog(
            prompt, lambda p:slmgr.save(p),
            20, # emergency
            slmgr.lastSave or ''))

    def cb_save(self, *args):
        slmgr = self.servoc.slmgr
        print 'lastSave', slmgr.lastSave
        if slmgr.lastSave is not None:
            slmgr.save(slmgr.lastSave)
        else:
            self.cb_save_as()

    def cb_load(self, *args):
        slmgr = self.servoc.slmgr
        self.prompt_unsaved()

        prompt = "Load: Type in the file path you want to load."
        pgui.Root.instance.show_dialog(pgui.Dialog(
            prompt, lambda p:slmgr.load(p),
            10, 
            slmgr.lastSave or ''))

    def prompt_unsaved(self):
        servoc = self.servoc
        slmgr = self.servoc.slmgr
        #prompt to save current
        savedData = slmgr.lastSaveData
        prompt = "Current data is not saved. Would you like to save it?"
        if savedData == slmgr.gen_save_data():
            return
        # prompt to save current
        dialog = pgui.OptionDialog(prompt, 
                    ["save", "save as", "discard"], # options
                    self.handle_choice_unsaved)
        pgui.Root.instance.show_dialog(dialog)

    def handle_choice_unsaved(self, choice):
        if choice == 0:
            self.cb_save()
        elif choice == 1:
            self.cb_save_as()
        elif choice == 2:
            pass

    def cb_new(self, *args):
        servoc = self.servoc
        self.prompt_unsaved()
        prompt = "New: Input the servo's number."
        def new(n):
            try:
                n = int(n)
                if 1 <= n <= 50:
                    servoc.new_servos(n)
                else:
                    warn('number must within [1, 50]')
            except ValueError:
                warn('failed. %s is not an integer' % n)
        pgui.Root.instance.show_dialog(pgui.Dialog(
            prompt, new, 10))

    def cb_add_servo(self, *args):
        self.servoc.add_servo()

    def cb_help(self, *args):
        pass
