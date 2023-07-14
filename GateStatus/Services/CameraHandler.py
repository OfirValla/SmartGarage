from colorama import Fore, Style

import cv2  # Install opencv-python
import os 

# --------------------------------------------------------------------------------------------------- #

CAMERA_RTSP = os.getenv('RTSP_URL')

# --------------------------------------------------------------------------------------------------- #

class CameraHandler():
    def __init__(self, verbose = False):
        print ("Init camera manager")
        self.video_capture = None
        self.call_counter = 0
        self._verbose = verbose

    def camera(self, reset = False):
        self.call_counter += 1
        if self.call_counter == 100 or reset:
            if self._verbose:
                print("Refreshing camera connection")
                print(" * Closing connection")
            self.call_counter = 0
            
            self.video_capture.release()
            self.video_capture = None

        if self.video_capture is None:
            if self._verbose:
                print(f" * {Fore.LIGHTGREEN_EX}Connecting to camera{Style.RESET_ALL}")
            self.video_capture = cv2.VideoCapture(CAMERA_RTSP, apiPreference=cv2.CAP_FFMPEG)

        return self.video_capture
