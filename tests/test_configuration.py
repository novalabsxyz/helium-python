"""Tests for Configuration."""

from __future__ import unicode_literals
from helium import Configuration


def test_create(client):
    config = Configuration.create(client, attributes={
        'test': 42
    })
    assert config.test == 42

    fetch = Configuration.find(client, config.id)
    assert fetch == config

    assert config.delete()


def test_device_configuration(tmp_configuration):
    device_configs = tmp_configuration.device_configurations()
    assert len(device_configs) == 0
