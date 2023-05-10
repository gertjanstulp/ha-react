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
        
    # clockformat = "%H:%M:%S"
    # clockvalue: datetime = None
    # try:
    #     clockvalue = datetime.strptime(time_string, clockformat)
    #     time_key = clockvalue.strftime("%H:%M:%S")
    #     time_data = TimeData(clockvalue.hour, clockvalue.minute, clockvalue.second)
    # except ValueError:
    #     # Do not catch exception here, should be propagated to caller
    #     value,type = parse_time_pattern(time_string)
    #     time_key = f"{value}{type}"
    #     hours = f"/{value}" if type == "h" else None
    #     minutes = f"/{value}" if type == "m" else None
    #     seconds = f"/{value}" if type == "s" else None
    #     # If larger units are specified, default the smaller units to zero
    #     if minutes is None and hours is not None:
    #         minutes = 0
    #     if seconds is None and minutes is not None:
    #         seconds = 0
    #     time_data = TimeData(hours, minutes, seconds)
    
    # return time_string, TimeData(hours, minutes, seconds)


# def parse_time_pattern(value: str) -> tuple[int, str]:
#     hour_pattern = "^(2[0-3]|[01]?[0-9])(h)$"
#     minute_pattern = "^([0-5]?[0-9])(m)$"
#     second_pattern = "^([0-5]?[0-9])(s)$"
#     result = -1
#     type: str = None

#     match = re.match(hour_pattern, value)
#     if not match:
#         match = re.match(minute_pattern, value)
#         if not match:
#             match = re.match(second_pattern, value)

#     if not match:
#         raise ValueError()

#     return (int(match.group(1)), match.group(2))


class TimeData():
    def __init__(self, hour: str = None, minute: str = None, second: str = None) -> None:
        self.hour = hour
        self.minute = minute
        self.second = second
