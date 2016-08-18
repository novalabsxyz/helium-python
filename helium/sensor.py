"""The sensor resource."""

from __future__ import unicode_literals
from . import Resource
from . import timeseries


@timeseries()
class Sensor(Resource):
    pass
