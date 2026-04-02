import argparse
import pathlib
import time

from g29py import G29


def format_packet(dat):
    return " ".join(f"{byte:02x}" for byte in dat)


def main():
    parser = argparse.ArgumentParser(description="Capture changed G29 HID packets.")
    parser.add_argument(
        "--output",
        default="packet_capture.log",
        help="Path to the packet log file.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Stop after this many changed packets. Use 0 to run until interrupted.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Read timeout in milliseconds.",
    )
    args = parser.parse_args()

    output_path = pathlib.Path(args.output)
    g29 = G29()
    last_packet = None
    changes_seen = 0

    print(f"Capturing changed packets to {output_path}")
    print("Press Ctrl+C to stop.")

    with output_path.open("w", encoding="ascii") as handle:
        try:
            while True:
                dat = g29.read(timeout=args.timeout)
                if not dat:
                    continue

                packet = bytes(dat)
                if packet == last_packet:
                    continue

                last_packet = packet
                changes_seen += 1
                line = f"{changes_seen:04d} {time.time():.6f} {format_packet(packet)}"
                print(line)
                handle.write(line + "\n")
                handle.flush()

                if args.count and changes_seen >= args.count:
                    break
        except KeyboardInterrupt:
            print("\nCapture stopped.")


if __name__ == "__main__":
    main()
