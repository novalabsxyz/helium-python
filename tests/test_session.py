from .util import HeliumMockTestCase


class TestHeliumSession(HeliumMockTestCase):

    def test_token_auth(self):
        assert self.client.headers.get('Authorization', None) is not None
        self.client.token_auth('test_auth')
        assert self.client.headers.get('Authorization') == 'test_auth'

    def test_request(self):
        response = self.client.request('get', self.client._build_url('user'))
        assert response is not None
