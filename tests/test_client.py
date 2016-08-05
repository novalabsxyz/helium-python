from .util import HeliumMockTestCase


class TestHeliumClient(HeliumMockTestCase):
    def _assert_all_resources(self, resources):
        assert len(resources) > 0

    def _assert_find_resource(self, resources, find_resource):
        resource_id = resources[0].id
        resource = find_resource(resource_id)
        assert resource.id == resource_id

    def test_all_sensors(self):
        resources = self.client.all_sensors()
        self._assert_all_resources(resources)

    def test_find_sensor(self):
        sensors = self.client.all_sensors()
        self._assert_find_resource(sensors, self.client.find_sensor)

    def test_all_labels(self):
        resources = self.client.all_labels()
        self._assert_all_resources(resources)

    def test_find_label(self):
        labels = self.client.all_labels()
        self._assert_find_resource(labels, self.client.find_label)
