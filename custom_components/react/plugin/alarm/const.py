from enum import Enum


ALARM_GENERIC_PROVIDER = "generic"

ATTR_ALARM_PROVIDER = "alarm_provider"

class ArmMode(str, Enum):
    HOME = "home"
    AWAY = "away"
    NIGHT = "night"
    VACATION = "vacation"