from g29py import G29


class FakeDevice:
    def __init__(self):
        self.writes = []

    def write(self, payload):
        self.writes.append(list(payload))


def make_test_g29():
    g29 = G29.__new__(G29)
    g29.device = FakeDevice()
    return g29


def test_set_anticenter_rounds_center_position_to_midpoint():
    g29 = make_test_g29()

    g29.set_anticenter(
        cw_position=0.5,
        ccw_position=0.5,
        cw_proportion=1.0,
        ccw_proportion=1.0,
        force=0.5,
    )

    assert g29.device.writes == [[0x11, 0x01, 0x80, 0x80, 0xFF, 0x00, 0x80]]


def test_set_autocenter_rounds_force_to_midpoint():
    g29 = make_test_g29()

    g29.set_autocenter(ccw_proportion=1.0, cw_proportion=1.0, force=0.5)

    assert g29.device.writes == [
        [0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        [0xFE, 0x0D, 0x07, 0x07, 0x80, 0x00, 0x00, 0x00],
    ]
