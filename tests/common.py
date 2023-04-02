from __future__ import annotations

import os

DOMAIN_SENSOR = "sensor"
FIXTURE_WORKFLOW_NAME = "workflow_name"
EVENT_TEST_CALLBACK = "test_callback"

ALARM_CONFIG = "alarm.yaml"
BINARY_SENSOR_CONFIG = "binary_sensor.yaml"
DEVICE_TRACKER_CONFIG = "device_tracker.yaml"
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
