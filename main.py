import sys, os
import pgui
import time
import servo
import pygame as pg
from mainmenu import MainMenu
from config import *
from oprboard import OprBoard
from attrboard import AttrBoard
from pgui import Timer

root = pgui.Root(bgcolor=(0x3e, 0x3e, 0x3e, 0xff), 
        size=(SCREEN_W, SCREEN_H))

def on_loop():
    fpsmeter.count()
    # self = controller
    # servo = self.servos[self.actived]
    # ti = servo.selected
    # if ti is None:
    #     ti = 0
    # else:
    #     ti += 1
    # servo.select(ti)
    # self.on_select(servo)
    # servo.mark_redraw()
def on_quit():
    # mmenu.prompt_unsaved()
    controller.auto_save()
def print_info(*args):
    controller.debug_print()
    print 'Timers:', len(Timer.timers)

Timer.add(Timer(AUTOSAVE_INTERVAL, lambda *args: controller.auto_save()))


root.on_loop = on_loop
root.on_quit = on_quit
root.bind_key(pg.K_p, print_info, [pg.KMOD_CTRL])
# set up the fps meter
fpsmeter = pgui.FPSMeter(root, level=2000)
fpsmeter.pos = (800, 690)

# set up the controller
controller = servo.ServoControl(root, 
        size=(CONTROLLER_W, CONTROLLER_H),
        pos=(1, MENU_H))

# set up the attribute board
attrs = AttrBoard(root,
        bgcolor=PANEL_BG,
        size=(RIGHT_PANEL_W, 180), pos=(CONTROLLER_W + 5, MENU_H))
def on_select_servo(aServo):
    # aServo is selected
    attrs.show_info(aServo, controller.SERVO_ATTRS, controller.SERVO_ATTR_EVALS)
    on_select(aServo)

# set up the operation board
oprs = OprBoard(root, bgcolor=PANEL_BG, 
        size=(RIGHT_PANEL_W, 100),
        pos=(CONTROLLER_W + 5, 185 + 5 + MENU_H))
oprs.servoc = controller
def on_select(servo):
    oprs.update_info()
controller.on_select_servo = on_select_servo
controller.on_select= on_select

# set up the main menu
mmenu = MainMenu(root, controller, level=200, pos=(1, 0))

# start mainloop 
# controller.new_servos()
controller.slmgr.load_last()
root.show_hint('startup time: %.2f sec' % (time.clock()))

# root.bind_key(pg.K_t, lambda e:controller.slmgr.load('save3'))
root.mainloop()
# print pg.display.Info()
