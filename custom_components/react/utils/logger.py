import logging
from datetime import datetime

from custom_components.react.const import DATETIME_FORMAT_READABLE, PACKAGE_NAME


_loggers: dict[str, logging.Logger] = {
    PACKAGE_NAME: logging.getLogger(PACKAGE_NAME)
}


def get_react_logger(name: str = None) -> logging.Logger:
    full_name = f"{PACKAGE_NAME}"
    if name:
        full_name = f"{full_name}.{name}"
    if name not in _loggers:
        _loggers[full_name] = logging.getLogger(full_name)
    return _loggers[full_name]


def format_data(**kwargs):
    items = []
    for k,v in kwargs.items():
        if isinstance(v, datetime):
            v = v.strftime(DATETIME_FORMAT_READABLE)
        items.append(f"{k}='{v}'")
    joined_items = "|".join(items)
    return f"|{joined_items}|"
