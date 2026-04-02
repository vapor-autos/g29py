import threading

from g29py import G29
from g29py.params import (
    BUTTON_MISC,
    BUTTON_MISC2,
    BUTTON_PLUS,
    BUTTON_PLUS_NIL,
    GAME_PAD,
    GAME_PAD_NIL,
    GAME_PAD_X,
    MISC2_TRACK_LEFT,
    MISC2_TRACK_RIGHT,
    PEDAL_ACCELERATOR,
    PEDAL_BRAKE,
    PEDAL_CLUTCH,
    STEERING_COARSE,
    STEERING_FINE,
)


def make_test_g29():
    g29 = G29.__new__(G29)
    g29.connected = True
    g29.state_lock = threading.Lock()
    g29.events = []
    g29.state = {
        "steering": 0.0,
        "accelerator": -1.0,
        "clutch": -1.0,
        "brake": -1.0,
        "buttons": {
            "right_paddle": 0,
            "left_paddle": 0,
            "up": 0,
            "down": 0,
            "left": 0,
            "right": 0,
            "X": 0,
            "O": 0,
            "S": 0,
            "T": 0,
            "R2": 0,
            "R3": 0,
            "L2": 0,
            "L3": 0,
            "Share": 0,
            "Options": 0,
            "+": 0,
            "-": 0,
            "PS": 0,
            "back": 0,
        },
    }
    return g29


def make_packet():
    packet = bytearray(12)
    packet[GAME_PAD] = GAME_PAD_NIL
    packet[BUTTON_MISC] = 0
    packet[BUTTON_PLUS] = BUTTON_PLUS_NIL
    packet[BUTTON_MISC2] = 0
    packet[STEERING_COARSE] = 0x80
    packet[STEERING_FINE] = 0x00
    packet[PEDAL_ACCELERATOR] = 0xFF
    packet[PEDAL_BRAKE] = 0xFF
    packet[PEDAL_CLUTCH] = 0xFF
    return packet


def test_get_events_clears_on_read():
    g29 = make_test_g29()
    g29.events = [{"type": "button_down", "control": "X"}]

    first = g29.get_events()
    second = g29.get_events()

    assert first == [{"type": "button_down", "control": "X"}]
    assert second == []


def test_update_state_emits_button_down_event():
    g29 = make_test_g29()
    packet = make_packet()
    packet[GAME_PAD] = GAME_PAD_X

    g29.update_state(packet)

    assert g29.get_events() == [{"type": "button_down", "control": "X"}]


def test_update_state_emits_button_up_event():
    g29 = make_test_g29()

    press_packet = make_packet()
    press_packet[GAME_PAD] = GAME_PAD_X
    g29.update_state(press_packet)
    g29.get_events()

    release_packet = make_packet()
    g29.update_state(release_packet)

    assert g29.get_events() == [{"type": "button_up", "control": "X"}]


def test_update_state_emits_dial_right_event():
    g29 = make_test_g29()
    packet = make_packet()
    packet[BUTTON_MISC2] = MISC2_TRACK_RIGHT

    g29.update_state(packet)

    assert g29.get_events() == [{"type": "dial", "delta": 1}]


def test_update_state_emits_dial_left_event():
    g29 = make_test_g29()
    packet = make_packet()
    packet[BUTTON_MISC2] = MISC2_TRACK_LEFT

    g29.update_state(packet)

    assert g29.get_events() == [{"type": "dial", "delta": -1}]
