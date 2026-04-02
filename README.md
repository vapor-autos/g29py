# g29py
> python driver for logitech g29 wheel/pedals

> :warning: **Warning**: g29py is alpha software. This repository is under heavy development and subject to breaking changes. :warning:

![](etc/g29py.jpg)

## Install
```bash
pip install g29py
```

`g29py` depends on the PyPI `hidapi` package, which provides prebuilt wheels on common platforms.

If a wheel is not available for your platform and `pip` falls back to a source build on Linux, you may still need system HID dependencies such as:

```bash
sudo apt install libusb-1.0-0-dev libudev-dev
```

## Use

```python
from g29py import G29
g29 = G29()
```

```python
# write 
g29.set_range(500)
g29.set_friction(0.5)
g29.set_autocenter(ccw_proportion=0.5, cw_proportion=0.5, force=0.5)
```

```python
# read
g29.listen() # thread
while 1:
    state = g29.get_state()
    events = g29.get_events()
    print("steering:", state["steering"])
    print("brake:", state["brake"])
    print("accelerator", state["accelerator"])
    print("X:", state["buttons"]["X"])
    print("events:", events)
```

## Read

### State vs Events

The driver exposes two read models:

- `get_state()`
  - latest snapshot
  - use for steering, pedals, and held buttons
- `get_events()`
  - buffered transient input events
  - use for button edges and dial pulses

Rule of thumb:

- if you want to know what is true now, use state
- if you want to know what happened since the last poll, use events

### Pedals/Steering

| Pedal         | Value Range      | Neutral Position |
|---------------|------------------|------------------|
| `steering`    | Float: -1 to 1   | 0 (Centered)     |
| `accelerator` | Float: -1 to 1   | -1 (Not pressed) |
| `clutch`      | Float: -1 to 1   | -1 (Not pressed) |
| `brake`       | Float: -1 to 1   | -1 (Not pressed) |

### Buttons

| Button  | Value |
|---------|-------|
| `up`    | 0/1   |
| `down`  | 0/1   |
| `left`  | 0/1   |
| `right` | 0/1   |
| `X`     | 0/1   |
| `O`     | 0/1   |
| `S`     | 0/1   |
| `T`     | 0/1   |
| `R2`    | 0/1   |
| `R3`    | 0/1   |
| `L2`    | 0/1   |
| `L3`    | 0/1   |
| `Share` | 0/1   |
| `Options` | 0/1 |
| `+`     | 0/1   |
| `-`     | 0/1   |
| `back`  | 0/1   |
| `PS`    | 0/1   |

State is returned in a flattened shape:

```python
state = {
    "steering": 0.0,
    "accelerator": -1.0,
    "clutch": -1.0,
    "brake": -1.0,
    "buttons": {
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
        "back": 0,
        "PS": 0,
    },
}
```

### Events

Transient inputs are exposed through `get_events()`.

```python
events = g29.get_events()
```

Current event shapes:

```python
{"type": "button_down", "control": "X"}
{"type": "button_up", "control": "X"}
{"type": "dial", "delta": 1}
{"type": "dial", "delta": -1}
```

`get_events()` clears the buffered event queue on read.

## Write

| Method Name       | Default Parameters                         | Parameter Types                  |
|-------------------|--------------------------------------------|----------------------------------|
| `force_constant`  | `val=0.0`                                  | `val`: float (-1 to 1)           |
| `set_friction`    | `val=0.5`                                  | `val`: float                     |
| `set_range`       | `val=400`                                  | `val`: int (400-900)             |
| `set_autocenter`  | `ccw_proportion=0.5, cw_proportion=0.5, force=0.5` | `ccw_proportion`: float (0-1), `cw_proportion`: float (0-1), `force`: float (0-1) |
| `set_anticenter`  | `slot=1, cw_angle=180, ccw_angle=180, cw_proportion=0.5, ccw_proportion=0.5, cw_reverse=False, ccw_reverse=False, force=0.5` | `slot`: int (1-4), `cw_angle`: int (0-255), `ccw_angle`: int (0-255), `cw_proportion`: float (0-1), `ccw_proportion`: float (0-1), `cw_reverse`: bool, `ccw_reverse`: bool, `force`: float (0-1) |
| `autocenter_off`  | None                                       | None                             |
| `force_off`       | `slot=0xf3`                                | `slot`: hexadecimal              |

## Sources

- Commands were originally informed by nightmode's [logitech-g29](https://github.com/nightmode/logitech-g29) node.js driver.
- Effects/layout were cross-checked against [WiiBrew's Logitech USB steering wheel reference](https://wiibrew.org/wiki/Logitech_USB_steering_wheel).
- HID access is provided by the Python [`hidapi`](https://pypi.org/project/hidapi/) package.
- Behavior has also been manually verified against a real Logitech G29 on Linux.

## Development

Use Python `3.9+`.

Setup:

```bash
poetry install
```

Useful commands:

```bash
make test
make build
make twine-check
make release-test
```

Examples:

```bash
PYTHONPATH=. poetry run python -u examples/dial_events.py
PYTHONPATH=. poetry run python scripts/test_effects.py set_friction --val 0.5 --hold 5
```

## Support

Only Logitech G29 Driving Force Racing Wheels & Pedals kit supported on linux in ps3 mode.

On linux, remove sudo requirements by adding udev rule.

```bash
echo 'KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c24f", MODE="0664", GROUP="plugdev"' \
    | sudo tee /etc/udev/rules.d/99-g29py.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```
