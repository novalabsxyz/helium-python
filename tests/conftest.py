from __future__ import unicode_literals

import os
import pytest
from betamax import Betamax
from betamax_serializers import pretty_json
from betamax_matchers import json_body

import helium

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
Betamax.register_request_matcher(json_body.JSONBodyMatcher)
API_TOKEN = os.environ.get('HELIUM_API_KEY', 'X' * 10)
API_URL = os.environ.get('HELIUM_API_URL', 'https://api.helium.com/v1')
RECORD_MODE = os.environ.get('HELIUM_RECORD_MODE', 'none')
RECORD_FOLDER = os.environ.get('HELIUM_RECORD_FOLDER', 'tests/cassettes')


with Betamax.configure() as config:
    config.cassette_library_dir = RECORD_FOLDER
    record_mode = RECORD_MODE
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

    cassette_name += request.function.__name__

    client = helium.Client(base_url=API_URL)
    client.api_token = API_TOKEN
    recorder = Betamax(client.adapter)
    setattr(recorder, 'client', client)

    recorder.use_cassette(cassette_name)
    recorder.start()
    request.addfinalizer(recorder.stop)
    return recorder


@pytest.fixture
def client(helium_recorder):
    """Return the helium.Client object used by the current recorder."""
    return helium_recorder.client


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
