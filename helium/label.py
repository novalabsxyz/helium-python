"""The label resource."""

from __future__ import unicode_literals
from . import (
    Resource,
    Sensor,
    Element,
    to_many,
    timeseries,
    metadata,
    build_request_relationship
)


@to_many(Sensor, writable=True, reverse=to_many)
@to_many(Element, writable=True, reverse=to_many)
@timeseries()
@metadata()
class Label(Resource):
    @classmethod
    def create(cls, session, attributes=None,
               sensors=None, elements=None, **kwargs):

        def _relate_resources(name, type, resources):
            if resources is None:
                return
            relationships = kwargs.setdefault('relationships', {})
            resource_ids = [r.id for r in resources]
            relationships[name] = build_request_relationship(type,
                                                             resource_ids)
        _relate_resources('sensor', 'sensor', sensors)
        _relate_resources('element', 'element', elements)

        return super(Label, cls).create(session,
                                        attributes=attributes,
                                        **kwargs)
