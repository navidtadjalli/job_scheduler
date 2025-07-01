from enum import Enum


class Phase(str, Enum):
    Local = "local"
    Production = "production"


class TaskStatus(str, Enum):
    Scheduled = "scheduled"
    Done = "done"
    Failed = "failed"


class PastTaskPolicy(str, Enum):
    SKIP = "skip"
    FAIL = "fail"
    RUN = "run"
