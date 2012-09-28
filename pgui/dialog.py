from ui import *
from inputbox import InputBox
from textbox import TextBox
from timer import Timer
from root import Root
from label import Label
from button import Button

class Dialog(UIBase):
    def __repr__(self):
        return super(Dialog, self).__repr__(self)+'(%d)' % self.emergency

    def __init__(self, msg, callbackOnConfrim, emergency=0, default='', **dargs):
        """
        msg: the prompt message
        default: the default input text
        callbackOnConfrim: shoud be a function with the inputed string as the argument
        """
        self.emergency = emergency
        root = Root.instance
        size = 400, 260
        super(Dialog, self).__init__(root, 
                size=size, 
                pos=((root.size[0]-size[0])/2, (root.size[1]-size[1])/2),
                bgcolor=(0x9f, 0xaf, 0xff, 0xff),
                level=Root.DIALOG_LEVEL,
                **dargs
                )
        self.msgbox = TextBox(self, text=msg,
                pos=(5, 5),
                size=(390, 200),
                bgcolor=(0, 0, 0, 0x88), color=(0xff, 0xff, 0xff),
                fontsize=14,
                )
        self.input = InputBox(self, text=default,
                pos=(5, 210),
                size=(390, 20),
                )
        btn_confirm = Button(self, pos=(5, 235), caption="confirm", size=(100, 20))
        btn_cancel = Button(self, pos=(295, 235), caption="cancel", size=(100, 20))

        self.callbackOnConfrim = callbackOnConfrim
        btn_confirm.bind_command(self.confirm)
        btn_cancel.bind_command(self.cancel)
        self.bind_key(K_ESCAPE, self.cancel)

        self.input.set_as_focus()

    def confirm(self, event):
        self.callbackOnConfrim(self.input.text)
        self.parent.hide_dialog()
        focus.set_focus(None)

    def cancel(self, event):
        print 'cancel'
        self.parent.hide_dialog()
        focus.set_focus(None)

class OptionDialog(UIBase):
    def __init__(self, msg, options, callback, emergency=0, **dargs):
        root = Root.instance
        itemsize = (80, 20)
        margin = 5
        self.emergency = emergency
        size = ((itemsize[0]+margin)*len(options)+margin, 
                200+3*margin+itemsize[1])
        super(OptionDialog, self).__init__(root,
                size=size,
                pos=((root.size[0]-size[0])/2, (root.size[1]-size[1])/2),
                bgcolor=(0x9f, 0xaf, 0xff, 0xff),
                level=Root.DIALOG_LEVEL,
                **dargs
                )
        TextBox(self, text=msg, pos=(margin, margin), size=(size[0]-2*margin, 200),
                bgcolor=(0, 0, 0, 0x88), color=(0xff, 0xff, 0xff),
                fontsize=14,
                )
        self.callback = callback
        for i, opt in enumerate(options):
            btn = Button(self, 
                    pos=(margin+i*(itemsize[0]+margin), 200+2*margin),
                    caption=opt, size=itemsize)
            btn.bind_command(lambda i=i:self.choose(i))

    def choose(self, i):
        self.callback(i)
        self.parent.hide_dialog()

class InfoDialog(Label):
    def __init__(self, msg, emergency=0, **dargs):
        root = Root.instance
        self.emergency = emergency
        super(InfoDialog, self).__init__(root, 
                autosize=True, text=msg,**dargs)
