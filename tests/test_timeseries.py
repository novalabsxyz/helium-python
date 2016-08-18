"""Test for Timeseries."""

from __future__ import unicode_literals
from itertools import islice
from datetime import datetime


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


def test_post(tmp_sensor):
    timeseries = tmp_sensor.timeseries()
    dp = timeseries.post('test', 22)
    assert dp.id is not None
    assert dp.value == 22
    assert dp.port == 'test'
    assert isinstance(dp.timestamp, datetime)

    timestamp = datetime(2016, 8, 25)
    dp = timeseries.post('test2', 24, timestamp=timestamp)
    assert dp.timestamp == timestamp
