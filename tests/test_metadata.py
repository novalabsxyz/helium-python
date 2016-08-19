"""Test for Metadata."""

from __future__ import unicode_literals


def test_update(tmp_sensor):
    metadata = tmp_sensor.metadata()
    assert metadata is not None

    updated = metadata.update(foo='bar', baz={'key': 'value'})
    assert updated.foo == 'bar'
    assert updated.baz == {'key': 'value'}


def test_replace(tmp_sensor):
    metadata = tmp_sensor.metadata()
    updated = metadata.update(foo=22)
    assert updated.foo == 22

    updated = metadata.replace(bar=42)
    assert updated is not None
    assert not hasattr(updated, 'foo')
    assert updated.bar == 42
