
_focus = None

def set_focus(obj):
    global _focus
    if _focus is not None:
        _focus.on_lost_focus()
    _focus = obj
    if obj is not None:
        obj.on_focus()
    return obj

def get_focus():
    return _focus

def next_focus():
    print 'next_focus'
    f = get_focus()
    if f is None:
        if _focusList:
            return _focusList[0]
        else:
            return None
    idx = _focusList.index(f)
    return _focusList[(idx + 1) % len(_focusList)]

def prev_focus():
    f = get_focus()
    if f is None:
        if _focusList:
            return _focusList[-1]
        else:
            return None
    idx = _focusList.index(f)
    return _focusList[idx - 1]

def add_focus_obj(obj, idx=-1):
    if idx == -1:
        _focusList.append(obj)
    else:
        _focusList.insert(idx, obj)

def remove_focus_obj(obj):
    try:
        _focusList.remove(obj)
    except ValueError:
        pass

_focusList = []

class Focusable:
    def __init__(self):
        add_focus_obj(self)

    def on_focus(self):
        pass

    def input(self):
        pass

    def on_lost_focus(self):
        pass

    def set_as_focus(self, event):
        set_focus(self)

