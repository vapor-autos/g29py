import pytest

from g29py.advanced import (
    SteeringTorqueConfig,
    SteeringTorqueController,
)


class FakeG29:
    def __init__(self):
        self.anticenter_calls = []
        self.friction_calls = []

    def set_anticenter(self, **kwargs):
        self.anticenter_calls.append(kwargs)

    def set_friction(self, val):
        self.friction_calls.append(val)


def test_parked_update_holds_current_steering_position():
    g29 = FakeG29()
    controller = SteeringTorqueController(g29)

    command = controller.update(longitudinal_velocity_m_s=0.0, steering=1.0)

    assert command.speed_factor == pytest.approx(0.0)
    assert command.force_factor == pytest.approx(0.0)
    assert command.steering_position == pytest.approx(1.0)
    assert command.hold_position == pytest.approx(1.0)
    assert command.target_position == pytest.approx(command.hold_position)
    assert command.force == pytest.approx(0.15)
    assert command.friction == pytest.approx(0.65)
    assert g29.anticenter_calls[-1]["cw_position"] == pytest.approx(command.target_position)
    assert g29.anticenter_calls[-1]["ccw_position"] == pytest.approx(command.target_position)
    assert g29.friction_calls[-1] == pytest.approx(0.65)


def test_full_speed_update_targets_center_with_rolling_values():
    g29 = FakeG29()
    controller = SteeringTorqueController(g29)

    command = controller.update(longitudinal_velocity_m_s=20.0, steering=1.0)

    assert command.speed_factor == pytest.approx(1.0)
    assert command.hold_position == pytest.approx(1.0)
    assert command.target_position == pytest.approx(0.5)
    assert command.force == pytest.approx(0.7277, abs=0.0001)
    assert command.friction == pytest.approx(0.25)


def test_mid_speed_update_targets_center_and_interpolates_friction():
    g29 = FakeG29()
    config = SteeringTorqueConfig(
        park_velocity_m_s=0.0,
        full_centering_velocity_m_s=20.0,
        park_friction=0.65,
        rolling_friction=0.25,
        park_force=0.15,
        rolling_force=0.75,
    )
    controller = SteeringTorqueController(g29, config=config)

    command = controller.update(longitudinal_velocity_m_s=10.0, steering=1.0)

    assert command.speed_factor == pytest.approx(0.5)
    assert command.hold_position == pytest.approx(1.0)
    assert command.target_position == pytest.approx(0.5)
    assert command.friction == pytest.approx(0.45)


def test_hold_position_tracks_current_steering_while_rolling():
    g29 = FakeG29()
    controller = SteeringTorqueController(g29)

    rolling_command = controller.update(longitudinal_velocity_m_s=4.0, steering=1.0)
    command = controller.update(longitudinal_velocity_m_s=0.0, steering=1.0)

    assert rolling_command.speed_factor > 0.0
    assert rolling_command.hold_position == pytest.approx(1.0)
    assert rolling_command.target_position == pytest.approx(0.5)
    assert command.speed_factor == pytest.approx(0.0)
    assert command.hold_position == pytest.approx(1.0)
    assert command.target_position == pytest.approx(1.0)


def test_force_curve_uses_exponential_response_velocity():
    g29 = FakeG29()
    config = SteeringTorqueConfig(
        park_velocity_m_s=0.0,
        park_force=0.15,
        rolling_force=0.75,
        force_response_velocity_m_s=4.0,
    )
    controller = SteeringTorqueController(g29, config=config)

    command = controller.update(longitudinal_velocity_m_s=4.0, steering=0.0)

    assert command.force_factor == pytest.approx(0.6321, abs=0.0001)
    assert command.force == pytest.approx(0.5293, abs=0.0001)
