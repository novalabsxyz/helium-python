"""An adapter for the standard blocking requests library."""

from __future__ import unicode_literals, absolute_import

import requests
from collections import Iterable, Iterator, deque
from json import loads as load_json
from helium.__about__ import __version__
from helium.session import Response, CB
from itertools import islice


class LiveIterator(Iterable):
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
        for line in response.iter_lines(decode_unicode=True):
            yield line

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

    def take(self, n):
        """Return the next n datapoints.

        Args:
            n(int): The number of datapoints to retrieve

        Returns:

            A list of at most `n` datapoints.
        """
        return self._session.adapter.take(self, n)

    def close(self):
        """Close the live session."""
        self._response.close()

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, *args):
        """Exit context."""
        self.close()
        return False


class DatapointIterator(Iterator):
    """Iterator over a timeseries endpoint."""

    def __init__(self, timeseries):
        """Construct an iterator.

        Args:
            timeseries: the timeseries to iterate over

            loop: The asyncio loop to use for iterating

        """
        self.timeseries = timeseries
        self.queue = deque()
        self.continuation_url = timeseries._base_url

    def __iter__(self):
        """Iterator for data points in a timeseries."""
        return self  # pragma: no cover

    def __next__(self):
        """Return the next data point."""
        timeseries = self.timeseries
        session = timeseries._session
        is_aggregate = timeseries._is_aggregate

        if len(self.queue) == 0:
            if self.continuation_url is None:
                raise StopIteration

            def _process(json):
                data = json.get('data')
                links = json.get('links')
                self.continuation_url = links.get(timeseries._direction, None)
                self.queue.extend(data)
            session.get(self.continuation_url, CB.json(200, _process),
                        params=timeseries._params)

        if len(self.queue) == 0:
            raise StopIteration

        json = self.queue.popleft()
        return timeseries._datapoint_class(json, session,
                                           is_aggregate=is_aggregate)

    def next(self):
        """Python 2 iterator compatibility."""
        # We remove coverage here to pacify coverage since this method
        # used in python 2.7 but no longer in python 3.5
        return self.__next__()  # pragma: no cover


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

    def _http(self, callback, method, url,
              params=None, json=None, headers=None, files=None):
        response = super(Adapter, self).request(method, url,
                                                params=params,
                                                json=json,
                                                headers=headers,
                                                files=files)
        if not response.encoding:
            response.encoding = 'utf8'
        body = response.text
        request = response.request
        return callback(Response(response.status_code, response.headers, body,
                                 request.method, request.url))

    def get(self, url, callback,
            params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'GET', url,
                          params=params,
                          headers=headers,
                          json=json)

    def put(self, url, callback,
            params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'PUT', url,
                          params=params, json=json, headers=headers)

    def post(self, url, callback,
             params=None, json=None, headers=None, files=None):  # noqa: D102
        return self._http(callback, 'POST', url,
                          params=params, json=json, headers=headers,
                          files=files)

    def patch(self, url, callback,
              params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'PATCH', url,
                          params=params, json=json, headers=headers)

    def delete(self, url, callback, json=None):  # noqa: D102
        return self._http(callback, 'DELETE', url, json=json)

    def datapoints(self, timeseries):   # noqa: D102
        return DatapointIterator(timeseries)

    def take(self, iter, n):   # noqa: D102
        return list(islice(iter, n))

    def live(self, session, url, resource_class, resource_args, params=None):  # noqa: D102
        headers = {
            'Accept': 'text/event-stream',
        }
        response = super(Adapter, self).get(url,
                                            stream=True,
                                            headers=headers,
                                            params=params)
        # Validate the response code
        CB.boolean(200)(Response(response.status_code, response.headers, None,
                                 response.request.method, url))
        return LiveIterator(response, session, resource_class, resource_args)
