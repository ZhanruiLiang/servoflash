from pgui.root import Root
from pgui.button import *
from pgui.label import *
from pgui.dragbar import *
from pgui.textbox import TextBox
from pgui.inputbox import InputBox
from pgui.menu import Menu
from servo import ServoControl, ServoBoard

def barker(msg):
    def bark(*args):
        print msg, args
    return bark

root = Root(bgcolor=(0xef, 0xef, 0xff, 0xff), size=(1024, 768))
# label = Label(root, text="hello", pos=(300, 200), size=(100, 30))
# label = Label(root, text="world", pos=(300, 250), size=(100, 30), 
#         align=Label.ALIGN_LEFT)
# label = Label(root, text="david", pos=(300, 300), size=(100, 30), 
#         align=Label.ALIGN_RIGHT)
# 
# button = Button(root, caption="Click Me", pos=(300, 400), size=(100, 30))
# button.bind_command(barker("How dare you!"))
def quit(event):
    if event.type == KEYDOWN:
        if event.key == K_q:
            root.quit()
        else:
            return True
root.bind(EV_KEYPRESS, quit, BLK_POST_BLOCK)
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
# textbox = TextBox(root, level=120, pos=(100, 20), size=(500, 200), 
#         color=(0xff, 0xff, 0xff, 0xff), bgcolor=(0, 0, 0, 0x9f),
#         text=src, wrapping=True, fontsize=12)
# drag = DragBar(root, pos=(650, 10), size=(20, 500), vertical=True,
#             minvalue=0, maxvalue=len(textbox.lines)-1)
# 
# def scroll(e):
#     drag.value = textbox.curline
# 
# textbox.bind(EV_MOUSEDOWN, scroll)
# 
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

controller = ServoControl(root, size=(800, 700), pos=(200, 10))
controller.new_servos()
# ser1 = ServoBoard(root, sid=3, bias=512, size=(630, 100), pos=(100, 20), direction=1)
# ser2 = ServoBoard(root, sid=3, bias=512, size=(630, 100), pos=(100, 122), direction=1)
# 
root.mainloop()
