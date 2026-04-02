import time

from g29py import G29


MIN_DIAL = -100
MAX_DIAL = 100


def clamp(value, low, high):
    return max(low, min(high, value))


def main():
    g29 = G29()
    dial = 0
    last_printed = dial

    print("Tracking dial events. Press Ctrl+C to stop.", flush=True)
    print(f"dial={dial}", flush=True)

    try:
        while True:
            g29.read()
            events = g29.get_events()
            for event in events:
                if event["type"] != "dial":
                    continue
                dial = clamp(dial + event["delta"], MIN_DIAL, MAX_DIAL)
                if dial != last_printed:
                    print(f"dial={dial}", flush=True)
                    last_printed = dial
            time.sleep(0.01)
    finally:
        g29.force_off()
        g29.autocenter_off()


if __name__ == "__main__":
    main()
