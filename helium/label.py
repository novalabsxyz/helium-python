"""The label resource."""

from . import Resource, RelationType, to_many
from . import Sensor


@to_many(Sensor, reverse=to_many, reverse_type=RelationType.INCLUDE)
class Label(Resource):
    pass
