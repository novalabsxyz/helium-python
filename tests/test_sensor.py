"""Test for Sensors."""

from __future__ import unicode_literals
from helium import Sensor, Element
from helium import to_one, to_many, RelationType
from builtins import filter
import pytest


def test_sensors(sensors, first_sensor):
    assert len(sensors) > 0
    assert first_sensor.id is not None


def test_update(tmp_sensor):
    updated_sensor = tmp_sensor.update(attributes={
        'name': 'bar'
    })
    assert updated_sensor.name == 'bar'
    assert updated_sensor.id == tmp_sensor.id


def test_metadata(first_sensor):
    metadata = first_sensor.metadata()
    assert metadata is not None


def test_metadata_filter(client, tmp_sensor):
    metadata = tmp_sensor.metadata()
    updated = metadata.replace({
        'foo': 22
    })
    assert updated.foo == 22
    found = Sensor.where(client, metadata={
        'foo': 22
    })
    assert tmp_sensor in found


def test_meta(first_sensor):
    assert first_sensor.meta is not None


def test_element(client):
    sensors = Sensor.all(client, include=[Element])
    found_sensors = list(filter(lambda s: s.element(use_included=True) is not None,
                                sensors))
    assert len(found_sensors) > 0
    found_sensor = found_sensors[0]
    found_element = found_sensor.element(use_included=True)
    assert found_element is not None

    lost_sensors = list(filter(lambda s: s.element(use_included=True) is None,
                               sensors))
    assert len(lost_sensors) > 0
    lost_sensor = lost_sensors[0]

    # switch to include based relationship
    to_one(Element, type=RelationType.INCLUDE, reverse=to_many)(Sensor)
    # exercise the include based to_one relationship
    assert found_sensor.element() is not None
    assert lost_sensor.element() is None

    found_sensor = Sensor.find(client, found_sensor.id, include=[Element])
    assert found_sensor.element(use_included=True) == found_element

    # try non included
    found_sensor = Sensor.find(client, found_sensor.id)
    with pytest.raises(AttributeError):
        found_sensor.element(use_included=True)
