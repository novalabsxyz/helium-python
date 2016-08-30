"""The organization resource."""

from __future__ import unicode_literals
from . import Resource, Sensor, User, Element
from . import to_many, timeseries, metadata


@to_many(User)
@to_many(Element)
@to_many(Sensor)
@timeseries()
@metadata()
class Organization(Resource):
    """The top level owner of resources.

    An organization represents container for all the sensors, elements
    and labels that you own.

    All :class:`User` resources in an organization have access to all
    resources in an organization.

    """

    pass
