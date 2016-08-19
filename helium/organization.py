"""The organization resource."""

from __future__ import unicode_literals
from . import Resource, User
from . import to_many, to_one, timeseries, metadata


@to_many(User, reverse=to_one)
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
