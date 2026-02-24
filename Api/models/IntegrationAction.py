from enum import Enum

class IntegrationAction(str, Enum):
    TOGGLE_LIGHT = "toggle_light"
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    CALL_SERVICE = "call_service"