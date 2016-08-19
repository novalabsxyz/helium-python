"""The sensor resource."""

from __future__ import unicode_literals
from . import Resource
from . import timeseries, metadata


@timeseries()
@metadata()
class Sensor(Resource):
    pass
