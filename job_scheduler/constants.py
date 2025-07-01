from enum import Enum


class Phase(str, Enum):
    Local = "local"
    Production = "production"


class TaskStatus(str, Enum):
    Scheduled = "Scheduled"
    Finished = "Finished"
    Failed = "Failed"


class ResultStatus(str, Enum):
    Done = "Done"
    Failed = "Failed"


class PastTaskPolicy(str, Enum):
    SKIP = "skip"
    FAIL = "fail"
    RUN = "run"
