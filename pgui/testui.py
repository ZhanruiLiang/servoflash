from root import Root
from button import *
from label import *
from dragbar import *
from textbox import TextBox
from inputbox import InputBox
from menu import Menu

def barker(msg):
    def bark(*args):
        print msg, args
    return bark
def callback1(e):
    label.text = e.unicode

root = Root(bgcolor=(0x3f, 0xff, 0xff, 0xff), size=(800, 600))
label = Label(root, text="hello", pos=(300, 200), size=(100, 30))
label = Label(root, text="world", pos=(300, 250), size=(100, 30), 
        align=Label.ALIGN_LEFT)
label = Label(root, text="david", pos=(300, 300), size=(100, 30), 
        align=Label.ALIGN_RIGHT)

button = Button(root, caption="Click Me", pos=(300, 400), size=(100, 30))
button.bind(EV_CLICK, barker("How dare you!"))
root.bind(EV_KEYPRESS, callback1)
src = (
"""
The textbox works!

This is the third line.
    The fourth line with 4 leading spaces.

    def handle_event(self, event):
        "event is in the pygame event type"
        if event.type == pg.MOUSEBUTTONDOWN:
            btn = event.button
            if btn == 1:
                pass
            elif btn == 2:
                # TODO: implement copy to clipboard by right click
                pass
            elif btn == 4:
                self.scroll(-1)
            elif btn == 5:
                self.scroll(1)
            return True
        if event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_UP:
                self.scroll(-1)
            elif key == pg.K_DOWN:
                self.scroll(1)
        return False
End.
"""
)
# textbox = TextBox(root, level=120, pos=(100, 20), size=(500, 400), 
#         color=(0xff, 0xff, 0xff, 0xff), bgcolor=(0, 0, 0, 0x9f),
#         text=src, wrapping=True, fontsize=12)
# drag = DragBar(root, pos=(650, 10), size=(20, 500), vertical=True,
#             minvalue=0, maxvalue=len(textbox.lines)-1)
def scroll(e):
    if e.button == BTN_MOUSEUP:
        textbox.scroll(-1)
    elif e.button == BTN_MOUSEDOWN:
        textbox.scroll(1)
    drag.value = textbox.curline

# textbox.bind(EV_MOUSEDOWN, scroll)
# drag.bind_on_change(lambda: textbox.scroll_to(int(drag.value)))
# drag.bind_on_change(lambda: setattr(button, "size", (5*(1 + int(drag.value)), 30)))

inputbox = InputBox(root, pos=(20, 200), size=(60, 20))
inputbox = InputBox(root, pos=(20, 250), size=(50, 20))
inputbox = InputBox(root, pos=(20, 300), size=(40, 20))
inputbox = InputBox(root, pos=(20, 350), size=(30, 20))

menu = Menu(root, pos=(10, 10), vertical=False)
menu.add_item('bark1', barker('bark1'))
menu.add_item('bark2', barker('bark2'))
menu.add_item('bark3', barker('bark3'))

root.mainloop()

