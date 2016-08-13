"""Test for Labels."""

from __future__ import unicode_literals
from .util import HeliumMockTestCase
from contextlib import contextmanager
import uuid
import helium


class TestHeliumLabels(HeliumMockTestCase):

    @contextmanager
    def temp_label(self, **kwargs):
        label = None
        try:
            label = helium.Label.create(self.client,
                                        name="test_label",
                                        **kwargs)
            yield label
        finally:
            if label is not None:
                self.assertTrue(label.delete())

    def test_create_delete(self):
        with self.temp_label(sensors=[]) as label:
            self.assertIsNotNone(label)
            self.assertIsNotNone(label.id)

    def test_sensors(self):
        with self.temp_label() as label:
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
