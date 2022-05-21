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
