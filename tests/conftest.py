from __future__ import unicode_literals

import os
import sys
import pytest
# from betamax import Betamax
# from betamax_serializers import pretty_json
# from betamax_matchers import json_body

from vcr import VCR

import helium

collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append(os.path.join(os.path.dirname(__file__),
                                       'test_aiohttp.py'))

API_TOKEN = os.environ.get('HELIUM_API_KEY', 'X' * 10)
API_URL = os.environ.get('HELIUM_API_URL', 'https://api.helium.com/v1')
RECORD_FOLDER = os.environ.get('HELIUM_RECORD_FOLDER', 'tests/cassettes')



@pytest.fixture
def recorder(request):
    """Generate and start a recorder using a helium.Client."""
    cassette_name = ''

    if request.module is not None:
        cassette_name += request.module.__name__ + '.'

    cassette_name += request.function.__name__

    recorder = VCR(
        cassette_library_dir=RECORD_FOLDER,
        decode_compressed_response=True,
        path_transformer=VCR.ensure_suffix('.yml'),
        filter_headers=['Authorization'],
        match_on=['uri', 'method'],
    )
    cassette = recorder.use_cassette(path=cassette_name)
    with cassette:
        yield recorder


@pytest.fixture
def client(recorder):
    """Return the helium.Client object used by the current recorder."""
    client = helium.Client(base_url=API_URL)
    client.api_token = API_TOKEN
    return client

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
