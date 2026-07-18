"""Support for PWM fans controlled via a pigpio daemon."""
from __future__ import annotations

import logging

import pigpio
import voluptuous as vol

from homeassistant.components.fan import (
    PLATFORM_SCHEMA,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_PIN = "pin"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_FREQUENCY = "frequency"
CONF_FANS = "fans"

DEFAULT_HOST = "68413af6-pigpio"
DEFAULT_PORT = 8888
DEFAULT_FREQUENCY = 25000

FAN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PIN): cv.positive_int,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): cv.positive_int,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FANS): vol.All(cv.ensure_list, [FAN_SCHEMA]),
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the pigpio PWM fan platform."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    pi = pigpio.pi(host, port)
    if not pi.connected:
        _LOGGER.error("Could not connect to pigpio daemon at %s:%s", host, port)
        return

    fans = [PigpioPwmFan(pi, fan_conf) for fan_conf in config[CONF_FANS]]
    add_entities(fans, True)


class PigpioPwmFan(FanEntity):
    """Representation of a PWM-controlled fan driven by pigpio."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_should_poll = False

    def __init__(self, pi: pigpio.pi, config: dict) -> None:
        """Initialize the fan."""
        self._pi = pi
        self._pin = config[CONF_PIN]
        self._attr_name = config[CONF_NAME]
        self._attr_unique_id = config.get(CONF_UNIQUE_ID)
        self._frequency = config[CONF_FREQUENCY]
        self._attr_percentage = 0
        self._attr_is_on = False

        self._pi.set_mode(self._pin, pigpio.OUTPUT)
        self._pi.set_PWM_frequency(self._pin, self._frequency)
        # Use a 0-100 duty cycle range so it maps directly to percentage.
        self._pi.set_PWM_range(self._pin, 100)

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        self._pi.set_PWM_dutycycle(self._pin, percentage)
        self._attr_percentage = percentage
        self._attr_is_on = percentage > 0
        self.schedule_update_ha_state()

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        """Turn on the fan."""
        self.set_percentage(percentage if percentage is not None else 50)

    def turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        self.set_percentage(0)
