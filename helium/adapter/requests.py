"""An adapter for the standard blocking requests library."""

from __future__ import unicode_literals, absolute_import

import requests
from collections import Iterable
from json import loads as load_json
from helium.__about__ import __version__


class Live(Iterable):
    """Iterable over a live endpoint."""

    _FIELD_SEPARATOR = ':'

    def __init__(self, response, session, resource_class, resource_args):
        """Construct a live endpoint represented as an Iterable.

        Keyword Args:

            response(Response): The response to a live endpoint request

            session(Session): The session with Helium

            resource_class(Resource): The class of resource to construct
        """
        self._response = response
        self._session = session
        self._resource_class = resource_class
        self._resource_args = resource_args

    def _read(self, response):
        data = ""
        for line in response.iter_lines(decode_unicode=True):
            if not line.strip():
                yield data
                data = ""
            data = data + "\n" + line

    def __iter__(self):
        """Iterate over lines looking for resources."""
        resource_class = self._resource_class
        resource_args = self._resource_args
        session = self._session
        response = self._response

        for chunk in self._read(response):
            event_data = ""
            for line in chunk.splitlines():
                # Ignore empty lines
                if not line.strip():
                    continue

                data = line.split(self._FIELD_SEPARATOR, 1)
                field = data[0]
                data = data[1]

                if field == 'data':
                    event_data += data

            if not event_data:
                # Don't report on events with no data
                continue

            event_data = load_json(event_data).get('data')
            yield resource_class(event_data, session, **resource_args)

    def close(self):
        """Close the live session."""
        self._response.close()


class Adapter(requests.Session):
    """A synchronous adapter based on the `requests` library."""

    def __init__(self):
        """Construct a basic requests session with the Helium API."""
        super(Adapter, self).__init__()
        self.headers.update({
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Content-Type': "application/json",
            'User-Agent': 'helium-python/{0}'.format(__version__)
        })

    @property
    def api_token(self):
        """The API token to use."""
        return self.headers.get('Authorization', None)

    @api_token.setter
    def api_token(self, api_token):
        self.headers.update({
            'Authorization': api_token
        })

    def get(self, url, callback,
            params=None,
            json=None,
            headers=None):  # noqa: D102
        return callback(super(Adapter, self).get(url,
                                                 params=params,
                                                 json=json,
                                                 headers=headers))

    def put(self, url, callback, params=None, json=None):  # noqa: D102
        return callback(super(Adapter, self).put(url,
                                                 params=params,
                                                 json=json))

    def post(self, url, callback, params=None, json=None):  # noqa: D102
        return callback(super(Adapter, self).post(url,
                                                  params=params,
                                                  json=json))

    def patch(self, url, callback, params=None, json=None):  # noqa: D102
        return callback(super(Adapter, self).patch(url,
                                                   params=params,
                                                   json=json))

    def delete(self, url, callback, json=None):  # noqa: D102
        return callback(super(Adapter, self).delete(url, json=json))

    def live(self, session, url, resource_class, resource_args):  # noqa: D102
        response = super(Adapter, self).get(url, stream=True)
        return Live(response, session, resource_class, resource_args)
