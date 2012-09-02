
_focus = None

def set_focus(obj):
    global _focus
    if _focus is not None:
        _focus.on_lost_focus()
    _focus = obj
    if obj is not None:
        obj.on_focus()
    # print 'set_focus', obj
    return obj

def get_focus():
    return _focus

def next_focus():
    f = get_focus()
    focusList = [x for x in _focusList if x.is_visible()]
    if f is None:
        if focusList:
            return _focusList[0]
        else:
            return None
    idx = focusList.index(f)
    return focusList[(idx + 1) % len(focusList)]

def prev_focus():
    f = get_focus()
    focusList = [x for x in _focusList if x.is_visible()]
    if f is None:
        if focusList:
            return focusList[-1]
        else:
            return None
    idx = focusList.index(f)
    return focusList[idx - 1]

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

    def set_as_focus(self, *args):
        if self in _focusList:
            set_focus(self)

