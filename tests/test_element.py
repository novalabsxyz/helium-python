from __future__ import unicode_literals


def test_elements(elements, first_element):
    assert len(elements) > 0
    assert first_element.id is not None


def timeseries(first_element):
    timeseries = first_element.timeseries()
    assert timeseries is not None


def test_metadata(first_element):
    metadata = first_element.metadata()
    assert metadata is not None


def test_meta(first_element):
    assert first_element.meta is not None
