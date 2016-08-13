from .util import HeliumMockTestCase


class TestHeliumClient(HeliumMockTestCase):
    def _assert_all_resources(self, resources):
        assert len(resources) > 0

    def _assert_find_resource(self, resources, find_resource):
        resource_id = resources[0].id
        resource = find_resource(resource_id)
        assert resource.id == resource_id

    def test_all_sensors(self):
        resources = self.client.sensors()
        self._assert_all_resources(resources)

    def test_find_sensor(self):
        sensors = self.client.sensors()
        self._assert_find_resource(sensors, self.client.sensor)

    def test_all_labels(self):
        resources = self.client.labels()
        self._assert_all_resources(resources)

    def test_find_label(self):
        labels = self.client.labels()
        self._assert_find_resource(labels, self.client.label)

    def test_organization(self):
        org = self.client.authorized_organization()
        self.assertIsNotNone(org)

    def test_user(self):
        user = self.client.authorized_user()
        self.assertIsNotNone(user)
