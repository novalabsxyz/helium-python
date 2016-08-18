"""The sensor resource."""

from __future__ import unicode_literals
from . import Resource, Metadata
from . import to_one, timeseries


@to_one(Metadata)
@timeseries()
class Sensor(Resource):
    pass
