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

root = Root(bgcolor=(0xef, 0xef, 0xff, 0xff), size=(800, 600))
label = Label(root, text="hello", pos=(300, 200), size=(100, 30))
label = Label(root, text="world", pos=(300, 250), size=(100, 30), 
        align=Label.ALIGN_LEFT)
label = Label(root, text="david", pos=(300, 300), size=(100, 30), 
        align=Label.ALIGN_RIGHT)

button = Button(root, caption="Click Me", pos=(300, 400), size=(100, 30))
button.bind_command(barker("How dare you!"))
def quit(event):
    if event.type == KEYDOWN:
        if event.key == K_q:
            root.quit()
root.bind(EV_KEYPRESS, quit, BLK_PRE_BLOCK)
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

menu = Menu(root, level=1000, pos=(10, 10), margin=2, itemsize=(120, 28), vertical=True)
menu.add_item('bark1', barker('bark1'))
menu.add_item('bark2', barker('bark2'))
menu.add_item('bark3', barker('bark3'))
menu.add_item('bark3', barker('bark3'))
menu.add_item('bark3', barker('bark3'))
menu.add_item('bark3', barker('bark3'))
menu.add_item('bark3', barker('bark3'))
menu.add_item('bark3', barker('bark3'))
menu.hide()

def show_menu(event):
    if menu.is_visible():
        menu.pos = event.pos
    else:
        menu.pos = event.pos
        menu.show()

root.bind(EV_RCLICK, show_menu, BLK_POST_BLOCK)
root.bind(EV_CLICK, menu.hide, BLK_POST_BLOCK)

root.mainloop()

