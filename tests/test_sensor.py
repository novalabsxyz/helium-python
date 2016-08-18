"""Test for Sensors."""

from __future__ import unicode_literals


def test_sensors(sensors, first_sensor):
    assert len(sensors) > 0
    assert first_sensor.id is not None


def test_metadata(first_sensor):
    metadata = first_sensor.metadata()
    assert metadata is not None
