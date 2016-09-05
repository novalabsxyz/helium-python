"""The element resource."""

from __future__ import unicode_literals
from . import Resource, Sensor
from . import RelationType, to_many, timeseries, metadata


@to_many(Sensor, type=RelationType.INCLUDE)
@timeseries()
@metadata()
class Element(Resource):
    pass
