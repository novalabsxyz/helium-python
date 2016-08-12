"""The user resource."""

from . import Resource


class User(Resource):
    @classmethod
    def authorized(cls, session):
        url = session._build_url(cls._resource_type())
        json = cls._json(session.get(url), 200)
        return cls(json, session)
