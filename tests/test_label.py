"""Test for Labels."""

from __future__ import unicode_literals
from .util import HeliumMockTestCase
import helium


class TestHeliumLabels(HeliumMockTestCase):

    def setUp(self):
        super(TestHeliumLabels, self).setUp()
        labels = helium.Label.all(self.client)
        self.first_label = labels[0]
        self.assertIsNotNone(self.first_label.id)

    def test_sensors(self):
        sensors = self.first_label.sensors()
        self.assertIsNotNone(sensors)
        self.assertTrue(len(sensors) > 0)
