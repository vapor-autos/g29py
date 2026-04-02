import argparse
import time

from g29py import G29


def format_bytes(values):
    return " ".join(f"{value:02x}" for value in values)


def log_write(label, values):
    print(f"{label}: {format_bytes(values)}")


def add_common_timing_args(parser):
    parser.add_argument(
        "--hold",
        type=float,
        default=3.0,
        help="Seconds to leave the effect active before cleanup.",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Read and print live state snapshots during the hold period.",
    )


def monitor_state(g29, hold_seconds, interval=0.1):
    end_time = time.time() + hold_seconds
    while time.time() < end_time:
        g29.read()
        state = g29.get_state()
        print(
            "state:",
            f"steering={state['steering']:.3f}",
            f"accelerator={state['accelerator']:.3f}",
            f"brake={state['brake']:.3f}",
            f"clutch={state['clutch']:.3f}",
        )
        time.sleep(interval)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run one G29 write effect at a time for manual testing."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    force_constant = subparsers.add_parser("force_constant")
    force_constant.add_argument("--val", type=float, default=0.0)
    add_common_timing_args(force_constant)

    friction = subparsers.add_parser("set_friction")
    friction.add_argument("--val", type=float, default=0.5)
    add_common_timing_args(friction)

    wheel_range = subparsers.add_parser("set_range")
    wheel_range.add_argument("--val", type=int, default=500)
    wheel_range.add_argument(
        "--reset-to",
        type=int,
        default=900,
        help="Range to restore after the hold period.",
    )
    add_common_timing_args(wheel_range)

    autocenter = subparsers.add_parser("set_autocenter")
    autocenter.add_argument("--ccw-proportion", type=float, default=0.5)
    autocenter.add_argument("--cw-proportion", type=float, default=0.5)
    autocenter.add_argument("--force", type=float, default=0.5)
    add_common_timing_args(autocenter)

    anticenter = subparsers.add_parser("set_anticenter")
    anticenter.add_argument("--slot", type=int, default=1)
    anticenter.add_argument("--cw-position", type=float, default=0.5)
    anticenter.add_argument("--ccw-position", type=float, default=0.5)
    anticenter.add_argument("--cw-proportion", type=float, default=0.5)
    anticenter.add_argument("--ccw-proportion", type=float, default=0.5)
    anticenter.add_argument("--cw-reverse", action="store_true")
    anticenter.add_argument("--ccw-reverse", action="store_true")
    anticenter.add_argument("--force", type=float, default=0.5)
    add_common_timing_args(anticenter)

    force_off = subparsers.add_parser("force_off")
    force_off.add_argument("--slot", type=lambda x: int(x, 0), default=0xF3)

    subparsers.add_parser("autocenter_off")
    subparsers.add_parser("reset")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    g29 = G29()
    print(f"Running {args.command}")

    if args.command == "force_constant":
        force = round((args.val + 1) * 127.5)
        log_write("write", [0x11, 0x00, force, 0x00, 0x00, 0x00, 0x00])
        g29.force_constant(args.val)
        if args.monitor:
            monitor_state(g29, args.hold)
        else:
            time.sleep(args.hold)
        log_write("cleanup", [0xF3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.force_off()
    elif args.command == "set_friction":
        force = round(int(args.val * 7))
        log_write("write", [0x21, 0x02, force, 0x00, force, 0x00, 0x00])
        g29.set_friction(args.val)
        if args.monitor:
            monitor_state(g29, args.hold)
        else:
            time.sleep(args.hold)
        log_write("cleanup", [0xF3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.force_off()
    elif args.command == "set_range":
        range1 = args.val & 0x00FF
        range2 = (args.val & 0xFF00) >> 8
        reset1 = args.reset_to & 0x00FF
        reset2 = (args.reset_to & 0xFF00) >> 8
        log_write("write", [0xF8, 0x81, range1, range2, 0x00, 0x00, 0x00])
        g29.set_range(args.val)
        if args.monitor:
            monitor_state(g29, args.hold)
        else:
            time.sleep(args.hold)
        log_write("cleanup", [0xF8, 0x81, reset1, reset2, 0x00, 0x00, 0x00])
        g29.set_range(args.reset_to)
    elif args.command == "set_autocenter":
        ccw_proportion = round(int(args.ccw_proportion * 7))
        cw_proportion = round(int(args.cw_proportion * 7))
        force = round(int(args.force * 255))
        log_write("write", [0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        log_write(
            "write",
            [
                0xFE,
                0x0D,
                ccw_proportion,
                cw_proportion,
                force,
                0x00,
                0x00,
                0x00,
            ],
        )
        g29.set_autocenter(
            ccw_proportion=args.ccw_proportion,
            cw_proportion=args.cw_proportion,
            force=args.force,
        )
        if args.monitor:
            monitor_state(g29, args.hold)
        else:
            time.sleep(args.hold)
        log_write("cleanup", [0xF5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.autocenter_off()
    elif args.command == "set_anticenter":
        cw_position = round(int(args.cw_position * 255))
        ccw_position = round(int(args.ccw_position * 255))
        cw_proportion = round(int(args.cw_proportion * 15))
        ccw_proportion = round(int(args.ccw_proportion * 15))
        cw_reverse = 0x1 if args.cw_reverse else 0x0
        ccw_reverse = 0x1 if args.ccw_reverse else 0x0
        force = round(int(args.force * 255))
        proportion_byte = (cw_proportion << 4) | ccw_proportion
        reverse_byte = (cw_reverse << 4) | ccw_reverse
        slot_command = ((1 << (args.slot - 1)) << 4) | 0x01
        log_write(
            "write",
            [slot_command, 0x01, cw_position, ccw_position, proportion_byte, reverse_byte, force],
        )
        print(
            f"args: slot={args.slot} subtype=0x01 cw_position={cw_position} ccw_position={ccw_position} "
            f"cw_proportion={cw_proportion} ccw_proportion={ccw_proportion} "
            f"cw_reverse={cw_reverse} ccw_reverse={ccw_reverse} force={force}"
        )
        g29.set_anticenter(
            slot=args.slot,
            cw_position=args.cw_position,
            ccw_position=args.ccw_position,
            cw_proportion=args.cw_proportion,
            ccw_proportion=args.ccw_proportion,
            cw_reverse=args.cw_reverse,
            ccw_reverse=args.ccw_reverse,
            force=args.force,
        )
        if args.monitor:
            monitor_state(g29, args.hold)
        else:
            time.sleep(args.hold)
        log_write("cleanup", [0xF3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.force_off()
    elif args.command == "force_off":
        log_write("write", [args.slot, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.force_off(args.slot)
    elif args.command == "autocenter_off":
        log_write("write", [0xF5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        g29.autocenter_off()
    elif args.command == "reset":
        log_write("write", [0xF8, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
        log_write("write", [0xF8, 0x09, 0x05, 0x01, 0x01, 0x00, 0x00])
        g29.reset()
    else:
        parser.error(f"Unknown command: {args.command}")

    print("Done.")


if __name__ == "__main__":
    main()
