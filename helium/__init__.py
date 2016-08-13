"""The public interface to the helium-python library."""

from __future__ import unicode_literals
from .exceptions import (
    Error, ClientError, ServerError, NotFoundError,
)
from .resource import Resource
from .relations import RelationType, to_many, to_one
from .user import User
from .sensor import Sensor
from .metadata import Metadata
from .label import Label
from .element import Element
from .organization import Organization
from .session import Session, Client
from .__about__ import (
    __package_name__, __title__, __author__, __author_email__,
    __license__, __copyright__, __version__, __version_info__,
    __url__,
)

__all__ = (
    Error,
    ServerError,
    ClientError,
    NotFoundError,
    Session,
    Client,
    Resource, to_one, to_many, RelationType,
    Organization,
    User,
    Sensor,
    Metadata,
    Element,
    Label,
    # Metadata attributes
    '__package_name__',
    '__title__',
    '__author__',
    '__author_email__',
    '__license__',
    '__copyright__',
    '__version__',
    '__version_info__',
    '__url__',
)
