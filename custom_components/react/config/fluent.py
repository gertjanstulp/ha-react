import re
from typing import Any
import voluptuous as vol

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_CONDITION,
    ATTR_DATA, 
    ATTR_DELAY, 
    ATTR_ENTITY,
    ATTR_ENTITY_GROUP, 
    ATTR_FORWARD_ACTION, 
    ATTR_FORWARD_DATA,
    ATTR_OVERWRITE,
    ATTR_RESET_WORKFLOW,
    ATTR_RESTART_MODE, 
    ATTR_SCHEDULE, 
    ATTR_SCHEDULE_AT, 
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_STATE, 
    ATTR_TYPE, 
    ATTR_WAIT,
    ATTR_WAIT_CONDITION,
)

FLUENT_GROUP_ENTITY = "entity"
FLUENT_GROUP_TYPE = "type"
FLUENT_GROUP_ACTION = "action"
FLUENT_GROUP_RESET_WORKFLOW = "reset_workflow"
FLUENT_GROUP_WAIT_DELAY_NUMBER = "wait_delay_number"
FLUENT_GROUP_WAIT_DELAY_UNIT = "wait_delay_unit"
FLUENT_GROUP_WAIT_SCHEDULE = "wait_schedule"
FLUENT_GROUP_WAIT_SCHEDULE_DAYS = "wait_schedule_days"
FLUENT_GROUP_OPTION_OVERWRITE = "option_overwrite"
FLUENT_GROUP_OPTION_FORWARD_ACTION = "option_forward_action"
FLUENT_GROUP_OPTION_FORWARD_DATA = "option_forward_data"
FLUENT_GROUP_OPTION_RESTART_MODE = "option_restart_mode"
FLUENT_GROUP_CTOR_CONDITION = "ctor_condition"
FLUENT_GROUP_WAIT_CONDITION = "wait_condition"
FLUENT_GROUP_DATA = "data"

FLUENT_BLOCK_WAIT_SCHEDULE_WEEKDAYS = "mon|tue|wed|thu|fri|sat|sun"
FLUENT_BLOCK_JINJA = "{{.+?(?=}})}}"
FLUENT_BLOCK_OPTION_OVERWRITE = "overwrite"
FLUENT_BLOCK_OPTION_FORWARD_ACTION = "forward_action"
FLUENT_BLOCK_OPTION_FORWARD_DATA = "forward_data"
FLUENT_BLOCK_OPTION_RESTART_MODE_MODES = "abort|force|rerun"
FLUENT_BLOCK_WAIT_DELAY_UNIT = "seconds|minutes|hours"
FLUENT_BLOCK_WORD_NO_DOT = "[\w\d\-\+\:\/]+"
FLUENT_BLOCK_WORD = "[\w\d\-\+\:\/\.\!]+"
FLUENT_BLOCK_NUMBER = "[\d]+"
FLUENT_BLOCK_TIME = "[\d\:]+"
FLUENT_BLOCK_LIST_END = "(?!,\w)"
FLUENT_BLOCK_DATA = r'[^,]+?\=(?:{{.+?}}|".+?"|[^,]+)'
FLUENT_BLOCK_WILDCARD = "\*"

FLUENT_PARSE_DATA = r'(?P<key>[^,]+?)\=(?P<value>{{.+?}}|".+?"|[^,]+)'

FLUENT_TOKEN_RESET = "reset"
FLUENT_TOKEN_USE = "use"
FLUENT_TOKEN_IF = "if"
FLUENT_TOKEN_WAIT_CONDITION = "wait until"
FLUENT_TOKEN_WAIT_DELAY = "wait for"
FLUENT_TOKEN_WAIT_SCHEDULE = "wait until"
FLUENT_TOKEN_EVERY = "every"
FLUENT_TOKEN_DATA = "with"
FLUENT_TOKEN_USE_RESTART_MODE = f"{FLUENT_TOKEN_USE} restart_mode"


def optional(value: str):
    return f"(?:[ ]+{value})?"


def named_group(name: str, expression: str):
    return f"(?P<{name}>{expression})"


def unnamed_group(value: str):
    return f"(?:{value})"


def enum_list(items: str):
    return unspaced(
        unnamed_group(items), 
        zero_or_many(
            unnamed_group(
                prepend_comma(unnamed_group(items))
            )
        ), 
        FLUENT_BLOCK_LIST_END
    )


def zero_or_many(value: str) -> str:
    return f"{value}*"


def prepend_comma(value: str) -> str:
    return f",\s*{value}"


def tokenize(token: str, value: str):
    return spaced(token, value)


def spaced(*args):
    return ' '.join(args)


def dotted(*args):
    return '\.'.join(args)


def piped(*args):
    return '|'.join(args)


def unspaced(*args):
    return ''.join(args)


def or_group(value1: str, value2: str):
    return unnamed_group(piped(value1, value2))


FLUENT_SYNTAX_GENERIC_BASE = spaced(
    dotted(
        named_group(
            FLUENT_GROUP_TYPE, 
            or_group(
                FLUENT_BLOCK_WORD_NO_DOT,
                FLUENT_BLOCK_JINJA,
            )
        ), 
        named_group(
            FLUENT_GROUP_ENTITY, 
            enum_list(
                or_group(
                    FLUENT_BLOCK_WORD,
                    FLUENT_BLOCK_JINJA,
                )
            )
        )
    ), 
    named_group(
        FLUENT_GROUP_ACTION,
        or_group(
            FLUENT_BLOCK_WILDCARD,
            enum_list(
                or_group(
                    FLUENT_BLOCK_WORD,
                    FLUENT_BLOCK_JINJA,
                )
            )
        )
    )
)

FLUENT_SYNTAX_RESET_BASE = tokenize(
    FLUENT_TOKEN_RESET, 
    named_group(
        FLUENT_GROUP_RESET_WORKFLOW,
        or_group(
            FLUENT_BLOCK_WORD,
            FLUENT_BLOCK_JINJA,
        )
    )
)

FLUENT_SYNTAX_WAIT_DELAY = optional(
    tokenize(
        FLUENT_TOKEN_WAIT_DELAY, 
        spaced(
            named_group(
                FLUENT_GROUP_WAIT_DELAY_NUMBER, 
                or_group(
                    FLUENT_BLOCK_NUMBER,
                    FLUENT_BLOCK_JINJA
                )
            ), 
            named_group(
                FLUENT_GROUP_WAIT_DELAY_UNIT, 
                FLUENT_BLOCK_WAIT_DELAY_UNIT
            )
        )
    )
)

FLUENT_SYNTAX_WAIT_SCHEDULE = optional(
    tokenize(
        FLUENT_TOKEN_WAIT_SCHEDULE, 
        unspaced(
            named_group(
                FLUENT_GROUP_WAIT_SCHEDULE, 
                FLUENT_BLOCK_TIME
            ),
            optional(
                tokenize(
                    FLUENT_TOKEN_EVERY, 
                    named_group(
                        FLUENT_GROUP_WAIT_SCHEDULE_DAYS, 
                        enum_list(
                            FLUENT_BLOCK_WAIT_SCHEDULE_WEEKDAYS
                        )
                    )
                )
            ),
            optional(
                tokenize(
                    FLUENT_TOKEN_USE_RESTART_MODE,
                    named_group(
                        FLUENT_GROUP_OPTION_RESTART_MODE,
                        enum_list(
                            FLUENT_BLOCK_OPTION_RESTART_MODE_MODES
                        ),
                    )
                )
            )
        )
    )
)

FLUENT_SYNTAX_WAIT_CONDITION = optional(
    tokenize(
        FLUENT_TOKEN_WAIT_CONDITION, 
        named_group(
            FLUENT_GROUP_WAIT_CONDITION, 
            FLUENT_BLOCK_JINJA
        )
    )
)

FLUENT_SYNTAX_OVERWRITE = optional(
    tokenize(
        FLUENT_TOKEN_USE, 
        named_group(
            FLUENT_GROUP_OPTION_OVERWRITE, 
            FLUENT_BLOCK_OPTION_OVERWRITE
        )
    )
)

FLUENT_SYNTAX_FORWARD_ACTION = optional(
    tokenize(
        FLUENT_TOKEN_USE, 
        named_group(
            FLUENT_GROUP_OPTION_FORWARD_ACTION, 
            FLUENT_BLOCK_OPTION_FORWARD_ACTION
        )
    )
)

FLUENT_SYNTAX_FORWARD_DATA = optional(
    tokenize(
        FLUENT_TOKEN_USE, 
        named_group(
            FLUENT_GROUP_OPTION_FORWARD_DATA, 
            FLUENT_BLOCK_OPTION_FORWARD_DATA
        )
    )
)

FLUENT_SYNTAX_CTOR_CONDITION = optional(
    tokenize(
        FLUENT_TOKEN_IF, 
        named_group(
            FLUENT_GROUP_CTOR_CONDITION, 
            FLUENT_BLOCK_JINJA
        )
    )
)

FLUENT_SYNTAX_DATA = optional(
    tokenize(
        FLUENT_TOKEN_DATA,
        named_group(
            FLUENT_GROUP_DATA,
            enum_list(
                FLUENT_BLOCK_DATA
            )
        )
    )
)


FLUENT_SYNTAX_OPTIONALS = unspaced(
    FLUENT_SYNTAX_OVERWRITE,
    FLUENT_SYNTAX_FORWARD_ACTION,
    FLUENT_SYNTAX_FORWARD_DATA,
    FLUENT_SYNTAX_CTOR_CONDITION,
    FLUENT_SYNTAX_WAIT_CONDITION,
    FLUENT_SYNTAX_WAIT_DELAY,
    FLUENT_SYNTAX_WAIT_SCHEDULE,
    FLUENT_SYNTAX_DATA,
)


FLUENT_SYNTAX_GENERIC = unspaced(
    FLUENT_SYNTAX_GENERIC_BASE,
    FLUENT_SYNTAX_OPTIONALS,
)


FLUENT_SYNTAX_RESET = unspaced(
    FLUENT_SYNTAX_RESET_BASE,
    FLUENT_SYNTAX_OPTIONALS,
)


def ensure_entity_data(value: list[Any] | None):
    if isinstance(value, list):
        for i,item in enumerate(value):
            if isinstance(item, str):
                match, result = find_match(item)

                if wait := parse_wait(match):
                    result[ATTR_WAIT] = wait

                if condition := match.group(FLUENT_GROUP_CTOR_CONDITION):
                    result[ATTR_CONDITION] = condition.strip()

                if data := match.group(FLUENT_GROUP_DATA):
                    result[ATTR_DATA] = parse_data(data)
                    
                if match.group(FLUENT_GROUP_OPTION_OVERWRITE):
                    result[ATTR_OVERWRITE] = True
                if match.group(FLUENT_GROUP_OPTION_FORWARD_ACTION):
                    result[ATTR_FORWARD_ACTION] = True
                if match.group(FLUENT_GROUP_OPTION_FORWARD_DATA):
                    result[ATTR_FORWARD_DATA] = True

                value[i] = result
                continue

    return value


def find_match(value: str) -> tuple[re.Match, dict]:
    if match := re.match(FLUENT_SYNTAX_GENERIC, value):
        result = {}
        entity_items = parse_match_group(match, FLUENT_GROUP_ENTITY)
        type = parse_match_group(match, FLUENT_GROUP_TYPE)
        action = parse_match_group(match, FLUENT_GROUP_ACTION)

        for entity_item in entity_items:
            result.setdefault(ATTR_ENTITY_GROUP if entity_item.endswith('!') else ATTR_ENTITY, []).append(entity_item.replace('!', ''))
        if type:
            result[ATTR_TYPE] = type
        if action:
            result[ATTR_ACTION] = action

    elif match := re.match(FLUENT_SYNTAX_RESET, value):
        result = {
            ATTR_RESET_WORKFLOW: match.group(FLUENT_GROUP_RESET_WORKFLOW)
        }

    else:
        raise vol.Invalid("Invalid fluent syntax used")
    
    return match, result
    

def parse_match_group(match: re.Match, name: str):
    result = None
    value = match.group(name)
    if value:
        if value != '*':
            result = value.split(',')
    return result


def parse_wait(match: re.Match):
    wait: dict = None

    # Delay
    if delay_number := match.group(FLUENT_GROUP_WAIT_DELAY_NUMBER):
        if not wait: wait = {}
        if delay_number.isnumeric():
            delay_number = int(delay_number)
        wait[ATTR_DELAY] = {
            match.group(FLUENT_GROUP_WAIT_DELAY_UNIT): delay_number
        }
    
    # Schedule
    if time := match.group(FLUENT_GROUP_WAIT_SCHEDULE):
        if not wait: wait = {}
        schedule = {
            ATTR_SCHEDULE_AT: time
        }
        if weekdays := match.group(FLUENT_GROUP_WAIT_SCHEDULE_DAYS):
            schedule[ATTR_SCHEDULE_WEEKDAYS] = weekdays.split(',')
        if restart_mode := match.group(FLUENT_GROUP_OPTION_RESTART_MODE):
            schedule[ATTR_RESTART_MODE] = restart_mode
        wait[ATTR_SCHEDULE] = schedule

    # condition
    if condition := match.group(FLUENT_GROUP_WAIT_CONDITION):
        if not wait: wait = {}
        wait[ATTR_STATE] = {
            ATTR_WAIT_CONDITION : condition
        }
    return wait


def parse_data(data: str):
    result = {}
    for match in re.finditer(FLUENT_PARSE_DATA, data):
        result[match.group('key').strip()] = parse_numeric(match.group('value').strip().strip('"'))
    return result


def parse_numeric(value: str) -> int | float | str:
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass

    return value
