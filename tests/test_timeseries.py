"""Test for Timeseries."""

from __future__ import unicode_literals
from itertools import islice
from helium import from_iso_date
from datetime import datetime, timedelta
from contextlib import closing


def _feed_timeseries(timeseries, count):
    points = [timeseries.post('test{}'.format(v), v) for v in range(count)]
    return points


def test_iteration(tmp_sensor):
    # construct a timeseries
    timeseries = tmp_sensor.timeseries(page_size=1)
    # post a few data points to it
    posted = _feed_timeseries(timeseries, 2)

    def _paired_datapoints(posted, timeseries):
        datapoints = list(islice(timeseries, 10))
        assert len(datapoints) == len(posted)
        return zip(posted, datapoints)

    def _assert_point(posted, point):
        assert point.id is not None
        assert point.port == posted.port
        assert point.value == posted.value

    for pp, dp in _paired_datapoints(list(reversed(posted)), timeseries):
        # Ensure that the data points arrive in descending time order
        _assert_point(pp, dp)

    # Create a new timeseries that starts at the end and reverses
    timeseries = tmp_sensor.timeseries(page_size=1,
                                       datapoint_id=posted[0].id,
                                       direction='next')
    for pp, dp in _paired_datapoints(posted, timeseries):
        # Ensure that the data points arrive in ascending time order
        _assert_point(pp, dp)


def test_port(tmp_sensor):
    timeseries = tmp_sensor.timeseries()
    dp_foo = timeseries.post('foo', 22)
    timeseries.post('bar', 22)

    timeseries = tmp_sensor.timeseries(port='foo')

    foos = list(islice(timeseries, 10))
    assert len(foos) == 1
    assert foos[0] == dp_foo


def test_start_end(tmp_sensor):
    timeseries = tmp_sensor.timeseries()
    start_date = datetime(2016, 9, 1)

    def _timestamp(day_offset):
        return start_date + timedelta(days=day_offset)

    points = [timeseries.post('test', 22, timestamp=_timestamp(day))
              for day in range(5)]

    timeseries = tmp_sensor.timeseries(start='2016-09-01', end='2016-09-02')
    filter_points = list(timeseries)
    assert filter_points == points[0:1]

    timeseries = tmp_sensor.timeseries(start='2016-09-02', end='2016-09-06')
    filter_points = list(timeseries)
    assert filter_points == list(reversed(points[1:5]))


def test_post(tmp_sensor):
    timeseries = tmp_sensor.timeseries()
    dp = timeseries.post('test', 22)
    assert dp.id is not None
    assert dp.value == 22
    assert dp.port == 'test'
    assert dp.timestamp is not None

    timestamp = datetime(2016, 8, 25)
    dp = timeseries.post('test2', 24, timestamp=timestamp)
    assert from_iso_date(dp.timestamp) == timestamp


def test_live(tmp_sensor):
    assert tmp_sensor is not None

    # We're faking the cassette for a live session pretty hard
    # here. The cassette was manually edited to reflect the
    # event/text-stream data in a single request to work around
    # betamax's problems with dealing with live sockets.
    with closing(tmp_sensor.timeseries().live()) as live:
        live_points = list(islice(live, 10))
        assert len(live_points) == 2
