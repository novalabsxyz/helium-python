"""The element resource."""

from __future__ import unicode_literals
from . import Resource, Sensor
from . import to_many, timeseries, metadata


@to_many(Sensor)
@timeseries()
@metadata()
class Element(Resource):
    pass
