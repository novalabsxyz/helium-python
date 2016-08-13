"""Test for Sensors."""

from __future__ import unicode_literals
from .util import HeliumMockTestCase
import helium


class TestHeliumSensors(HeliumMockTestCase):

    def setUp(self):
        super(TestHeliumSensors, self).setUp()
        sensors = helium.Sensor.all(self.client)
        self.first_sensor = sensors[0]
        self.assertIsNotNone(self.first_sensor.id)

    def test_labels(self):
        labels = self.first_sensor.labels()
        self.assertIsNotNone(labels)
        self.assertTrue(len(labels) > 0)
