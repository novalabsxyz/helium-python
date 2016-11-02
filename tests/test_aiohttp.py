"""Tests for the aiohttp adapter."""

from __future__ import unicode_literals

import os
import pytest
import aiohttp
from helium import Client, Label, Sensor
from helium.adapter.aiohttp import Adapter


API_TOKEN = os.environ.get('HELIUM_API_KEY', 'X' * 10)
API_URL = os.environ.get('HELIUM_API_URL', 'https://api.helium.com/v1')

pytest_plugins = 'aiohttp.pytest_plugin'

@pytest.fixture
def aclient(loop, recorder):
    adapter = Adapter(loop=loop)
    loop.run_until_complete(adapter.__aenter__())

    client = Client(api_token=API_TOKEN, base_url=API_URL,
                    adapter=adapter)
    yield client

    loop.run_until_complete(adapter.__aexit__(None, None, None))


async def test_async_with_adapter(loop):
    async with Adapter(loop=loop) as adapter:
        pass

    assert adapter.closed

async def test_client(aclient):
    assert aclient.api_token == API_TOKEN

    # get
    sensors = await aclient.sensors()
    assert len(sensors) > 0

    # patch
    sensor = sensors[0]
    updated_sensor = await sensor.update(name=sensor.name)
    assert sensor.name == updated_sensor.name

    # post
    label = await Label.create(aclient, name="test-label")
    assert label is not None
    await label.add_sensors([sensor])

    # put
    metadata = await label.metadata()
    assert await metadata.replace(meta=25) == metadata

    # delete
    assert await label.delete() is True


async def test_datapoints(aclient):
    sensor = await Sensor.create(aclient, name="test_sensor")
    assert sensor is not None

    timeseries = sensor.timeseries()

    datapoints = await timeseries.take(0)
    assert len(await timeseries.take(0)) == 0
    assert len(await timeseries.take(2)) == 0

    datapoint = await timeseries.create('test_point', 22)
    assert datapoint is not None
    datapoint = await timeseries.create('test_point', 32)
    assert datapoint is not None

    timeseries = sensor.timeseries(page_size=1)
    datapoints = await timeseries.take(2)
    assert len(datapoints) == 2
    assert datapoints[0] == datapoint

    assert await sensor.delete() is True
