import time

from g29py import G29


RANGE = 500
SLOT = 1
CW_PROPORTION = 0.5
CCW_PROPORTION = 0.5
FORCE = 0.3
HOLD_SECONDS = 0.02
FINAL_CENTER_HOLD_SECONDS = 1.0

CENTER = 0.5
LEFT = 0.0
RIGHT = 1.0

STEPS_PER_HALF_SWEEP = 255


def interpolate(start, end, steps):
    if steps <= 1:
        return [start]
    return [
        start + ((end - start) * index / (steps - 1))
        for index in range(steps)
    ]


def build_positions(points, steps_per_half_sweep):
    positions = []
    for start, end in zip(points, points[1:]):
        distance = abs(end - start)
        steps = max(2, round((distance / 0.5) * steps_per_half_sweep))
        segment = interpolate(start, end, steps)
        if positions:
            segment = segment[1:]
        positions.extend(segment)
    return positions


# Smooth sweep: center -> left -> right -> center.
POSITIONS = build_positions(
    [CENTER, LEFT, RIGHT, CENTER],
    STEPS_PER_HALF_SWEEP,
)


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
