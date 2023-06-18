from pickle import FALSE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from threading import Thread

from Models.GateRequest import GateRequest

class FirebaseListener:
    def __init__(self, on_command):
        json_path = 'valla-projects-firebase-adminsdk-3ogbz-2ec52a9c7b.json'
        project_id = 'valla-projects'
        options = { 'databaseURL': 'https://valla-projects-default-rtdb.firebaseio.com' }

        print("Connecting to firebase")

        self.cred = credentials.Certificate(json_path)        
        self.app = firebase_admin.initialize_app(credential= self.cred, options= options, name= project_id)
        self.on_command = on_command
        self.is_running_command = False

        print("Connected")

        print("Start listening to events")
        db.reference('gate-controller', app= self.app).listen(self.__listener)

    # ------------------------------------------------------------------ #

    def __listener(self, event):
        if not event.data:
            return

        print("new event")
        print (event.data)
        commands = list(event.data.keys())
        
        if "placeholder" in commands:
            return
        
        request = GateRequest(
            type= event.data[commands[0]]['type']   
        )

        # If multiple commands arrive execute only once
        # Execute only one command
        if not self.is_running_command:
            t = Thread(target=self.__execute_command, args= (request, ))
            t.daemon = True
            t.start()


        # Delete all existing commands
        for key in commands:
            # Skip placeholder key that keeps the gate-controller reference visible in ui
            if key is "placeholder":
                continue

            db.reference('gate-controller', app= self.app).child(key).delete()
   
    # ------------------------------------------------------------------ #

    def __execute_command(self, request: GateRequest):
        self.is_running_command = True
        print("Execute command")
        self.on_command(request)
        self.is_running_command = False