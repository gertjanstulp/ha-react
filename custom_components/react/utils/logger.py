"""Custom logger for React."""
from datetime import datetime
import logging

from ..const import (
    PACKAGE_NAME,
)

_ReactLogger: logging.Logger = logging.getLogger(PACKAGE_NAME)


def get_react_logger() -> logging.Logger:
    """Return a Logger instance."""
    return _ReactLogger


def format_data(**kwargs):
    items = []
    for k,v in kwargs.items():
        if isinstance(v, datetime):
            v = v.strftime("%Y/%m/%d, %H:%M:%S")
        items.append(f"{k}='{v}'")
    joined_items = "|".join(items)
    return f"|{joined_items}|"
