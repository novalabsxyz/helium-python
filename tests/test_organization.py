"""Tests for Organization."""

from __future__ import unicode_literals
from .util import HeliumMockTestCase
import helium


class TestHeliumOrganization(HeliumMockTestCase):
    def setUp(self):
        super(TestHeliumOrganization, self).setUp()
        self.organization = helium.Organization.singleton(self.client)
        self.assertIsNotNone(self.organization)

    def test_users(self):
        users = self.organization.users()
        self.assertIsNotNone(users)
        self.assertTrue(len(users) > 0)

    def test_metadata(self):
        self.assertIsNotNone(self.organization.metadata())
