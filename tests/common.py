from __future__ import annotations

import os

FIXTURE_WORKFLOW_NAME = "workflow_name"
FIXTURE_CONFIG_VALUE = "config_value"
FIXTURE_EVENT_VALUE = "event_value"
VALUE_FIXTURES = f"{FIXTURE_CONFIG_VALUE},{FIXTURE_EVENT_VALUE}"
VALUE_FIXTURE_COMBOS = [(True, False), (False, True)]
VALUE_FIXTURE_COMBOS_EXTENDED = [(True, False), (False, True), (False, False)]
EVENT_TEST_CALLBACK = "test_callback"

ALARM_CONFIG = "alarm_control_panel.yaml"
BINARY_SENSOR_CONFIG = "binary_sensor.yaml"
DEVICE_TRACKER_CONFIG = "device_tracker.yaml"
FAN_CONFIG = "fan.yaml"
GROUP_CONFIG = "group.yaml"
INPUT_BOOLEAN_CONFIG = "input_boolean.yaml"
INPUT_BUTTON_CONFIG = "input_button.yaml"
INPUT_NUMBER_CONFIG = "input_number.yaml"
INPUT_TEXT_CONFIG = "input_text.yaml"
LIGHT_CONFIG = "light.yaml"
MEDIA_PLAYER_CONFIG = "media_player.yaml"
PERSON_CONFIG = "person.yaml"
REACT_CONFIG = "react.yaml"
SENSOR_CONFIG = "sensor.yaml"
SWITCH_CONFIG = "switch.yaml"
TEMPLATE_CONFIG = "template.yaml"

TEST_CONTEXT = "test_context"
TEST_FLAG_VERIFY_CONFIG = "test_flag_verify_config"

def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), "_config", *add_path)
