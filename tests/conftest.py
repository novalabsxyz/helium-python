from __future__ import unicode_literals

import os
import pytest
from betamax import Betamax
from betamax_serializers import pretty_json
from betamax_matchers import json_body

import helium

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
Betamax.register_request_matcher(json_body.JSONBodyMatcher)
if os.environ.get('TRAVIS'):
    API_TOKEN = 'X' * 10
else:
    API_TOKEN = os.environ.get('HELIUM_TEST_API_KEY')
    assert API_TOKEN, 'Please set HELIUM_TEST_API_KEY to a valid API key'

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    record_mode = 'none' if os.environ.get('TRAVIS') else 'once'
    cassette_options = config.default_cassette_options
    cassette_options['record_mode'] = record_mode
    cassette_options['serialize_with'] = 'prettyjson'
    cassette_options['match_requests_on'].append('json-body')
    config.define_cassette_placeholder('<AUTH_TOKEN>', API_TOKEN)


@pytest.fixture
def helium_recorder(request):
    """Generate and start a recorder using a helium.Client."""
    cassette_name = ''

    if request.module is not None:
        cassette_name += request.module.__name__ + '.'

    if request.cls is not None:
        cassette_name += request.cls.__name__ + '.'

    cassette_name += request.function.__name__

    session = helium.Client()
    session.token_auth(API_TOKEN)
    recorder = Betamax(session)

    recorder.use_cassette(cassette_name)
    recorder.start()
    request.addfinalizer(recorder.stop)
    return recorder


@pytest.fixture
def client(helium_recorder):
    """Return the helium.Client object used by the current recorder."""
    return helium_recorder.session


@pytest.fixture
def sensors(client):
    """Returns the all known sensors for the active helium.Client."""
    return helium.Sensor.all(client)


@pytest.fixture
def first_sensor(sensors):
    """Return the first of the known sensor for the active helium.Client"""
    return sensors[0]


@pytest.yield_fixture
def tmp_sensor(client):
    sensor = helium.Sensor.create(client, name='test')
    yield sensor
    sensor.delete()


@pytest.yield_fixture
def tmp_label(client):
    """Yield a temporary label called 'temp-label'.

    The label is deleted after the test completes.
    """
    label = helium.Label.create(client, name='temp-label', sensors=[])
    yield label
    label.delete()


@pytest.fixture
def elements(client):
    """Returns the all known elements for the active helium.Client."""
    return helium.Element.all(client)


@pytest.fixture
def first_element(elements):
    """Return the first of the known elements for the active helium.Client"""
    return elements[0]


@pytest.fixture
def authorized_user(client):
    return client.authorized_user()


@pytest.fixture
def authorized_organization(client):
    return client.authorized_organization()
