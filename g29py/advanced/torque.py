from dataclasses import dataclass
import math


CENTER_POSITION = 0.5


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(start, end, factor):
    return start + ((end - start) * factor)


def steering_to_effect_position(steering):
    return (clamp(steering, -1.0, 1.0) + 1.0) / 2.0


@dataclass
class SteeringTorqueConfig:
    park_velocity_m_s: float = 0.25
    full_centering_velocity_m_s: float = 11.0
    park_friction: float = 0.65
    rolling_friction: float = 0.25
    park_force: float = 0.15
    rolling_force: float = 0.75
    force_response_velocity_m_s: float = 6.0
    slot: int = 1
    cw_proportion: float = 1.0
    ccw_proportion: float = 1.0


@dataclass
class SteeringTorqueCommand:
    longitudinal_velocity_m_s: float
    speed_factor: float
    force_factor: float
    steering_position: float
    hold_position: float
    target_position: float
    force: float
    friction: float


class SteeringTorqueController:
    """Speed-based steering feel controller built from G29 effects."""

    def __init__(self, g29, config=None):
        self.g29 = g29
        self.config = config or SteeringTorqueConfig()

    def update(self, longitudinal_velocity_m_s, steering):
        config = self.config
        velocity = max(0.0, longitudinal_velocity_m_s)
        steering_position = steering_to_effect_position(steering)
        speed_factor = self._speed_factor(velocity)
        force_factor = self._force_factor(velocity)

        hold_position = steering_position

        if speed_factor == 0.0:
            target_position = hold_position
        else:
            target_position = CENTER_POSITION

        force = lerp(config.park_force, config.rolling_force, force_factor)
        friction = lerp(config.park_friction, config.rolling_friction, speed_factor)

        command = SteeringTorqueCommand(
            longitudinal_velocity_m_s=velocity,
            speed_factor=speed_factor,
            force_factor=force_factor,
            steering_position=steering_position,
            hold_position=hold_position,
            target_position=target_position,
            force=force,
            friction=friction,
        )
        self.apply(command)
        return command

    def apply(self, command):
        self.g29.set_anticenter(
            slot=self.config.slot,
            cw_position=command.target_position,
            ccw_position=command.target_position,
            cw_proportion=self.config.cw_proportion,
            ccw_proportion=self.config.ccw_proportion,
            force=command.force,
        )
        self.g29.set_friction(command.friction)

    def _speed_factor(self, velocity):
        config = self.config
        if velocity <= config.park_velocity_m_s:
            return 0.0
        if config.full_centering_velocity_m_s <= config.park_velocity_m_s:
            return 1.0

        active_range = config.full_centering_velocity_m_s - config.park_velocity_m_s
        return clamp((velocity - config.park_velocity_m_s) / active_range, 0.0, 1.0)

    def _force_factor(self, velocity):
        config = self.config
        if velocity <= config.park_velocity_m_s:
            return 0.0
        if config.force_response_velocity_m_s <= 0:
            return 1.0

        active_velocity = velocity - config.park_velocity_m_s
        return clamp(
            1.0 - math.exp(-active_velocity / config.force_response_velocity_m_s),
            0.0,
            1.0,
        )
