from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict


@dataclass
class TaskStatistics:
    """Class to represent task statistics for model training."""
    
    total_tasks: int
    gate_status_counts: Optional[Dict[str, int]] = field(default_factory=dict)
    parking_status_counts: Optional[Dict[str, int]] = field(default_factory=dict)
    export_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Set export date if not provided."""
        if self.export_date is None:
            self.export_date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        # Ensure export_date is set
        if self.export_date is None:
            self.export_date = datetime.now()
            
        return {
            "total_tasks": self.total_tasks,
            "gate_status_counts": self.gate_status_counts,
            "parking_status_counts": self.parking_status_counts,
            "export_date": self.export_date.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of task statistics."""
        return (f"TaskStatistics(total_tasks={self.total_tasks}, "
                f"gate_status_counts={self.gate_status_counts}, "
                f"parking_status_counts={self.parking_status_counts})") 