import sys, os
import pgui
import time
import servo
from mainmenu import MainMenu
from config import *
from oprboard import OprBoard
from attrboard import AttrBoard

root = pgui.Root(bgcolor=(0x3e, 0x3e, 0x3e, 0xff), 
        size=(pgui.SCREEN_W, pgui.SCREEN_H))

def on_loop():
    fpsmeter.count()
    # print pgui.eventh.mouse.pos
root.on_loop = on_loop
# set up the fps meter
fpsmeter = pgui.FPSMeter(root, level=2000, pos=(700, 600))

# set up the controller
controller = servo.ServoControl(root, 
        size=(CONTROLLER_W, CONTROLLER_H),
        pos=(1, MENU_H))
controller.new_servos()

# set up the attribute board
attrs = AttrBoard(root,
        bgcolor=PANEL_BG,
        size=(RIGHT_PANEL_W, 150), pos=(CONTROLLER_W + 5, MENU_H))
def on_select_servo(aServo):
    # aServo is selected
    attrs.show_info(aServo, controller.SERVO_ATTRS, controller.SERVO_ATTR_EVALS)
controller.on_select_servo = on_select_servo
controller.select_servo(controller.actived)

# set up the operation board
oprs = OprBoard(root, bgcolor=PANEL_BG, 
        size=(RIGHT_PANEL_W, 100),
        pos=(CONTROLLER_W + 5, 150 + 5 + MENU_H))
oprs.servoc = controller
def on_select(servo):
    if servo.selected is not None:
        oprs.input_angle.text = str(servo.get_a_at(servo.selected))
        oprs.input_angle.mark_redraw()
controller.on_select= on_select

# set up the main menu
mmenu = MainMenu(root, controller, level=200, pos=(1, 0))

# start mainloop 
root.show_hint('startup time: %.2f sec' % (time.clock()))
root.mainloop()
