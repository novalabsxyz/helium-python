"""The element resource."""

from __future__ import unicode_literals
from . import Device, Sensor
from . import RelationType, to_many, to_one
from . import timeseries, metadata


@to_many(Sensor, type=RelationType.INCLUDE,
         reverse=to_one, reverse_type=RelationType.DIRECT)
@timeseries()
@metadata()
class Element(Device):
    pass
