"""The organization resource."""

from . import Resource, to_many, to_one
from . import User, Metadata


@to_many(User, singleton=True)
@to_one(Metadata, singleton=True)
class Organization(Resource):
    @classmethod
    def authorized(cls, session):
        url = session._build_url(cls._resource_type())
        json = cls._json(session.get(url), 200)
        return cls(json, session)
