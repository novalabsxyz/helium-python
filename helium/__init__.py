"""The public interface to the helium-python library."""

from __future__ import unicode_literals
from .exceptions import (
    Error, ClientError, ServerError, NotFoundError,
)
from .util import (
    from_iso_date, to_iso_date,
    build_request_body, build_request_relationship,
    build_request_include,
)
from .session import Session, CB
from .resource import Base, Resource, ResourceMeta
from .relations import RelationType, to_many, to_one
from .metadata import Metadata, metadata
from .user import User
from .timeseries import Timeseries, DataPoint, AggregateValue, timeseries
from .device import Device
from .sensor import Sensor
from .element import Element
from .configuration import Configuration
from .device_configuration import DeviceConfiguration
from .label import Label
from .organization import Organization
from .client import Client
from .__about__ import (
    __package_name__, __title__, __author__, __author_email__,
    __license__, __copyright__, __version__, __revision__,
    __url__,
)

__all__ = (
    'from_iso_date', 'to_iso_date',
    'build_request_body', 'build_request_relationship',
    'build_request_include',
    'Error',
    'ServerError',
    'ClientError',
    'NotFoundError',
    'Base', 'Resource', 'ResourceMeta',
    'RelationType', 'to_one', 'to_many',
    'Session', 'CB',
    'Organization',
    'User',
    'Timeseries', 'DataPoint', 'timeseries', 'AggregateValue',
    'DeviceConfiguration', 'Configuration', 'Device',
    'Sensor',
    'Metadata', 'metadata',
    'Element',
    'Label',
    'Client',
    # Metadata attributes
    '__package_name__',
    '__title__',
    '__author__',
    '__author_email__',
    '__license__',
    '__copyright__',
    '__version__',
    '__revision__',
    '__url__',
)
