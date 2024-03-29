from homeassistant.components.notify.const import ATTR_TITLE

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, 
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
)


TEST_NOTIFY_EVENT_MESSAGE = "Approve something"
TEST_NOTIFY_TITLE1 = "Approve"
TEST_NOTIFY_FEEDBACK1 = "approve"
TEST_NOTIFY_ACKNOWLEDGEMENT1 = "approved"
TEST_NOTIFY_TITLE2 = "Deny"
TEST_NOTIFY_FEEDBACK2 = "deny"
TEST_NOTIFY_ACKNOWLEDGEMENT2 = "denied"
    
TEST_NOTIFY_SEND_MESSAGE_DATA_IN = {
    ATTR_EVENT_MESSAGE: TEST_NOTIFY_EVENT_MESSAGE,
    ATTR_EVENT_FEEDBACK_ITEMS: [{
        ATTR_TITLE: TEST_NOTIFY_TITLE1,
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: TEST_NOTIFY_FEEDBACK1,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: TEST_NOTIFY_ACKNOWLEDGEMENT1
    },{
        ATTR_TITLE: TEST_NOTIFY_TITLE2,
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: TEST_NOTIFY_FEEDBACK2,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: TEST_NOTIFY_ACKNOWLEDGEMENT2
    }]
}
TEST_NOTIFY_SEND_MESSAGE_DATA_OUT_FEEDBACK_ITEMS_STRING = f"{TEST_NOTIFY_TITLE1}|{TEST_NOTIFY_FEEDBACK1}|{TEST_NOTIFY_ACKNOWLEDGEMENT1},{TEST_NOTIFY_TITLE2}|{TEST_NOTIFY_FEEDBACK2}|{TEST_NOTIFY_ACKNOWLEDGEMENT2}"