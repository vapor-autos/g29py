from g29py import G29
from g29py.params import (
    BUTTON_MISC,
    BUTTON_MISC2,
    BUTTON_PLUS,
    BUTTON_PLUS_NIL,
    BUTTON_PLUS_ON,
    GAME_PAD,
    GAME_PAD_NIL,
    GAME_PAD_UP,
    MISC2_BACK,
    MISC_OPTIONS,
    PEDAL_ACCELERATOR,
    PEDAL_BRAKE,
    PEDAL_CLUTCH,
    STEERING_COARSE,
    STEERING_FINE,
)


class FakeDevice:
    def __init__(self):
        self.open_args = None

    def open(self, vendor_id, product_id):
        self.open_args = (vendor_id, product_id)

    def get_manufacturer_string(self):
        return "Logitech"

    def get_product_string(self):
        return "G29"


def make_test_g29():
    return G29.__new__(G29)


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


def test_decode_packet_defaults():
    g29 = make_test_g29()
    packet = make_packet()

    state = g29.decode_packet(packet)

    assert state["buttons"]["up"] == 0
    assert state["buttons"]["Options"] == 0
    assert state["buttons"]["+"] == 0
    assert state["buttons"]["PS"] == 0
    assert state["buttons"]["back"] == 0


def test_decode_packet_maps_known_button_values():
    g29 = make_test_g29()
    packet = make_packet()
    packet[GAME_PAD] = GAME_PAD_UP
    packet[BUTTON_MISC] = MISC_OPTIONS
    packet[BUTTON_PLUS] = BUTTON_PLUS_ON
    packet[BUTTON_MISC2] = MISC2_BACK

    state = g29.decode_packet(packet)

    assert state["buttons"]["up"] == 1
    assert state["buttons"]["Options"] == 1
    assert state["buttons"]["+"] == 1
    assert state["buttons"]["back"] == 1


def test_init_opens_hidapi_device(monkeypatch):
    fake_device = FakeDevice()

    monkeypatch.setattr("g29py.g29.hid.device", lambda: fake_device)

    g29 = G29()

    assert fake_device.open_args == (0x046D, 0xC24F)
    assert g29.device is fake_device
    assert g29.connected is True
