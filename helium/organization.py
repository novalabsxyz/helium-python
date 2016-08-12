"""The organization resource."""

from __future__ import unicode_literals
from . import Resource, to_many, to_one
from . import User, Metadata


@to_many(User)
@to_one(Metadata)
class Organization(Resource):
    pass
