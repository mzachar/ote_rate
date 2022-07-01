"""Platform for sensor integration."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.sensor import  (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.const import (
    CURRENCY_EURO,
    CURRENCY_DOLLAR,
    ENERGY_MEGA_WATT_HOUR,
    ENERGY_KILO_WATT_HOUR,
)

""" External Imports """
import requests
import json
import datetime
import logging


""" Constants """
_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType) -> None:
    """Set up the sensor platform."""
    add_entities([OTERateSensor()], update_before_add=True)


class OTERateSensor(SensorEntity):
    """Representation of a Sensor."""
    
    _attr_name = "Current OTE Energy Cost"
    _attr_native_unit_of_measurement = f'{CURRENCY_EURO}/{ENERGY_KILO_WATT_HOUR}'
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_available = False

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        
        Parse the data and return value in EUR/kWh
        """
        try:
          current_cost = 0
          cost_history = dict()
          history_index = 0
          cost_string = "Cena (EUR/MWh)"
          hour_string = "Hodina"
          cost_data = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"

          date = datetime.datetime.now()
          params = dict (
              date = date.strftime('%Y-%m-%d')
          )

          response = requests.get(url=cost_data, params=params)
          json = response.json()
          cost_axis = ""
          hour_axis = ""
          for key in json['axis'].keys():
              if json['axis'][key]['legend'] == cost_string:
                  cost_axis = key
              if json['axis'][key]['legend'] == hour_string:
                  hour_axis = key


          for values in json['data']['dataLine']:
              if values['title'] == cost_string:
                  for data in values['point']:
                     history_index = int(data[hour_axis])-1
                     cost_history[history_index] = round(float(data[cost_axis]) / 1000, 4)
                  current_cost = cost_history[date.hour]


          self._attr_native_value = current_cost
          self._attr_extra_state_attributes = cost_history
          self._attr_available = True
        except:
          self._attr_available = False
          _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
