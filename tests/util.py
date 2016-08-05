import os
from betamax import Betamax
from betamax.fixtures import unittest
from betamax_serializers import pretty_json
from betamax_matchers import json_body

import helium

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
Betamax.register_request_matcher(json_body.JSONBodyMatcher)
if os.environ.get('TRAVIS'):
    API_TOKEN = 'X'*10
else:
    API_TOKEN = os.environ.get('HELIUM_TEST_API_KEY')
    assert API_TOKEN, 'Please set HELIUM_TEST_API_KEY to a valid API key'

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    record_mode = 'none' if os.environ.get('TRAVIS') else 'new_episodes'
    cassette_options = config.default_cassette_options
    cassette_options['record_mode'] = record_mode
    cassette_options['serialize_with'] = 'prettyjson'
    cassette_options['match_requests_on'].append('json-body')
    config.define_cassette_placeholder('<AUTH_TOKEN>', API_TOKEN)


class HeliumMockTestCase(unittest.BetamaxTestCase):
    """unittest test case that wraps and configures betamax for tests that
    require mocking HTTP requests in helium-python
    """
    SESSION_CLASS = helium.HeliumClient

    def setUp(self):
        super(HeliumMockTestCase, self).setUp()

        self.session.token_auth(API_TOKEN)
        self.client = self.session
