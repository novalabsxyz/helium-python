"""The element resource."""

from . import Resource, RelationType, to_many
from . import Sensor


@to_many(Sensor)
class Element(Resource):
    pass
