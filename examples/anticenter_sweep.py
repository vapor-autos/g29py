import time

from g29py import G29


RANGE = 500
SLOT = 1
CW_PROPORTION = 0.5
CCW_PROPORTION = 0.5
FORCE = 0.2
HOLD_SECONDS = 1.0

# Sweep equal clockwise / anti-clockwise positions across the normalized range.
POSITIONS = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0]


def main():
    g29 = G29()
    g29.set_range(RANGE)

    print("Sweeping anticenter positions. Press Ctrl+C to stop.", flush=True)

    try:
        for position in POSITIONS:
            print(
                f"position={position:.3f} cw_proportion={CW_PROPORTION} "
                f"ccw_proportion={CCW_PROPORTION} force={FORCE}",
                flush=True,
            )
            g29.set_anticenter(
                slot=SLOT,
                cw_position=position,
                ccw_position=position,
                cw_proportion=CW_PROPORTION,
                ccw_proportion=CCW_PROPORTION,
                force=FORCE,
            )
            time.sleep(HOLD_SECONDS)
    finally:
        g29.force_off()


if __name__ == "__main__":
    main()
