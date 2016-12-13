"""Utility functions."""

from __future__ import unicode_literals

from datetime import datetime
from collections import OrderedDict
from builtins import str


def from_iso_date(str):
    """Convert an ISO8601 to a datetime.

    Args:

       str(string): The ISO8601 formatted string to convert

    Returns:

       A :class:`datetime` object representing the given time
    """
    try:
        return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(str, "%Y-%m-%dT%H:%M:%SZ")


def to_iso_date(timestamp):
    """Convert a UTC timestamp to an ISO8601 string.

    datetime instances can be constructed in alternate timezones. This
    function assumes that the given timestamp is in the UTC timezone.

    Args:

        timestamp(datetime): A datetime object in the UTC timezone.

    Returns:

        An ISO8601 formatted string representing the timestamp.

    """
    return timestamp.isoformat() + 'Z'


def build_request_body(type, id, attributes=None, relationships=None):
    """Build a request body  object.

    A body JSON object is used for any of the ``update`` or ``create``
    methods on :class:`Resource` subclasses. In normal library use you
    should not have to use this function directly.

    Args:

        type(string): The resource type for the attribute
        id(uuid): The id of the object to update. This may be ``None``

    Keyword Args:

        attributes(dict): A JSON dictionary of the attributes to set
        relationships(dict) A JSON dictionary of relationships to set

    Returns:

        A valid attribute dictionary. Often used in the ``update`` or
            ``create`` :class:`Resource`` methods.

    """
    result = {
        "data": {
            "type": type
        }
    }
    data = result['data']
    if attributes is not None:
        data['attributes'] = attributes
    if relationships is not None:
        data['relationships'] = relationships
    if id is not None:
        data['id'] = id
    return result


def build_request_relationship(type, ids):
    """Build a relationship list.

    A relationship list is used to update relationships between two
    resources. Setting sensors on a label, for example, uses this
    function to construct the list of sensor ids to pass to the Helium
    API.

    Args:

        type(string): The resource type for the ids in the relationship
        ids([uuid] or uuid): Just one or a list of resource uuids to use
            in the relationship

    Returns:

        A ready to use relationship JSON object.

    """
    if ids is None:
        return {
            'data': None
        }
    elif isinstance(ids, str):
        return {
            'data': {'id': ids, 'type': type}
        }
    else:
        return {
            "data": [{"id": id, "type": type} for id in ids]
        }


def build_request_include(include, params):
    """Augment request parameters with includes.

    When one or all resources are requested an additional set of
    resources can be requested as part of the request. This function
    extends the given parameters for a request with a list of resource
    types passed in as a list of :class:`Resource` subclasses.

    Args:

        include([Resource class]): A list of resource classes to include

        params(dict): The (optional) dictionary of request parameters to extend

    Returns:

        An updated or new dictionary of parameters extended with an
        include query parameter.

    """
    params = params or OrderedDict()
    if include is not None:
        params['include'] = ','.join([cls._resource_type() for cls in include])
    return params
