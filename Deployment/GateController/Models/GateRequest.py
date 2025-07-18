from dataclasses import dataclass, field

from Models.User import User

@dataclass
class GateRequest:
    type: str
    user: User
    data: dict = field(default_factory=dict)
