"""Tests for DeviceConfiguration."""

from __future__ import unicode_literals
from helium import DeviceConfiguration, Device, Configuration


def test_with_sensor(client, tmp_configuration, first_sensor):
    device_config = DeviceConfiguration.create(client,
                                               configuration=tmp_configuration,
                                               device=first_sensor)
    assert device_config is not None
    assert device_config.configuration() == tmp_configuration
    assert device_config.device() == first_sensor

    # Test include of relationships
    fetch = DeviceConfiguration.find(client, device_config.id,
                                     include=[Device, Configuration])
    assert fetch.device(use_included=True) == first_sensor
    assert fetch.device(use_included=True).__class__ == first_sensor.__class__
    assert fetch.configuration(use_included=True) == tmp_configuration

    # Test reverse. A device can have a loaded an a pending configuration
    fetch = first_sensor.device_configurations()
    assert device_config in fetch
    assert len(fetch) <= 2
    assert first_sensor.device_configuration(pending=True) == device_config

    assert device_config.delete()


def test_with_element(client, tmp_configuration, first_element):
    device_config = DeviceConfiguration.create(client,
                                               configuration=tmp_configuration,
                                               device=first_element)
    assert device_config is not None
    assert device_config.configuration() == tmp_configuration
    assert device_config.device() == first_element

    # Test reverse. A device can have a loaded and a pending configuration
    # The pending version of this test is in test_with_sensor
    fetch = first_element.device_configuration(pending=False)
    assert fetch is None

    assert device_config.delete()
