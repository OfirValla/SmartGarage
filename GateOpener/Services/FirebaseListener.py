from colorama import Fore, Style

from firebase_admin import credentials
from firebase_admin import db
from dacite import from_dict

from threading import Thread

from Models.GateRequest import GateRequest
from Models.User import User
from Services.DiscordSender import send_discord_message

import firebase_admin

class FirebaseListener:
    def __init__(self, on_command):
        json_path = "valla-projects-firebase-adminsdk-3ogbz-2ec52a9c7b.json"
        project_id = "valla-projects"
        options = {"databaseURL": "https://valla-projects-default-rtdb.firebaseio.com"}

        print(f"Connecting to {Fore.LIGHTGREEN_EX}Firebase{Style.RESET_ALL}")

        self.cred = credentials.Certificate(json_path)
        self.app = firebase_admin.initialize_app(
            credential=self.cred, options=options, name=project_id
        )
        self.on_command = on_command
        self.is_running_command = False
        self.authed_users = []

        print(f" * {Fore.LIGHTGREEN_EX}Connected{Style.RESET_ALL}")

        self.__remove_old_commands()

        print(f"{Fore.LIGHTGREEN_EX}Start listening to events{Style.RESET_ALL}")
        db.reference("gate-controller/authed-users", app=self.app).listen(
            self.__authed_users_listener
        )
        db.reference("gate-controller/commands", app=self.app).listen(self.__listener)

    # ------------------------------------------------------------------ #

    def __remove_old_commands(self):
        print("Removing old commands")
        keys = list(db.reference("gate-controller/commands", app=self.app).get().keys())
        for key in keys:
            if key == "placeholder":
                continue

            print(f" * {Fore.LIGHTRED_EX}Removing: {key}{Style.RESET_ALL}")
            db.reference("gate-controller/commands", app=self.app).child(key).delete()

    # ------------------------------------------------------------------ #

    def __authed_users_listener(self, event: db.Event):
        if event.event_type == "put":
            self.authed_users = event.data
            return

        # patch event
        new_emails = list(event.data.values())
        for email in new_emails:
            self.authed_users.append(email)

    # ------------------------------------------------------------------ #

    def __listener(self, event: db.Event):
        if not event.data:
            return

        # Skip initial event
        if event.path == "/":
            return
        
        if "placeholder" == event.data["type"]:
            print(f"{Fore.LIGHTWHITE_EX}{event.path} is placeholder{Style.RESET_ALL}")
            return
        
        request = from_dict(data_class= GateRequest, data= event.data)

        # Check if the user is authed
        if request.user.email not in self.authed_users:
            print(f"{Fore.LIGHTRED_EX}{request.user.email} is not authorized{Style.RESET_ALL}")
            send_discord_message(request.user, 'Un-authorized access', 'Not authorized to open or close the gate')
            return
        
        # If multiple commands arrive execute only once
        # Execute only one command
        if not self.is_running_command:
            t = Thread(target=self.__execute_command, args=(request,))
            t.daemon = True
            t.start()

        # Delete command
        db.reference(f"gate-controller/commands{event.path}", app=self.app).delete()

    # ------------------------------------------------------------------ #

    def __execute_command(self, request: GateRequest):
        self.is_running_command = True
        print(f" * Executing command: {Fore.LIGHTYELLOW_EX}{request.type}{Style.RESET_ALL}")
        self.on_command(request)
        self.is_running_command = False