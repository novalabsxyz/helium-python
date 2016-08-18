"""The organization resource."""

from __future__ import unicode_literals
from . import Resource, to_many, to_one
from . import User, Metadata
from . import timeseries


@to_many(User)
@to_one(Metadata)
@timeseries()
class Organization(Resource):
    """The top level owner of resources.

    An organization represents container for all the sensors, elements
    and labels that you own.

    All :class:`User` resources in an organization have access to all
    resources in an organization.

    """
    pass
