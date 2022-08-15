from __future__ import annotations

import os

DOMAIN_SENSOR = "sensor"
FIXTURE_WORKFLOW_NAME = "workflow_name"
EVENT_TEST_CALLBACK = "test_callback"

REACT_CONFIG = "react.yaml"
TEMPLATE_CONFIG = "template.yaml"
INPUT_BOOLEAN_CONFIG = "input_boolean.yaml"
INPUT_TEXT_CONFIG = "input_text.yaml"
GROUP_CONFIG = "group.yaml"
PERSON_CONFIG = "person.yaml"


def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), "testing_config", *add_path)
