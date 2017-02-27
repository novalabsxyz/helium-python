"""Test for the resources module."""

from __future__ import unicode_literals

import pytest
import helium
import pickle
from datetime import datetime


def test_notfound_resource(client):
    with pytest.raises(helium.NotFoundError):
        helium.Sensor.find(client,
                           "A44D968E-50B4-4A4E-A6A5-C5283863C59D")


def test_invalid_id(client):
    with pytest.raises(helium.ClientError) as raised:
        helium.Sensor.find(client, 'xx')

    raised = raised.value
    assert raised.message is not None
    assert raised.code == 400
    assert str(raised).startswith('400')


def test_create(tmp_sensor):
    assert tmp_sensor is not None
    assert tmp_sensor.id is not None
    assert tmp_sensor.name == 'test'


def test_find(client, tmp_sensor):
    sensor = helium.Sensor.find(client, tmp_sensor.id)
    assert sensor is not None
    assert sensor.id == tmp_sensor.id
    assert tmp_sensor == sensor


def test_update(tmp_sensor):
    updated_sensor = tmp_sensor.update(attributes={
        'name': 'bar'
    })
    assert updated_sensor.name == 'bar'
    assert updated_sensor.id == tmp_sensor.id


def test_meta(tmp_sensor):
    meta = tmp_sensor.meta
    assert meta is not None
    assert meta.created is not None
    assert meta.updated is not None


def test_basic(client, tmp_sensor):
    # equality
    assert tmp_sensor != helium.Sensor({id: None}, None)

    # hash
    assert hash(tmp_sensor) is not None

    # __getattr__ lookup
    with pytest.raises(AttributeError):
        tmp_sensor.no_such_attribute

def test_pickles(tmp_sensor):
    pickled = pickle.dumps(tmp_sensor)
    assert pickle.loads(pickled) == tmp_sensor
