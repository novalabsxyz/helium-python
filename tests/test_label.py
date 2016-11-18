"""Test for Labels."""

from __future__ import unicode_literals
import pytest


def test_sensors(tmp_label, sensors, first_sensor):
    current_sensors = tmp_label.sensors()
    assert len(current_sensors) == 1
    # Update all sensors
    assert tmp_label.update_sensors(sensors)

    # Remove a sensor
    assert tmp_label.remove_sensors([first_sensor])
    assert first_sensor not in tmp_label.sensors()
    assert not tmp_label.remove_sensors([first_sensor])

    # Add a sensor
    assert tmp_label.add_sensors([first_sensor])
    assert first_sensor in tmp_label.sensors()
    assert not tmp_label.add_sensors([first_sensor])

    # Ensure sensor is in label
    assert tmp_label in first_sensor.labels()

    # And check final result reflects the complete set
    current_sensors = tmp_label.sensors()
    assert set(sensors) == set(current_sensors)


def test_update(tmp_label):
    updated = tmp_label.update(attributes={
        'name': 'bar'
    })
    assert updated.name == 'bar'
    assert updated == tmp_label


def test_metadata(tmp_label):
    metadata = tmp_label.metadata()
    assert metadata is not None


def test_meta(tmp_label):
    assert tmp_label.meta is not None
