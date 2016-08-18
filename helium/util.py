"""Utility functions."""

from __future__ import unicode_literals

from .exceptions import error_for
from datetime import datetime


def response_boolean(response, true_code):
    if response is not None:
        status_code = response.status_code
        if status_code == true_code:
            return True
        raise error_for(response)


def response_json(response, status_code, extract='data'):
    ret = None
    if response_boolean(response, status_code) and response.content:
        ret = response.json()
        if extract is not None:
            ret = ret.get(extract)
    return ret


def from_iso_date(str):
    try:
        return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(str, "%Y-%m-%dT%H:%M:%SZ")


def to_iso_date(timestamp):
    return timestamp.isoformat() + (timestamp.tzname() or 'Z')


def build_resource_attributes(type, id, attributes):
    result = {
        "data": {
            "attributes": attributes,
            "type": type
        }
    }
    if id is not None:
        result['data']['id'] = id
    return result


def build_resource_relationship(type, ids):
    return {
        "data": [{"id": id, "type": type} for id in ids]
    }
