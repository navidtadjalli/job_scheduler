from enum import Enum


class TaskStatus(str, Enum):
    Scheduled = "scheduled"
    Done = "done"
    Failed = "failed"


class PastTaskPolicy(str, Enum):
    SKIP = "skip"
    FAIL = "fail"
    RUN = "run"
