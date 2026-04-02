"""
Manual hardware smoke checks for a real Logitech G29.

These are intentionally not part of the automated pytest suite.
Run them manually when you want a quick sanity pass on a connected wheel.
"""

import time

from g29py import G29


def check_init():
    g29 = G29()
    assert g29.state is not None
    assert g29.cache is None


def check_read():
    g29 = G29()
    dat = g29.read()
    assert dat is not None


def check_reset():
    g29 = G29()
    g29.reset()


def check_force_off():
    g29 = G29()
    g29.force_off(0xF3)


def check_set_friction():
    g29 = G29()
    g29.set_friction(0.5)
    time.sleep(5)
    g29.force_off(0xF3)


def check_set_range():
    g29 = G29()
    g29.set_range(500)
    time.sleep(5)
    g29.set_range(900)


def check_set_autocenter():
    g29 = G29()
    g29.set_autocenter(ccw_proportion=0.5, cw_proportion=0.5, force=0.5)
    time.sleep(5)
    g29.autocenter_off()


if __name__ == "__main__":
    checks = [
        ("init", check_init),
        ("read", check_read),
        ("reset", check_reset),
        ("force_off", check_force_off),
        ("set_friction", check_set_friction),
        ("set_range", check_set_range),
        ("set_autocenter", check_set_autocenter),
    ]

    for name, fn in checks:
        print(f"running {name}...", flush=True)
        fn()
        print(f"ok: {name}", flush=True)
