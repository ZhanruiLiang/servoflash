
_focus = None

def set_focus(obj):
    global _focus
    if _focus is not None:
        _focus.on_lost_focus()
    _focus = obj
    _focus.on_focus()

def get_focus():
    return _focus

class Focusable:
    def on_focus(self):
        pass

    def input(self):
        pass

    def on_lost_focus(self):
        pass

    def set_as_focus(self, event):
        set_focus(self)
