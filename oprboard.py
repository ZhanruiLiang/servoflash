from pgui import UIBase, Button, Label, InputBox, Root 
from pgui.uiconsts import *
from pgui.root import warn, hint
import pygame as pg

class OprBoard(UIBase):
    def init(self):
        margin = 4
        btnSize=(50, 25)
        # home, play/pause, end, sync
        # button home
        btn_home = Button(self, caption='<<',
                pos=(margin , margin), size=(btnSize))
        btn_home.bind_command(self.cb_home)
        btn_home.bind_key(K_6, self.cb_home, [KMOD_SHIFT]) # key ^
        # button play
        self.btn_play = btn_play = Button(self, caption='play', 
                pos=(margin + btnSize[0] + 1, margin), size=(btnSize))
        btn_play.bind_command(self.cb_play)
        # button pause
        self.btn_pause = btn_pause = Button(self, caption='pause', 
                bgcolor=(0x8f, 0, 0, 0xff), hovercolor=(0xff, 0, 0, 0xff),
                pos=(margin + btnSize[0] + 1, margin), size=(btnSize))
        btn_pause.hide()
        btn_pause.bind_command(self.cb_pause)
        self.bind_key(pg.K_SPACE, self.cb_toggle)
        # button end
        btn_end = Button(self, caption='>>', 
                pos=(margin + 2*(btnSize[0] + 1), margin), size=(btnSize))
        btn_end.bind_command(self.cb_end)
        btn_end.bind_key(K_4, self.cb_end, [KMOD_SHIFT]) # key $
        # button sync
        self.btn_sync = btn_sync = Button(self, caption='sync', 
                pos=(margin + 3*(btnSize[0] + 1), margin), size=(btnSize))
        btn_sync.bind_command(self.cb_sync)
        btn_sync.bind_key(K_o, self.cb_sync)
        # button unsync
        self.btn_unsync = btn_unsync = Button(self, caption='unsync', 
                bgcolor=(0x8f, 0, 0, 0xff), hovercolor=(0xff, 0, 0, 0xff),
                pos=(margin + 3*(btnSize[0] + 1), margin), size=(btnSize))
        btn_unsync.bind_command(self.cb_unsync)
        btn_unsync.bind_key(K_o, self.cb_unsync, [KMOD_SHIFT])
        # the next line
        # angle: [   ]
        label_angle = Label(self, text='angle:',
                pos=(margin, margin+btnSize[1]), size=btnSize)
        self.input_angle = InputBox(self, 
                pos=(margin + btnSize[0] + 1, margin+btnSize[1]),
                size=btnSize)
        self.input_angle.bind_on_confirm(self.cb_angle)
        # other values
        self.servoc = None

    def cb_home(self, *args):
        self.servoc.goto_frame(0)

    def cb_end(self, *args):
        servoc = self.servoc
        servo = servoc.servos[servoc.actived]
        servoc.goto_frame(servo.total_frame())

    def cb_play(self, *args):
        if self.btn_play.is_visible():
            hint('start playing')
            self.servoc.play()
            self.btn_play.hide()
            self.btn_pause.show()

    def cb_toggle(self, *args):
        if self.btn_pause.is_visible():
            hint('paused')
            self.servoc.pause()
            self.btn_play.show()
            self.btn_pause.hide()
        else:
            hint('start playing')
            self.servoc.play()
            self.btn_play.hide()
            self.btn_pause.show()

    def cb_pause(self, *args):
        if self.btn_pause.is_visible():
            hint('paused')
            self.servoc.pause()
            self.btn_play.show()
            self.btn_pause.hide()

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

    def cb_sync(self, *args):
        if self.btn_sync.is_visible():
            self.btn_sync.hide()
            self.btn_unsync.show()
            self.servoc.connect_robot()

    def cb_unsync(self, *args):
        if self.btn_unsync.is_visible():
            self.btn_unsync.hide()
            self.btn_sync.show()
            self.servoc.disconnect_robot()

    def update_info(self):
        servoc = self.servoc
        servo = servoc.servos[servoc.actived]
        if servo.selected is not None:
            self.input_angle.text = str(servo.get_a_at(servo.selected))
            self.input_angle.mark_redraw()
