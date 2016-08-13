"""Test for Labels."""

from __future__ import unicode_literals
from .util import HeliumMockTestCase
import helium


class TestHeliumLabels(HeliumMockTestCase):

    def test_sensors(self):
        label = helium.Label.create(self.client, name="test-label", sensors=[])
        self.assertIsNotNone(label.id)

        self.assertTrue(len(label.sensors()) == 0)
        # Fetch some sensors
        sensors = helium.Sensor.all(self.client)
        self.assertTrue(len(sensors) > 0)
        # update all sensors for the label
        updated_sensors = label.update_sensors(sensors)
        self.assertTrue(len(updated_sensors) > 0)
        # remove a sensor
        sensor = sensors[0]
        updated_sensors = label.remove_sensors([sensor])
        self.assertFalse(sensor in updated_sensors)
        # add a sensor
        updated_sensors = label.add_sensors([sensor])
        self.assertTrue(sensor in updated_sensors)

        self.assertTrue(label.delete())
