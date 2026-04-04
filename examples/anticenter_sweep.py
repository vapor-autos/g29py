import time

from g29py import G29


RANGE = 500
SLOT = 1
CW_PROPORTION = 0.5
CCW_PROPORTION = 0.5
FORCE = 0.3
HOLD_SECONDS = 0.01
FINAL_CENTER_HOLD_SECONDS = 1.0
MAX_POSITION_STEP = 0.002

CENTER = 0.5
LEFT = 0.0
RIGHT = 1.0

SWEEP_SEGMENTS = [
    (CENTER, LEFT),
    (LEFT, RIGHT),
    (RIGHT, CENTER),
]


def build_segment(start, end, max_position_step):
    distance = abs(end - start)
    steps = max(2, int(distance / max_position_step) + 1)
    step_size = (end - start) / (steps - 1)
    return [start + (step_size * index) for index in range(steps)]


def build_positions(segments, max_position_step):
    positions = []
    for start, end in segments:
        segment = build_segment(start, end, max_position_step)
        if positions:
            segment = segment[1:]
        positions.extend(segment)
    return positions


POSITIONS = build_positions(SWEEP_SEGMENTS, MAX_POSITION_STEP)


def main():
    g29 = G29()
    g29.set_range(RANGE)

    print("Sweeping anticenter positions: center -> left -> right -> center", flush=True)

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
        print(f"final center hold: position={CENTER:.3f}", flush=True)
        g29.set_anticenter(
            slot=SLOT,
            cw_position=CENTER,
            ccw_position=CENTER,
            cw_proportion=CW_PROPORTION,
            ccw_proportion=CCW_PROPORTION,
            force=FORCE,
        )
        time.sleep(FINAL_CENTER_HOLD_SECONDS)
    finally:
        g29.force_off()


if __name__ == "__main__":
    main()
