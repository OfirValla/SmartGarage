from Utils.FirebaseListener import FirebaseListener
from GateRadioController import operate_gate
from Models.GateRequest import GateRequest

import dataclasses
import time

# ------------------------------------------------------------------ #

def __open_or_close(**_):
    print("Open or Close")
    operate_gate()


def __open_and_close(delay_in_seconds = 90, **_):
    print("Open gate")
    operate_gate()

    time.sleep(delay_in_seconds)
    
    print("Close gate")
    operate_gate()


requests = {
    'open&close': __open_and_close,
    'open|close': __open_or_close
}

# ------------------------------------------------------------------ #

def on_command(request: GateRequest):
    requests[request.type](**dataclasses.asdict(request))

# ------------------------------------------------------------------ #

FirebaseListener(on_command)