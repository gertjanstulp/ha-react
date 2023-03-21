from __future__ import annotations

import os

DOMAIN_SENSOR = "sensor"
FIXTURE_WORKFLOW_NAME = "workflow_name"
EVENT_TEST_CALLBACK = "test_callback"

REACT_CONFIG = "react.yaml"
TEMPLATE_CONFIG = "template.yaml"
INPUT_BOOLEAN_CONFIG = "input_boolean.yaml"
INPUT_BUTTON_CONFIG = "input_button.yaml"
INPUT_NUMBER_CONFIG = "input_number.yaml"
INPUT_TEXT_CONFIG = "input_text.yaml"
GROUP_CONFIG = "group.yaml"
PERSON_CONFIG = "person.yaml"
ALARM_CONFIG = "alarm.yaml"
LIGHT_CONFIG = "light.yaml"
SWITCH_CONFIG = "switch.yaml"
BINARY_SENSOR_CONFIG = "binary_sensor.yaml"
SENSOR_CONFIG = "sensor.yaml"
DEVICE_TRACKER_CONFIG = "device_tracker.yaml"

TEST_CONTEXT = "test_context"
TEST_FLAG_VERIFY_CONFIG = "test_flag_verify_config"

def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), "_config", *add_path)
