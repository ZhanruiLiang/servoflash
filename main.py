import pgui
import time
import servo

root = pgui.Root(bgcolor=(0xee, 0xee, 0xee, 0xff), 
        size=(pgui.SCREEN_W, pgui.SCREEN_H))
# set up the fps meter
fpsmeter = pgui.FPSMeter(root, pos=(0, 0))
# set up the controller
controller = servo.ServoControl(root, size=(600, 700), pos=(30, 10))
controller.new_servos()
# set up the attribute board
attrs = servo.AttrBoard(root, size=(250, 400), pos=(650, 10))
def on_select(aServo):
    # aServo is selected
    attrs.show(aServo, controller.SERVO_ATTRS)
controller.on_select = on_select

# set up the operation board
# TODO

def on_loop():
    fpsmeter.count()
root.on_loop = on_loop
print 'startup time: %.2f sec' % (time.clock())
root.mainloop()
