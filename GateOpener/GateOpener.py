from GateRadioController import operate_gate, cleanup

from Services.DiscordSender import send_discord_message
from Services.FirebaseListener import FirebaseListener
from Models.GateRequest import GateRequest
from Models.User import User

import threading
import signal
import time
import sys

# ------------------------------------------------------------------ #

def __open_or_close(user: User, **_) -> None:
    send_discord_message(user, 'Open or Close', 'Openning or Closing the gate')
    operate_gate()


def __open_and_close(user: User, delay_in_seconds: int = 90, **_) -> None:
    send_discord_message(user, 'Open', 'Openning the gate')
    operate_gate()

    time.sleep(delay_in_seconds)
    
    send_discord_message(user, 'Close', 'Closing the gate')
    operate_gate()


requests = {
    'open&close': __open_and_close,
    'open|close': __open_or_close
}

# ------------------------------------------------------------------ #

def on_command(request: GateRequest) -> None:
    requests[request.type](user= request.user, **request.data)

# ------------------------------------------------------------------ #

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    cleanup()
    sys.exit(0)

# ------------------------------------------------------------------ #

FirebaseListener(on_command)

signal.signal(signal.SIGINT, signal_handler)

print('Press Ctrl+C')
forever = threading.Event()
forever.wait()