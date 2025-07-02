from enum import Enum


class Phase(str, Enum):
    Local = "local"
    Production = "production"


class ResultStatus(str, Enum):
    Done = "Done"
    Failed = "Failed"
