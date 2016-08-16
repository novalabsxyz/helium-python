"""Test for Labels."""

from __future__ import unicode_literals


def test_sensors(temp_label, sensors, first_sensor):
    current_sensors = temp_label.sensors()
    assert len(current_sensors) == 0
    # Update all sensors
    updated_sensors = temp_label.update_sensors(sensors)
    assert len(updated_sensors) > 0
    # Remove a sensor
    updated_sensors = temp_label.remove_sensors([first_sensor])
    assert first_sensor not in updated_sensors
    # Add a sensor
    updated_sensors = temp_label.add_sensors([first_sensor])
    assert first_sensor in updated_sensors
    # Ensure sensor is in label
    assert temp_label in first_sensor.labels()

    # And check final result reflects the complete set
    current_sensors = temp_label.sensors()
    assert set(updated_sensors) == set(current_sensors)
