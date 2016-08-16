"""Test for the resources module."""

from __future__ import unicode_literals

import pytest
import helium


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


def test_update_name(tmp_sensor):
    updated_sensor = tmp_sensor.update(name='bar')
    assert updated_sensor.name == 'bar'
    assert updated_sensor.id == tmp_sensor.id


def test_resource(client, tmp_sensor):
    sensor = helium.Sensor.find(client, tmp_sensor.id)
    assert sensor is not None
    assert sensor.id == tmp_sensor.id

    # equality
    assert tmp_sensor == sensor
    assert tmp_sensor != helium.Sensor({id: None}, None)

    # hash
    assert hash(sensor) is not None

    # __getattr__ lookup
    assert sensor.meta is not None
    with pytest.raises(AttributeError):
        sensor.no_such_attribute

    # short id
    assert sensor.short_id is not None
