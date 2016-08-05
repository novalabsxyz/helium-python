from .util import HeliumMockTestCase
import helium


class TestHeliumSession(HeliumMockTestCase):

    def test_token_auth(self):
        self.assertIsNotNone(self.session.headers.get('Authorization'))
        self.session.token_auth('test_auth')
        self.assertEqual(self.session.headers.get('Authorization'),
                         'test_auth')

        session = helium.HeliumSession(api_token='XX')
        self.assertEqual(session.headers.get('Authorization'), 'XX')

    def test_request(self):
        response = self.client.request('get', self.client._build_url('user'))
        self.assertIsNotNone(response)
