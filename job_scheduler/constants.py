from enum import Enum


class Phase(str, Enum):
    Local = "local"
    Production = "production"


class TaskStatus(str, Enum):
    Scheduled = "Scheduled"
    Done = "Done"
    Failed = "Failed"


class PastTaskPolicy(str, Enum):
    SKIP = "skip"
    FAIL = "fail"
    RUN = "run"
