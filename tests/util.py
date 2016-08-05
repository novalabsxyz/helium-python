import os
from betamax import Betamax
from betamax.fixtures import unittest
from betamax_serializers import pretty_json
from betamax_matchers import json_body

import helium

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
Betamax.register_request_matcher(json_body.JSONBodyMatcher)


class HeliumMockTestCase(unittest.BetamaxTestCase):
    """unittest test case that wraps and configures betamax for tests that
    require mocking HTTP requests in helium-python
    """
    SESSION_CLASS = helium.HeliumClient

    def setUp(self):
        if os.environ.get('TRAVIS'):
            token = 'X'*10
        else:
            token = os.environ.get('HELIUM_TEST_API_KEY')
            assert token, 'Please set HELIUM_TEST_API_KEY to a valid API key'
        with Betamax.configure() as config:
            config.cassette_library_dir = 'tests/cassettes'
            record_mode = 'never' if os.environ.get('TRAVIS') else 'once'
            config.define_cassette_placeholder('<AUTH_TOKEN>', token)

            cassette_options = config.default_cassette_options
            cassette_options['record_mode'] = record_mode
            cassette_options['serialize_with'] = 'prettyjson'
            cassette_options['match_requests_on'].append('json-body')

        super(HeliumMockTestCase, self).setUp()

        self.recorder.session.token_auth(token)
        self.client = self.recorder.session
