from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TaskStatistics:
    """Class to represent task statistics for model training."""
    
    total_tasks: int
    labeled_tasks: int
    valid_tasks: int
    export_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Set export date if not provided."""
        if self.export_date is None:
            self.export_date = datetime.now()
    
    @property
    def training_utilization_percent(self) -> float:
        """Calculate training utilization percentage."""
        if self.total_tasks == 0:
            return 0.0
        return round((self.valid_tasks / self.total_tasks) * 100, 1)
    
    @property
    def labeled_percentage(self) -> float:
        """Calculate percentage of tasks that are labeled."""
        if self.total_tasks == 0:
            return 0.0
        return round((self.labeled_tasks / self.total_tasks) * 100, 1)
    
    @property
    def valid_percentage(self) -> float:
        """Calculate percentage of labeled tasks that are valid for training."""
        if self.labeled_tasks == 0:
            return 0.0
        return round((self.valid_tasks / self.labeled_tasks) * 100, 1)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        # Ensure export_date is set
        if self.export_date is None:
            self.export_date = datetime.now()
            
        return {
            "total_tasks": self.total_tasks,
            "labeled_tasks": self.labeled_tasks,
            "valid_tasks": self.valid_tasks,
            "training_utilization_percent": self.training_utilization_percent,
            "labeled_percentage": self.labeled_percentage,
            "valid_percentage": self.valid_percentage,
            "export_date": self.export_date.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of task statistics."""
        return (f"TaskStatistics(total_tasks={self.total_tasks}, "
                f"labeled_tasks={self.labeled_tasks}, "
                f"valid_tasks={self.valid_tasks}, "
                f"utilization={self.training_utilization_percent}%)") 