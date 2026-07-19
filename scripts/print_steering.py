import time

from g29py import G29


if __name__ == "__main__":
    g29 = G29()
    g29.listen()

    try:
        while True:
            print("steering={:.3f}".format(g29.get_state()["steering"]), flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        g29.stop()
