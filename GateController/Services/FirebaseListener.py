from colorama import Fore, Style

from firebase_admin import credentials
from firebase_admin import db
from dacite import from_dict

from threading import Thread

from Models.GateRequest import GateRequest
from Models.User import User
from Services.DiscordSender import send_discord_message

import firebase_admin
import dataclasses
import datetime 
import time
import os

class FirebaseListener:
    def __init__(self, on_command):
        access_key_path = os.getenv('ACCESS_KEY_PATH')

        json_path = os.path.join(access_key_path, "valla-projects-gate-controller.json")
        project_id = "valla-projects"
        options = {"databaseURL": "https://valla-projects-default-rtdb.firebaseio.com"}

        print(f"Connecting to {Fore.LIGHTGREEN_EX}Firebase{Style.RESET_ALL}")

        self.cred = credentials.Certificate(json_path)
        self.app = firebase_admin.initialize_app(
            credential=self.cred, options=options, name=project_id
        )
        self.on_command = on_command
        self.is_running_command = False

        print(f" * {Fore.LIGHTGREEN_EX}Connected{Style.RESET_ALL}")

        self.__remove_old_commands()

        print(f" * {Fore.LIGHTGREEN_EX}Starting program status report thread{Style.RESET_ALL}")
        self.status_report_thread = Thread(target=self.__report_program_status_thread, args=())
        self.status_report_thread.daemon = True
        self.status_report_thread.start()

        print(f"{Fore.LIGHTGREEN_EX}Start listening to events{Style.RESET_ALL}")
        db.reference("gate-controller/commands", app=self.app).listen(self.__listener)

    # ------------------------------------------------------------------ #

    def __remove_old_commands(self) -> None:
        print("Removing old commands")
        keys = list(db.reference("gate-controller/commands", app=self.app).get().keys())
        for key in keys:
            if key == "placeholder":
                continue

            print(f" * {Fore.LIGHTRED_EX}Removing: {key}{Style.RESET_ALL}")
            db.reference("gate-controller/commands", app=self.app).child(key).delete()

    # ------------------------------------------------------------------ #

    def __report_program_status_thread(self) -> None:
        while True:
            db.reference(f"gate-controller/program-status", app=self.app).set(datetime.datetime.now().isoformat())
            time.sleep(1)
            
    # ------------------------------------------------------------------ #

    def __listener(self, event: db.Event) -> None:
        if not event.data:
            return

        # Skip initial event
        if event.path == "/":
            return
        
        if "placeholder" == event.data["type"]:
            print(f"{Fore.LIGHTWHITE_EX}{event.path} is placeholder{Style.RESET_ALL}")
            return
        
        request = from_dict(data_class= GateRequest, data= event.data)

        # Delete command
        db.reference(f"gate-controller/commands{event.path}", app=self.app).delete()

        # If multiple commands arrive execute only once
        # Execute only one command
        if not self.is_running_command:
            t = Thread(target=self.__execute_command, args=(request,))
            t.daemon = True
            t.start()
            
    # ------------------------------------------------------------------ #

    def __execute_command(self, request: GateRequest) -> None:
        self.is_running_command = True
        print(f" * Executing command: {Fore.LIGHTYELLOW_EX}{request.type}{Style.RESET_ALL}")
        self.on_command(request)
        self.is_running_command = False