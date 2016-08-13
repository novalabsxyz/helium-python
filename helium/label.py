"""The label resource."""

from __future__ import unicode_literals
from . import Resource, RelationType, to_many
from . import Sensor


@to_many(Sensor, writable=True,
         reverse=to_many,
         reverse_type=RelationType.INCLUDE)
class Label(Resource):
    @classmethod
    def create(cls, session, **kwargs):
        sensors = kwargs.pop('sensors', None)
        label = super(Label, cls).create(session, **kwargs)
        if sensors is not None:
            label.update_sensors(sensors)
        return label
