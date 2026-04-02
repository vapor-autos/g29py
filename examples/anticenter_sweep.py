import time

from g29py import G29


RANGE = 500
SLOT = 1
CW_PROPORTION = 0.5
CCW_PROPORTION = 0.5
FORCE = 0.2
HOLD_SECONDS = 1.0

# Sweep equal clockwise / anti-clockwise angles across the byte range.
ANGLES = [0, 32, 64, 96, 128, 160, 192, 224, 255, 224, 192, 160, 128, 96, 64, 32, 0]


def main():
    g29 = G29()
    g29.set_range(RANGE)

    print("Sweeping anticenter angles. Press Ctrl+C to stop.", flush=True)

    try:
        for angle in ANGLES:
            print(
                f"angle={angle} cw_proportion={CW_PROPORTION} "
                f"ccw_proportion={CCW_PROPORTION} force={FORCE}",
                flush=True,
            )
            g29.set_anticenter(
                slot=SLOT,
                cw_angle=angle,
                ccw_angle=angle,
                cw_proportion=CW_PROPORTION,
                ccw_proportion=CCW_PROPORTION,
                force=FORCE,
            )
            time.sleep(HOLD_SECONDS)
    finally:
        g29.force_off()


if __name__ == "__main__":
    main()
