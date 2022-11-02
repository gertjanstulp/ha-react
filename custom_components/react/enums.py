from enum import Enum


class ReactStage(str, Enum):
    SETUP = "setup"
    STARTUP = "startup"
    WAITING = "waiting"
    RUNNING = "running"
    BACKGROUND = "background"


class ReactDisabledReason(str, Enum):
    REMOVED = "removed"
    LOAD_REACT = "load_react"
    RESTORE = "restore"
    CONSTRAINTS = "constraints"
        

class StepResult(Enum):
    NONE = 0,
    YIELD_STATE = 1,
    YIELD_DELAY = 2,
    YIELD_SCHEDULE = 3,
    SUCCESS = 4,
    FAIL = 5,
    STOP = 6,

YIELD_RESULTS = [ StepResult.YIELD_STATE, StepResult.YIELD_DELAY, StepResult.YIELD_SCHEDULE ]
