import hid
import time
import threading
import copy
import logging as log
from .params import *

EMPTY_STATE_TEMPLATE = {
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

class G29:
    def __init__(self):
        self.connected = False
        self.cache = None
        self.state_lock = threading.Lock()
        self.events = []
        self.state = copy.deepcopy(EMPTY_STATE_TEMPLATE)
        self.pump_thread = None
        try:
            device = hid.Device(VENDOR_ID, PRODUCT_ID)
        except Exception as exc:
            raise Exception("Device not found. Is it plugged in?") from exc
        log.debug("Device manufacturer: %s", device.manufacturer)
        log.debug("Product: %s", device.product)
        self.device = device
        self.connected = True

    def reset(self, wait_seconds=RESET_WAIT_SECONDS):
        """Run the wheel calibration/reset sequence."""
        self.device.write(bytes(RESET_STAGE_1))
        self.device.write(bytes(RESET_STAGE_2))
        time.sleep(wait_seconds)

    # WRITE

    def force_constant(self, val=0.0):
        """Sets the force constant of the wheel.

        Args:
            val (float, optional): Signed force from -1 to 1. Defaults to 0.

        Raises:
            ValueError: force_constant val must be between -1 and 1
        """
        if val < -1 or val > 1:
            raise ValueError("force_constant val must be between -1 and 1")
        # normalize signed force to 0-255 with neutral near the midpoint
        val = round((val + 1) * 127.5)
        log.debug("force_constant: %s", val)
        msg = [0x11, 0x00, val, 0x00, 0x00, 0x00, 0x00]
        self.device.write(bytes(msg))

    def set_friction(self, val=0.5):
        """Sets the friction of the wheel.

        Args:
            val (float, optional): Defaults to 0.5.

        Raises:
            ValueError: force_fricion val must be between 0 and 1
        """
        if val < 0 or val > 1:
            raise ValueError("force_fricion val must be between 0 and 1")
        # normalize to the verified working range 0-7
        val = round(int(val * 7))
        log.debug("force_friction: %s", val)
        msg = [0x21, 0x02, val, 0x00, val, 0x00, 0x00]
        self.device.write(bytes(msg))

    def set_range(self, val=400):
        """Sets the range of the wheel.

        Args:
            val (int, optional): Defaults to 400.

        Raises:
            ValueError: set_range val must be between 400 and 900
        """
        if val < 400 or val > 900:
            raise ValueError("set_range val must be between 400 and 900")
        range1 = val & 0x00ff
        range2 = (val & 0xff00) >> 8
        log.debug("range: %s,%s", range1, range2)
        msg = [0xf8, 0x81, range1, range2, 0x00, 0x00, 0x00]
        self.device.write(bytes(msg))

    def set_autocenter(self, ccw_proportion=0.5, cw_proportion=0.5, force=0.5):
        """Sets simple autocenter.

        Args:
            ccw_proportion (float, optional): 0..1. Anti-clockwise proportion.
            cw_proportion (float, optional): 0..1. Clockwise proportion.
            force (float, optional): 0..1. Main force.

        Raises:
            ValueError: ccw_proportion must be between 0 and 1
            ValueError: cw_proportion must be between 0 and 1
            ValueError: force must be between 0 and 1
        """
        if ccw_proportion < 0 or ccw_proportion > 1:
            raise ValueError("ccw_proportion must be between 0 and 1")
        if cw_proportion < 0 or cw_proportion > 1:
            raise ValueError("cw_proportion must be between 0 and 1")
        if force < 0 or force > 1:
            raise ValueError("force must be between 0 and 1")

        ccw_proportion = round(int(ccw_proportion * 7))
        cw_proportion = round(int(cw_proportion * 7))
        force = round(int(force * 255))

        up_msg = [0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.device.write(bytes(up_msg))

        log.debug(
            "autocenter: %s %s %s",
            ccw_proportion,
            cw_proportion,
            force,
        )
        msg = [0xfe, 0x0d, ccw_proportion, cw_proportion, force, 0x00, 0x00, 0x00]
        self.device.write(bytes(msg))

    def set_anticenter(
        self,
        slot=1,
        cw_position=0.5,
        ccw_position=0.5,
        cw_proportion=0.5,
        ccw_proportion=0.5,
        cw_reverse=False,
        ccw_reverse=False,
        force=0.5,
    ):
        """Sets complex auto/anti-center using per-direction fields.

        Args:
            slot (int, optional): effect slot 1..4.
            cw_position (float, optional): 0..1 clockwise position.
            ccw_position (float, optional): 0..1 anti-clockwise position.
            cw_proportion (float, optional): 0..1 clockwise proportion.
            ccw_proportion (float, optional): 0..1 anti-clockwise proportion.
            cw_reverse (bool, optional): Clockwise reverse flag.
            ccw_reverse (bool, optional): Anti-clockwise reverse flag.
            force (float, optional): 0..1 main force.

        Raises:
            ValueError: cw_position must be between 0 and 1
            ValueError: ccw_position must be between 0 and 1
            ValueError: cw_proportion must be between 0 and 1
            ValueError: ccw_proportion must be between 0 and 1
            ValueError: force must be between 0 and 1
        """
        if slot not in (1, 2, 3, 4):
            raise ValueError("slot must be between 1 and 4")
        if cw_position < 0 or cw_position > 1:
            raise ValueError("cw_position must be between 0 and 1")
        if ccw_position < 0 or ccw_position > 1:
            raise ValueError("ccw_position must be between 0 and 1")
        if cw_proportion < 0 or cw_proportion > 1:
            raise ValueError("cw_proportion must be between 0 and 1")
        if ccw_proportion < 0 or ccw_proportion > 1:
            raise ValueError("ccw_proportion must be between 0 and 1")
        if force < 0 or force > 1:
            raise ValueError("force must be between 0 and 1")

        cw_position = round(int(cw_position * 255))
        ccw_position = round(int(ccw_position * 255))
        cw_proportion = round(int(cw_proportion * 15))
        ccw_proportion = round(int(ccw_proportion * 15))
        cw_reverse = 0x1 if cw_reverse else 0x0
        ccw_reverse = 0x1 if ccw_reverse else 0x0
        force = round(int(force * 255))

        proportion_byte = (cw_proportion << 4) | ccw_proportion
        reverse_byte = (cw_reverse << 4) | ccw_reverse
        slot_command = (1 << (slot - 1)) << 4

        log.debug(
            "anticenter: %s %s %s %s %s %s %s %s",
            slot,
            cw_position,
            ccw_position,
            cw_proportion,
            ccw_proportion,
            cw_reverse,
            ccw_reverse,
            force,
        )
        msg = [slot_command | 0x01, 0x01, cw_position, ccw_position, proportion_byte, reverse_byte, force]
        self.device.write(bytes(msg))

    def autocenter_off(self):
        """Disable simple autocenter."""
        msg = [0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.device.write(bytes(msg))

    def force_off(self, slot=0xf3):
        """Disable active force effects.

        Args:
            slot (int, optional): Effect slot or off-mask. `0xf3` clears all.

        Raises:
            ValueError: slot must be between 0 and 4 or 0xf3.
        """
        if slot < 0 or slot > 4 and slot !=0xf3:
            raise ValueError("force_off slot must be between 0 and 4 or 0xf3")
        log.debug("force_off: %s", slot)
        msg = [slot, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.device.write(bytes(msg))

    # READ

    def read(self, timeout=10):
        try:
            dat = self.device.read(16, timeout)
        except Exception as e:
            log.warning("G29 read failed; stopping listener: %s", e)
            self.connected = False
            return

        # only handle 12 byte msgs
        byte_array = bytearray(dat)
        if len(byte_array) >= 12:
            self.update_state(byte_array)
            self.cache = byte_array
        return dat

    def listen(self, timeout=10):
        """Start the background read loop."""
        if self.pump_thread is not None and self.pump_thread.is_alive():
            return
        self.pump_thread = threading.Thread(target=self.pump, args=(timeout,))
        self.pump_thread.start()

    def pump(self, timeout=10):
        while self.connected:
            self.read(timeout)

    def stop(self):
        """Stop the background read loop."""
        if self.pump_thread is None:
            return
        if not self.pump_thread.is_alive():
            self.pump_thread = None
            return
        self.connected = False
        self.pump_thread.join()
        self.pump_thread = None

    def get_state(self):
        if not self.connected:
            raise Exception("G29 not connected")
        with self.state_lock:
            return copy.deepcopy(self.state)

    def get_events(self):
        if not self.connected:
            raise Exception("G29 not connected")
        with self.state_lock:
            events = copy.deepcopy(self.events)
            self.events.clear()
            return events

    def update_state(self, byte_array):
        with self.state_lock:
            new_state = self.decode_packet(byte_array)
            self.append_button_events(self.state["buttons"], new_state["buttons"])
            self.append_dial_events(byte_array[BUTTON_MISC2])
            self.state = new_state

    def append_button_events(self, old_buttons, new_buttons):
        for control, old_value in old_buttons.items():
            new_value = new_buttons[control]
            if old_value == new_value:
                continue
            if new_value:
                self.events.append({"type": "button_down", "control": control})
            else:
                self.events.append({"type": "button_up", "control": control})

    def append_dial_events(self, misc2_value):
        if misc2_value == MISC2_TRACK_RIGHT:
            self.events.append({"type": "dial", "delta": 1})
        elif misc2_value == MISC2_TRACK_LEFT:
            self.events.append({"type": "dial", "delta": -1})

    def decode_packet(self, byte_array):
        state = copy.deepcopy(EMPTY_STATE_TEMPLATE)
        state["steering"] = self.calc_steering(
            byte_array[STEERING_COARSE],
            byte_array[STEERING_FINE],
        )
        state["accelerator"] = self.calc_pedal(byte_array[PEDAL_ACCELERATOR])
        state["clutch"] = self.calc_pedal(byte_array[PEDAL_CLUTCH])
        state["brake"] = self.calc_pedal(byte_array[PEDAL_BRAKE])
        self.apply_gamepad(state, byte_array[GAME_PAD])
        self.apply_misc(state, byte_array[BUTTON_MISC])
        self.apply_plus(state, byte_array[BUTTON_PLUS])
        self.apply_misc2(state, byte_array[BUTTON_MISC2])
        return state

    def calc_steering(self, coarse_byte, fine_byte):
        # coarse 0-255
        # fine 0-255
        steering_raw = (coarse_byte << 8) | fine_byte  # 0-65535 for 16 bit integer
        # scale to -1 to 1
        steering_normalized = (steering_raw / 65535.0) * 2 - 1

        return steering_normalized

    def calc_pedal(self, val):
        # input 255-0
        normalized = (255 - val) / 255.0

        # scale to -1 to 1
        return normalized * 2 - 1

    def apply_gamepad(self, state, val):
        if val == GAME_PAD_NIL:
            return
        elif val == GAME_PAD_UP:
            state["buttons"]["up"] = 1
        elif val == GAME_PAD_DOWN:
            state["buttons"]["down"] = 1
        elif val == GAME_PAD_RIGHT:
            state["buttons"]["right"] = 1
        elif val == GAME_PAD_LEFT:
            state["buttons"]["left"] = 1
        elif val == GAME_PAD_X:
            state["buttons"]["X"] = 1
        elif val == GAME_PAD_SQUARE:
            state["buttons"]["S"] = 1
        elif val == GAME_PAD_CIRCLE:
            state["buttons"]["O"] = 1
        elif val == GAME_PAD_TRIANGLE:
            state["buttons"]["T"] = 1
        else:
            log.debug("unknown gamepad value: %s", val)

    def apply_misc(self, state, val):
        if val == MISC_NIL:
            return
        elif val == 0x01:
            state["buttons"]["right_paddle"] = 1
        elif val == 0x02:
            state["buttons"]["left_paddle"] = 1
        elif val == MISC_R2:
            state["buttons"]["R2"] = 1
        elif val == MISC_R3:
            state["buttons"]["R3"] = 1
        elif val == MISC_L2:
            state["buttons"]["L2"] = 1
        elif val == MISC_L3:
            state["buttons"]["L3"] = 1
        elif val == MISC_SHARE:
            state["buttons"]["Share"] = 1
        elif val == MISC_OPTIONS:
            state["buttons"]["Options"] = 1
        else:
            log.debug("unknown misc value: %s", val)

    def apply_plus(self, state, val):
        if val == BUTTON_PLUS_ON:
            state["buttons"]["+"] = 1
        elif val == BUTTON_PLUS_NIL:
            state["buttons"]["+"] = 0
        else:
            log.debug("unknown plus value: %s", val)

    def apply_misc2(self, state, val):
        if val == MISC2_NIL:
            return
        elif val == MISC2_MINUS:
            state["buttons"]["-"] = 1
        elif val == MISC2_TRACK_RIGHT:
            return
        elif val == MISC2_TRACK_LEFT:
            return
        elif val == MISC2_BACK:
            state["buttons"]["back"] = 1
        elif val == MISC2_PS:
            state["buttons"]["PS"] = 1
        else:
            log.debug("unknown misc2 value: %s", val)
