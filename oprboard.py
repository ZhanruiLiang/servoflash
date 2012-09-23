from pgui import UIBase, Button, Label, InputBox, Root 
from pgui.root import warn, hint

class OprBoard(UIBase):
    def init(self):
        margin = 4
        btnSize=(50, 25)
        # home, play/pause, end, sync
        btn_home = Button(self, caption='<<',
                pos=(margin , margin), size=(btnSize))
        btn_play = Button(self, caption='play', 
                pos=(margin + btnSize[0] + 1, margin), size=(btnSize))
        btn_pause = Button(self, caption='pause', 
                pos=(margin + btnSize[0] + 1, margin), size=(btnSize))
        btn_pause.hide()
        btn_end = Button(self, caption='>>', 
                pos=(margin + 2*(btnSize[0] + 1), margin), size=(btnSize))
        btn_sync = Button(self, caption='sync', 
                pos=(margin + 3*(btnSize[0] + 1), margin), size=(btnSize))

        # angle: [   ]
        label_angle = Label(self, text='angle:',
                pos=(margin, margin+btnSize[1]), size=btnSize)
        self.input_angle = InputBox(self, 
                pos=(margin + btnSize[0] + 1, margin+btnSize[1]),
                size=btnSize)
        self.input_angle.bind_on_confirm(self.cb_angle)

        self.servoc = None

    def cb_home(self, *args):
        self.servoc.go_home()

    def cb_end(self, *args):
        self.servoc.go_end()

    def cb_play(self, *args):
        self.servoc.play()

    def cb_pause(self, *args):
        self.servoc.pause()

    def cb_angle(self):
        # v: the new input value
        v = self.input_angle.text
        servoc = self.servoc
        servo = servoc.servos[servoc.actived]
        try:
            v = int(v)
            if servo.selected is not None:
                i, dti = servo.find_ti_pos(servo.selected)
                if i < len(servo.keyFrames) and dti == 0:
                    if servo.min <= v <= servo.max:
                        servo.keyFrames[i].a = v
                        servo.mark_redraw()
                        servo.select(servo.selected)
                    else:
                        warn("angle=%d out of range(%s)" %(v, (servo.min, servo.max)))
                else:
                    warn("cannot set a non-key frame")
        except Exception as ex:
            warn(str(ex))
            self.input_angle.text = ''

