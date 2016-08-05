from .util import HeliumMockTestCase
import helium


class TestHeliumResources(HeliumMockTestCase):
    def setUp(self):
        super(TestHeliumResources, self).setUp()
        sensors = helium.Sensor.all(self.client)
        self.first_sensor = sensors[0]
        self.assertIsNotNone(self.first_sensor.id)

    def test_resource(self):
        sensor = helium.Sensor.find(self.client, self.first_sensor.id)
        self.assertIsNotNone(sensor)

        # equality
        self.assertEqual(self.first_sensor, sensor)
        self.assertNotEqual(self.first_sensor,
                            helium.Sensor({id: None}, None))
        self.assertNotEqual(self.first_sensor, object())

        # hash
        self.assertIsNotNone(hash(self.first_sensor))

        # __getattr__ lookup
        self.assertIsNotNone(sensor.meta)
        with self.assertRaises(AttributeError):
            sensor.no_such_attribute

        # short id
        self.assertIsNotNone(self.first_sensor.short_id())

    def test_404_resource(self):
        sensor = helium.Sensor.find(self.client,
                                    "A44D968E-50B4-4A4E-A6A5-C5283863C59D")
        self.assertIsNone(sensor)

    def test_exception_resource(self):
        with self.assertRaises(helium.ClientError) as raised:
            helium.Sensor.find(self.client, 'xx')
        self.assertIsNotNone(raised.exception.message)
        self.assertEqual(raised.exception.code, 400)
        self.assertTrue(str(raised.exception).startswith('400'))
