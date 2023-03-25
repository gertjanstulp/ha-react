from enum import Enum


PLUGIN_NAME = "alarm"

class ArmMode(str, Enum):
    HOME = "home"
    AWAY = "away"
    NIGHT = "night"
    VACATION = "vacation"