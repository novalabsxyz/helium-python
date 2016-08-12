"""The element resource."""

from __future__ import unicode_literals
from . import Resource, to_many
from . import Sensor


@to_many(Sensor)
class Element(Resource):
    pass
