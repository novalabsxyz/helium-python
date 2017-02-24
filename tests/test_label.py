"""Test for Labels."""

from __future__ import unicode_literals
from helium import Label
import pytest


def test_create(client, first_sensor, first_element):
    label = None
    try:
        label = Label.create(client,
                             sensors=[first_sensor],
                             elements=[first_element],
                             attributes = {
                                 'name': "test_label"
                             })
        assert label is not None
        assert first_element in label.elements()
        assert first_sensor in label.sensors()
    finally:
        if label:
            label.delete()


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


def test_elements(tmp_label, elements, first_element):
    current_elements = tmp_label.elements()
    assert len(current_elements) == 0
    # Update to all elements
    assert tmp_label.update_elements(elements)

    # Remove an element
    assert tmp_label.remove_elements([first_element])
    assert first_element not in tmp_label.elements()
    assert not tmp_label.remove_elements([first_element])

    # Add an element
    assert tmp_label.add_elements([first_element])
    assert first_element in tmp_label.elements()
    assert not tmp_label.add_elements([first_element])

    # Ensure element is in label
    assert tmp_label in first_element.labels()

    # And check final result reflects the complete set
    current_elements = tmp_label.elements()
    assert set(elements) == set(current_elements)


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
