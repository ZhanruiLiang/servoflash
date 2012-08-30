from root import Root
from button import *
from label import *
from dragbar import *

def barker(msg):
    def bark(*args):
        print msg, args
    return bark
def callback1(e):
    label.text = e.unicode

root = Root(bgcolor=(0xff, 0xff, 0xff, 0xff), size=(800, 600))
label = Label(root, text="hello", pos=(300, 200), size=(100, 30))
label.bind(EV_CLICK, barker('mouse click'))

button = Button(root, caption="Click Me", pos=(300, 400), size=(100, 30))
button.bind(EV_CLICK, barker("How dare you!"))
root.bind(EV_KEYPRESS, callback1)
# 
# drag = DragBar(root, pos=(200, 100))
# drag.bind_on_change(lambda: setattr(label, 'text',"%.2f%%" % (100 * drag.percent)))
root.mainloop()

