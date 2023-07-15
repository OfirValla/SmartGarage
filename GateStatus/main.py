from Services.DiscordSender import send_log_message, send_status_update
from Services.CameraHandler import CameraHandler
from Services.MLHandler import MLHandler
from Services.Firebase import Firebase

from Models.Status import Status

from datetime import datetime

import time
import cv2

# --------------------------------------------------------------------------------------------------- #

def main():
    send_log_message("GateStatus - Starting")

    firebase = Firebase()
    camera_manager = CameraHandler()
    model = MLHandler()

    last_status = ""
    last_time = time.time()

    while True:
        success, frame = camera_manager.camera().read()
        
        if not success:
            camera_manager.camera(reset= True)
        
        # Skip empty frames
        if frame is None:
            continue

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break

        curr_time = time.time()

        original_frame = frame
        
        frame, _ = model.preprocess_image(frame)
        
        if curr_time - last_time < .5:
            continue
        last_time = curr_time
        
        class_name, confidence_score = model.predict(frame)

        # Skip predictions with lower than 75% confidence
        if confidence_score < 75:
            continue

        # On prediction change send alert to discord
        if last_status != class_name:
            if class_name == 'Opening|Closing' and last_status == 'Open':
                class_name = 'Closing'
            elif class_name == 'Opening|Closing' and last_status == 'Closed':
                class_name = 'Opening'

            last_status = class_name
            print(datetime.now())
            print(f"Class: {class_name}")
            print(f"Confidence Score: {str(confidence_score)[:-2]}%")
            
            new_status = Status(
                current_status= class_name, 
                confidence_score= int(str(confidence_score)[:-2]),
                timestamp= time.time()
            )
            firebase.update_status(new_status)
            send_status_update(new_status, cv2.imencode('.jpg', original_frame)[1])
            
# --------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()