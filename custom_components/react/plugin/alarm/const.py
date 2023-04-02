from enum import Enum


ALARM_GENERIC_PROVIDER = "generic"

class ArmMode(str, Enum):
    HOME = "home"
    AWAY = "away"
    NIGHT = "night"
    VACATION = "vacation"