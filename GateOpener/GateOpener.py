#from GateRadioController import operate_gate
from Utils.FirebaseListener import FirebaseListener
from Models.GateRequest import GateRequest

import time

# ------------------------------------------------------------------ #

def __open_or_close():
    print("Open or Close")
    #operate_gate()


def __open_and_close():
    print("Open gate")
    #operate_gate()

    time.sleep(60 * 3)
    
    print("Close gate")
    #operate_gate()


requests = {
    'open&close': __open_and_close,
    'open|close': __open_or_close
}

# ------------------------------------------------------------------ #

def on_command(request: GateRequest):
    requests[request.type]()

# ------------------------------------------------------------------ #

FirebaseListener(on_command)