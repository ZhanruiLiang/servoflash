from ui import *

class Menu(UIBase):
    AllArgs = update_join(UIBase.AllArgs, 
            )
    ArgsOrd = ord_join(UIBase.ArgsOrd,
            []
            )
    assert sorted(AllArgs.keys()) == sorted(ArgsOrd)

