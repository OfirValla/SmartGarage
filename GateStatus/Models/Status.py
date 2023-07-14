from dataclasses import dataclass

@dataclass
class Status:
    current_status: str
    confidence_score: int
    timestamp: float
