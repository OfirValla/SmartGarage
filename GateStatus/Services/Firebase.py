from colorama import Fore, Style
from firebase_admin import credentials
from firebase_admin import db

from Models.Status import Status

import firebase_admin
import dataclasses
import os

# ------------------------------------------------------------------ #


class Firebase:
    def __init__(self):
        access_key_path = os.getenv('ACCESS_KEY_PATH')

        json_path = os.path.join(access_key_path, "valla-projects-gate-controller.json")
        project_id = "valla-projects"
        options = {"databaseURL": "https://valla-projects-default-rtdb.firebaseio.com"}

        print(f"Connecting to {Fore.LIGHTGREEN_EX}Firebase{Style.RESET_ALL}")

        self.cred = credentials.Certificate(json_path)
        self.app = firebase_admin.initialize_app(
            credential=self.cred, options=options, name=project_id
        )

        print(f" * {Fore.LIGHTGREEN_EX}Connected{Style.RESET_ALL}")
        
    # ------------------------------------------------------------------ #
    
    def update_status(self, new_status: Status) -> None:
        db.reference(f"gate-controller/status", app=self.app).set(dataclasses.asdict(new_status))

# ------------------------------------------------------------------ #