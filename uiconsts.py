# event types
EV_CLICK = 'click'
EV_RCLICK = 'rclick'
EV_MOUSEDOWN = 'mousedown'
EV_MOUSEUP = 'mouseup'
EV_MOUSEOVER = 'mouseover'
EV_MOUSEOUT = 'mouseout'
EV_DRAGOVER = 'dragover'
EV_DRAGOUT = 'dragout'
EV_KEYPRESS = 'keypress'

# event flow block mode
BLK_PRE_BLOCK = 1
BLK_PRE_NONBLOCK = 0
BLK_POST_BLOCK = 3
BLK_POST_NONBLOCK = 2

PG_NUM = 323 # key state list length of pygame.key.get_pressed
MOUSE_BUTTON_NUM = 5
KEY_NUM = PG_NUM + MOUSE_BUTTON_NUM

# mouse buttons
K_MOUSELEFT = PG_NUM
K_MOUSERIGHT = PG_NUM + 1
K_MOUSEMID = PG_NUM + 2
K_MOUSEUP = PG_NUM + 3
K_MOUSEDOWN = PG_NUM + 4

