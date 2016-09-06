"""Utility functions."""

from __future__ import unicode_literals

from .exceptions import error_for
from datetime import datetime


def response_boolean(response, true_code, false_code=None):
    """Validate a response code.

    Checks whether the given response has a ``status_code`` that is
    considered good (``true_code``) and raise an appropriate error if
    not.

    The optional ``false_code`` allows for a non-successful status
    code to return False instead of throwing an error. This is used,
    for example in relationship mutation to indicate that the
    relationship was not modified.

    Args:

        response(Response): A :class:`requests.Response` to validate

        true_code(int): The http status code to consider as a success

    Keyword Args:

        false_code(int): The http status code to consider a failure

    Returns:

        ``True`` if the response's status code matches the given
            code. Raises a :class:`HeliumError` if the response code
            does not match.

    """
    if response is not None:
        status_code = response.status_code
        if status_code == true_code:
            return True
        if false_code is not None and status_code == false_code:
            return False
        raise error_for(response)


def response_json(response, status_code, extract='data'):
    """Validate and extract a JSON object.

    Checks the given response for the given status_code using
    :function:`respnse_boolean`. On success the response JSON is
    extracted and the optional ``extract`` attribute from the top
    level JSON object is returned.

    Args:

        response(Response): A :class:`requests.Response` to parse
        status_code(int): The http status code to consider a success

    Keywords Args:

        extract(string): The optional JSON attribute to extract from the
            response JSON

    Returns:

        The JSON object in the given response or the ``extract``ed
        attribute from that response. Raises a :class:`HeliumError` if
        the response code does not match.

    """
    ret = None
    if response_boolean(response, status_code) and response.content:
        ret = response.json()
        if extract is not None:
            ret = ret.get(extract)
    return ret


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


def build_request_attributes(type, id, attributes):
    """Build a resource attributes object.

    A resource attributes JSON object is used for any of the
    ``update`` methods on :class:`Resource` subclasses. In normal
    library use you should not have to use this function directly.

    Args:

        type(string): The resource type for the attribute
        id(uuid): The id of the object to update. This may be ``None``
        attributes(dict): A JSON dictionary of the attributes to set

    Returns:

        A valid attribute dictionary. Often used in the ``update`` or
            ``create`` :class:`Resource`` methods.

    """
    result = {
        "data": {
            "attributes": attributes,
            "type": type
        }
    }
    if id is not None:
        result['data']['id'] = id
    return result


def build_request_relationship(type, ids):
    """Build a relationship list.

    A relationship list is used to update relationships between two
    resources. Setting sensors on a label, for example, uses this
    function to construct the list of sensor ids to pass to the Helium
    API.

    Args:

        type(string): The resource type for the ids in the relationship
        ids([uuid]): The list of resource uuids to use in the relationship

    Returns:

        A ready to use relationship JSON object.

    """
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
    params = params or {}
    if include is not None:
        params['include'] = ','.join([cls._resource_type() for cls in include])
    return params
