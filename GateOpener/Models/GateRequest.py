from dataclasses import dataclass

from Models.User import User

@dataclass
class GateRequest:
    type: str
    user: User
    data: dict

    

