from __future__ import annotations

from custom_components.react.exceptions import ReactException


def parse_time_data(time_string: str) -> TimeData:
    time_string_parts = time_string.split(":")
    if len(time_string_parts) != 3:
        raise ReactException("Time action should be formatted as '<hour_value>:<minute_value>:<second_value>'")
    
    hours = time_string_parts[0] or None
    minutes = time_string_parts[1] or None
    seconds = time_string_parts[2] or None

    check_value(hours, 0, 23, "Hours")
    check_value(minutes, 0, 59, "Minutes")
    check_value(seconds, 0, 59, "Seconds")

    return TimeData(hours, minutes, seconds)


def check_value(value: str, min: int, max: int, name: str):
    if not any([
        value in ["*", None],
        check_numeric(value, min, max, name),
        check_pattern(value, min, max, name),
    ]):
        raise ReactException(f"Invalid value for {name.lower()}")
        
    
def check_numeric(value: str, min: int, max: int, name: str) -> bool:
    if value and value.isnumeric():
        value_number = int(value)
        if value_number < min or value_number > max:
            raise ReactException(f"{name} value should be between {min} and {max}")
        return True
    return False
        

def check_pattern(value: str, min: int, max: int, name: str) -> bool:
    if value and value.startswith("/"):
        value_string = value[1:]
        if not value_string.isnumeric():
            raise ReactException(f"{name} pattern should start with '/' and end with a number")
        value_number = int(value_string)
        if value_number < min or value_number > max:
            raise ReactException(f"{name} pattern should be between {min} and {max}")
        return True
    return False


class TimeData():
    def __init__(self, hour: str = None, minute: str = None, second: str = None) -> None:
        self.hour = hour
        self.minute = minute
        self.second = second
