# Reads from G29 in a loop and prints the values.

if __name__ == "__main__":
    import time
    from g29py import G29
    g29 = G29()
    g29.set_range(500)
    g29.set_autocenter(0.25, 0.25)
    g29.listen()
    while True:
        state = g29.get_state()
        time.sleep(0.1)
