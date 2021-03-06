"""
Support for Danfoss Air HRV.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/danfoss_air/
"""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.const import CONF_HOST
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

REQUIREMENTS = ['pydanfossair==0.0.6']

_LOGGER = logging.getLogger(__name__)

DANFOSS_AIR_PLATFORMS = ['sensor', 'binary_sensor']
DOMAIN = 'danfoss_air'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Danfoss Air component."""
    conf = config[DOMAIN]

    hass.data[DOMAIN] = DanfossAir(conf[CONF_HOST])

    for platform in DANFOSS_AIR_PLATFORMS:
        discovery.load_platform(hass, platform, DOMAIN, {}, config)

    return True


class DanfossAir:
    """Handle all communication with Danfoss Air CCM unit."""

    def __init__(self, host):
        """Initialize the Danfoss Air CCM connection."""
        self._data = {}

        from pydanfossair.danfossclient import DanfossClient

        self._client = DanfossClient(host)

    def get_value(self, item):
        """Get value for sensor."""
        if item in self._data:
            return self._data[item]

        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Use the data from Danfoss Air API."""
        _LOGGER.debug("Fetching data from Danfoss Air CCM module")
        from pydanfossair.commands import ReadCommand
        self._data[ReadCommand.exhaustTemperature] \
            = self._client.command(ReadCommand.exhaustTemperature)
        self._data[ReadCommand.outdoorTemperature] \
            = self._client.command(ReadCommand.outdoorTemperature)
        self._data[ReadCommand.supplyTemperature] \
            = self._client.command(ReadCommand.supplyTemperature)
        self._data[ReadCommand.extractTemperature] \
            = self._client.command(ReadCommand.extractTemperature)
        self._data[ReadCommand.humidity] \
            = round(self._client.command(ReadCommand.humidity), 2)
        self._data[ReadCommand.filterPercent] \
            = round(self._client.command(ReadCommand.filterPercent), 2)
        self._data[ReadCommand.bypass] \
            = self._client.command(ReadCommand.bypass)

        _LOGGER.debug("Done fetching data from Danfoss Air CCM module")
