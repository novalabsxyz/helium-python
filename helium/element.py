"""The element resource."""

from __future__ import unicode_literals
from . import Resource, Sensor
from . import RelationType, to_many, to_one
from . import timeseries, metadata


@to_many(Sensor, type=RelationType.INCLUDE, reverse=to_one)
@timeseries()
@metadata()
class Element(Resource):
    pass
