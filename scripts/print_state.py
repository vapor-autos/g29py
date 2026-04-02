import time

from g29py import G29


if __name__ == "__main__":
    g29 = G29()
    g29.listen()

    try:
        while True:
            state = g29.get_state()
            events = g29.get_events()
            active_buttons = {
                name: value for name, value in state["buttons"].items() if value
            }
            print(
                "steering={:.3f} accelerator={:.3f} brake={:.3f} clutch={:.3f}".format(
                    state["steering"],
                    state["accelerator"],
                    state["brake"],
                    state["clutch"],
                ),
                flush=True,
            )
            if active_buttons:
                print(f"buttons={active_buttons}", flush=True)
            if events:
                print(f"events={events}", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
