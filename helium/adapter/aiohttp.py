"""An adapter for the standard blocking requests library."""

from __future__ import unicode_literals, absolute_import

import aiohttp

from collections import AsyncIterable, deque
from json import loads as load_json, dumps as dump_json
from helium.__about__ import __version__
from helium.session import Response, CB


class LiveIterator(AsyncIterable):
    """Iterable over a live endpoint."""

    _FIELD_SEPARATOR = ':'

    def __init__(self, response, session, resource_class, resource_args):
        """Construct a live endpoint async iterator.

        Keyword Args:

            response(Response): The response to a live endpoint request

            session(Session): The session with Helium

            resource_class(Resource): The class of resource to construct
        """
        self._response = response
        self._session = session
        self._resource_class = resource_class
        self._resource_args = resource_args

    def __aiter__(self):
        """Create an async iterator."""
        return self

    async def __anext__(self):
        """Iterate over lines looking for resources."""
        resource_class = self._resource_class
        resource_args = self._resource_args
        session = self._session
        response = self._response

        async for line in response.content:
            line = line.decode('utf-8')
            if len(line) == 0 and response.at_eof:
                raise StopAsyncIteration

            if len(line.strip()) > 0:
                field, data = line.split(self._FIELD_SEPARATOR, 1)
                if field.strip() == 'data':
                    json = load_json(data).get('data')
                    return resource_class(json, session, **resource_args)

    def take(self, n):
        """Return the next n datapoints.

        Args:
            n(int): The number of datapoints to retrieve

        Returns:

            A list of at most `n` datapoints.
        """
        return self._session.adapter.take(self, n)

    def close(self):
        """Close the live iterator."""
        self._response.close()

    async def __aenter__(self):
        """Enter context."""
        # Get the actual response
        response = await self._response
        CB.boolean(200)(Response(response.status, response.headers,
                                 response.content, 'GET', response.url))
        self._response = response
        # and enter its' context
        await self._response.__aenter__()
        return self

    async def __aexit__(self, *args):
        """Exit context and close iterator."""
        self.close()
        await self._response.__aexit__(*args)


class DatapointIterator(AsyncIterable):
    """Iterator over a timeseries endpoint."""

    def __init__(self, timeseries, loop=None):
        """Construct an iterator.

        Args:
            timeseries: the timeseries to iterate over

            loop: The asyncio loop to use for iterating

        """
        self.timeseries = timeseries
        self.queue = deque()
        self.continuation_url = timeseries._base_url

    def __aiter__(self):
        """Async iterator over data points in a timeseries."""
        return self

    async def __anext__(self):
        """Return the next datapoint."""
        timeseries = self.timeseries
        session = timeseries._session
        is_aggregate = timeseries._is_aggregate
        if len(self.queue) == 0:
            if self.continuation_url is None:
                raise StopAsyncIteration

            def _process(json):
                data = json.get('data')
                links = json.get('links')
                self.continuation_url = links.get(timeseries._direction, None)
                self.queue.extend(data)
            await session.get(self.continuation_url, CB.json(200, _process),
                              params=timeseries._params)

        if len(self.queue) == 0:
            raise StopAsyncIteration

        json = self.queue.popleft()
        return timeseries._datapoint_class(json, session,
                                           is_aggregate=is_aggregate)


class Adapter(aiohttp.client.ClientSession):
    """A asynchronous adapter based on the `aiohttp` library."""

    def __init__(self, loop=None):
        """Construct a basic requests session with the Helium API."""
        super(Adapter, self).__init__(headers={
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Content-Type': "application/json",
            'User-Agent': 'helium-python/{0}'.format(__version__)
        }, loop=loop)

    @property
    def api_token(self):
        """The API token to use."""
        return self._default_headers.get('Authorization', None)

    @api_token.setter
    def api_token(self, api_token):
        self._default_headers.update({
            'Authorization': api_token
        })

    async def _http(self, callback, method, url,
                    params=None, json=None,
                    headers=None, files=None):
        data = None
        if files:
            data = files
        elif json:
            data = dump_json(json)
        data = files if files else data
        async with self.request(method, url,
                                params=params,
                                headers=headers,
                                data=data) as response:
            body = await response.text(encoding='utf-8')
            return callback(Response(response.status, response.headers, body,
                                     method, url))

    def get(self, url, callback,
            params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'GET', url,
                          params=params,
                          json=json,
                          headers=headers)

    def put(self, url, callback,
            params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'PUT', url,
                          params=params, json=json, headers=headers)

    def post(self, url, callback,
             params=None, json=None, headers=None,
             files=None):  # noqa: D102
        return self._http(callback, 'POST', url,
                          params=params, json=json, headers=headers,
                          files=files)

    def patch(self, url, callback,
              params=None, json=None, headers=None):  # noqa: D102
        return self._http(callback, 'PATCH', url,
                          params=params, json=json, headers=headers)

    def delete(self, url, callback, json=None):  # noqa: D102
        return self._http(callback, 'DELETE', url,
                          json=json)

    def live(self, session, url,
             resource_class, resource_args,
             params=None):  # noqa: D102
        headers = {
            'Accept': 'text/event-stream',
        }
        response = super(Adapter, self).get(url,
                                            read_until_eof=False,
                                            params=params,
                                            headers=headers)
        return LiveIterator(response, session, resource_class, resource_args)

    def datapoints(self, timeseries):  # noqa: D102
        return DatapointIterator(timeseries)

    async def take(self, aiter, n):  # noqa: D102
        result = []
        if n == 0:
            return result
        async for entry in aiter:
            result.append(entry)
            n -= 1
            if n == 0:
                break
        return result
