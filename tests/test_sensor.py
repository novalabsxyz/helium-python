"""Test for Sensors."""

from __future__ import unicode_literals


def test_sensors(sensors, first_sensor):
    assert len(sensors) > 0
    assert first_sensor.id is not None


def test_update(tmp_sensor):
    updated_sensor = tmp_sensor.update(name='bar')
    assert updated_sensor.name == 'bar'
    assert updated_sensor.id == tmp_sensor.id


def test_metadata(first_sensor):
    metadata = first_sensor.metadata()
    assert metadata is not None


def test_meta(first_sensor):
    assert first_sensor.meta is not None
