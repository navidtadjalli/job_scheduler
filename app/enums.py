from enum import Enum


class TaskStatus(str, Enum):
    Scheduled = "scheduled"
    Done = "done"
    Failed = "failed"
