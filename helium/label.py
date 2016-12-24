"""The label resource."""

from __future__ import unicode_literals
from . import (
    Resource,
    Sensor,
    to_many,
    timeseries,
    metadata,
    build_request_relationship
)


@to_many(Sensor, writable=True, reverse=to_many)
@timeseries()
@metadata()
class Label(Resource):
    @classmethod
    def create(cls, session,
               attributes=None, sensors=None, **kwargs):
        if sensors is not None:
            relationships = kwargs.setdefault('relationships', {})
            sensor_ids = [r.id for r in sensors]
            relationships['sensor'] = build_request_relationship('sensor',
                                                                 sensor_ids)

        return super(Label, cls).create(session,
                                        attributes=attributes,
                                        **kwargs)
