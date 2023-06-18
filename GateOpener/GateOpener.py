#from GateRadioController import operate_gate
from Utils.FirebaseListener import FirebaseListener
from Models.GateRequest import GateRequest

import time

# ------------------------------------------------------------------ #

def __open_or_close():
    print("Open or Close")


def __open_and_close():
    print("Open gate")
    time.sleep(60 * 3)
    print("Close gate")


requests = {
    'open&close': __open_and_close,
    'open|close': __open_or_close
}

# ------------------------------------------------------------------ #

def on_command(request: GateRequest):
    requests[request.type]()

# ------------------------------------------------------------------ #

FirebaseListener(on_command)