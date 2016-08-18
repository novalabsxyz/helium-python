"""The element resource."""

from __future__ import unicode_literals
from . import Resource, Sensor, Metadata
from . import to_one, to_many, timeseries


@to_one(Metadata)
@to_many(Sensor)
@timeseries()
class Element(Resource):
    pass
