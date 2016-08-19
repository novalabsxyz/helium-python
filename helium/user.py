"""The user resource."""

from __future__ import unicode_literals
from . import Resource


class User(Resource):
    """An authorized user of the Helium API.

    A user represents a single developer using the Helium API. Each
    user gets their own API key, which gives them access to all the
    resources in the :class:`Organization` that the user belongs to.

    """

    pass
