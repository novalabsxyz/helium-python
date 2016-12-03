"""The sensor resource."""

from __future__ import unicode_literals
from . import Device
from . import timeseries, metadata


@timeseries()
@metadata()
class Sensor(Device):
    pass
