import argparse
import time

from g29py import G29
from g29py.advanced import (
    SteeringTorqueConfig,
    SteeringTorqueController,
    accelerator_to_longitudinal_velocity_m_s,
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Test speed-based steering torque simulation using accelerator pedal as velocity input."
    )
    parser.add_argument("--hold", type=float, default=20.0)
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--max-velocity", type=float, default=20.0)
    parser.add_argument("--park-velocity", type=float, default=0.25)
    parser.add_argument("--full-centering-velocity", type=float, default=11.0)
    parser.add_argument("--park-friction", type=float, default=0.65)
    parser.add_argument("--rolling-friction", type=float, default=0.25)
    parser.add_argument("--park-force", type=float, default=0.15)
    parser.add_argument("--rolling-force", type=float, default=0.75)
    parser.add_argument("--force-response-velocity", type=float, default=6.0)
    return parser


def accelerator_pedal(accelerator):
    return (max(-1.0, min(1.0, accelerator)) + 1.0) / 2.0


def main():
    args = build_parser().parse_args()
    g29 = G29()
    config = SteeringTorqueConfig(
        park_velocity_m_s=args.park_velocity,
        full_centering_velocity_m_s=args.full_centering_velocity,
        park_friction=args.park_friction,
        rolling_friction=args.rolling_friction,
        park_force=args.park_force,
        rolling_force=args.rolling_force,
        force_response_velocity_m_s=args.force_response_velocity,
    )
    controller = SteeringTorqueController(g29, config=config)

    print(
        "Running torque simulation:",
        f"max_velocity={args.max_velocity:.1f}m/s",
        f"park_force={args.park_force:.2f}",
        f"rolling_force={args.rolling_force:.2f}",
        f"force_response={args.force_response_velocity:.1f}m/s",
        f"park_friction={args.park_friction:.2f}",
        f"rolling_friction={args.rolling_friction:.2f}",
        flush=True,
    )

    g29.listen()
    try:
        end = time.time() + args.hold
        while time.time() < end:
            state = g29.get_state()
            pedal = accelerator_pedal(state["accelerator"])
            velocity = accelerator_to_longitudinal_velocity_m_s(
                state["accelerator"],
                max_velocity_m_s=args.max_velocity,
            )
            command = controller.update(
                longitudinal_velocity_m_s=velocity,
                steering=state["steering"],
            )
            print(
                "state:",
                f"steering={state['steering']:.3f}",
                f"accel_pedal={pedal:.2f}",
                f"velocity={velocity:.2f}m/s",
                f"factor={command.speed_factor:.2f}",
                f"force_factor={command.force_factor:.2f}",
                f"anchor={command.anchor_position:.3f}",
                f"target={command.target_position:.3f}",
                f"force={command.force:.2f}",
                f"friction={command.friction:.2f}",
                flush=True,
            )
            time.sleep(args.interval)
    finally:
        print("cleanup: force_off", flush=True)
        g29.force_off()
        g29.stop()


if __name__ == "__main__":
    main()
