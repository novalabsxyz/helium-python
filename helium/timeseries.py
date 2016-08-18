"""Helium Timeseries functionality."""

from __future__ import unicode_literals

from . import Resource, response_json
from . import from_iso_date, to_iso_date
from . import build_resource_attributes
from collections import Iterable


class DataPoint(Resource):

    def _promote_json_attribute(self, attribute, value):
        if attribute == 'timestamp':
            value = from_iso_date(value)
        return super(DataPoint, self)._promote_json_attribute(attribute, value)


class Timeseries(Iterable):
    def __init__(self, session, resource_type, resource_id,
                 datapoint_class=DataPoint,
                 datapoint_id=None,
                 page_size=None,
                 direction='prev'):
        self._session = session
        self._datapoint_class = datapoint_class
        self._base_url = session._build_url(resource_type,
                                            resource_id,
                                            'timeseries')
        self._resource_type = resource_type
        self._resource_id = resource_id
        self._direction = direction

        params = {}
        if datapoint_id is not None:
            params['page[id]'] = datapoint_id
        if page_size is not None:
            params['page[size]'] = page_size
        self._params = params

    def __iter__(self):
        session = self._session
        datapoint_class = self._datapoint_class
        direction = self._direction
        params = self._params

        def _get_json(url):
            json = response_json(session.get(url, params=params), 200,
                                 extract=None)
            data = json.get('data')
            link = json.get('links')
            link = link.get(direction)
            return (json, data, link)

        json, data, url = _get_json(self._base_url)

        finished = False
        while not finished:
            for entry in data:
                datapoint = datapoint_class(entry, session)
                yield datapoint

            if url is None:
                finished = True
            else:
                json, data, url = _get_json(url)

    def post(self, port, value, timestamp=None):
        session = self._session
        datapoint_class = self._datapoint_class
        attributes = {
            'port': port,
            'value': value,
        }
        if timestamp is not None:
            attributes['timestamp'] = to_iso_date(timestamp)
        attributes = build_resource_attributes('data-point', None, attributes)
        data = session.post(self._base_url, json=attributes)
        return datapoint_class(response_json(data, 201), session)


def timeseries():
    def method_builder(cls):
        def method(self, **kwargs):
            resource_id = None if hasattr(self, '_singleton') else self.id
            return Timeseries(self._session, cls._resource_type(), resource_id,
                              **kwargs)
        setattr(cls, 'timeseries', method)
        return cls
    return method_builder
