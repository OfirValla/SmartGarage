from pickle import FALSE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from threading import Thread

from Models.GateRequest import GateRequest
from Models.User import User

class FirebaseListener:
    def __init__(self, on_command):
        json_path = "valla-projects-firebase-adminsdk-3ogbz-2ec52a9c7b.json"
        project_id = "valla-projects"
        options = {"databaseURL": "https://valla-projects-default-rtdb.firebaseio.com"}

        print("Connecting to firebase")

        self.cred = credentials.Certificate(json_path)
        self.app = firebase_admin.initialize_app(
            credential=self.cred, options=options, name=project_id
        )
        self.on_command = on_command
        self.is_running_command = False

        print("Connected")

        self.__remove_old_commands()

        print("Start listening to events")
        db.reference("gate-controller", app=self.app).listen(self.__listener)

    # ------------------------------------------------------------------ #

    def __remove_old_commands(self):
        print("Removing old commands")
        keys = list(db.reference("gate-controller", app=self.app).get().keys())
        for key in keys:
            if key == "placeholder":
                continue

            print(f"Removing: {key}")
            db.reference("gate-controller", app=self.app).child(key).delete()

    # ------------------------------------------------------------------ #

    def __listener(self, event: db.Event):
        if not event.data:
            return

        # Skip initial event
        if event.path == "/":
            return

        print("new event")
        print(event.path)
        print(event.event_type)
        print(event.data)

        if "placeholder" == event.data["type"]:
            print(f"{event.path} is placeholder")
            return

        request = GateRequest(
            type=event.data["type"],
            user=User(
                email=event.data["email"],
                name=event.data["name"],
                photo=event.data["photo"],
            ),
        )

        # If multiple commands arrive execute only once
        # Execute only one command
        if not self.is_running_command:
            t = Thread(target=self.__execute_command, args=(request,))
            t.daemon = True
            t.start()

        # Delte command
        db.reference(f"gate-controller{event.path}", app=self.app).delete()

    # ------------------------------------------------------------------ #

    def __execute_command(self, request: GateRequest):
        self.is_running_command = True
        print("Execute command")
        self.on_command(request)
        self.is_running_command = False