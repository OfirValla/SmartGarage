from RPi import GPIO
import time

# ------------------------------------------------------------------ #

_gpio = 27

# ------------------------------------------------------------------ #

def _sleep_microseconds(ms):
    delayInSeconds = ms / 1000000
    _delayInSeconds = delayInSeconds / 100
    end = time.time() + delayInSeconds - _delayInSeconds
    while time.time() < end:
        time.sleep(_delayInSeconds)

# ------------------------------------------------------------------ #

def _pulse(high, low):
    GPIO.output(_gpio, GPIO.HIGH)
    _sleep_microseconds(high)
    GPIO.output(_gpio, GPIO.LOW)
    _sleep_microseconds(low)

# ------------------------------------------------------------------ #

def _send_code():
    _pulse(320, 320)
    _pulse(676, 320)
    _pulse(676, 320)
    _pulse(676, 320)
    _pulse(676, 676)
    _pulse(320, 320)
    _pulse(676, 676)
    _pulse(320, 320)
    _pulse(676, 320)
    _pulse(676, 676)
    _pulse(320, 320)
    _pulse(676, 320)
    _pulse(676, 10004)

# ------------------------------------------------------------------ #

def operate_gate():
    print("Open/Close gate")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(_gpio, GPIO.OUT)

    #for _ in range(0, 20):
    _send_code()

    GPIO.cleanup()

# ------------------------------------------------------------------ #
