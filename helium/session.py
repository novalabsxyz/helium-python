"""The root entry point for a client to the Helium API."""

from __future__ import unicode_literals
from .exceptions import error_for
from collections import namedtuple
from json import loads as load_json


class Response(namedtuple('Response', ['status', 'headers', 'body',
                                       'request_method', 'request_url'])):
    __slots__ = ()

    def json(self):
        return load_json(self.body)


class CB(object):
    """Convenience callback functions for sessions.

    This class offers up convenience callback builders that make it
    easy to use the callback session API to behave like a synchronous
    API.

    """

    @classmethod
    def boolean(cls, true_code, false_code=None):
        """Callback to validate a response code.

        The returned callback checks whether a given response has a
        ``status_code`` that is considered good (``true_code``) and
        raise an appropriate error if not.

        The optional ``false_code`` allows for a non-successful status
        code to return False instead of throwing an error. This is used,
        for example in relationship mutation to indicate that the
        relationship was not modified.

        Args:

            true_code(int): The http status code to consider as a success

        Keyword Args:

            false_code(int): The http status code to consider a failure

        Returns:

            A function that given a response returns ``True`` if the
                response's status code matches the given code. Raises
                a :class:`HeliumError` if the response code does not
                match.

        """
        def func(response):
            if response is not None:
                status_code = response.status
                if status_code == true_code:
                    return True
                if false_code is not None and status_code == false_code:
                    return False
                raise error_for(response)
        return func

    @classmethod
    def json(cls, status_code, process):
        """Callback to validate and extract a JSON object.

        The returned callback checks a given response for the given
        status_code using :function:`response_boolean`. On success the
        response JSON is parsed and returned.

        Args:

            status_code(int): The http status code to consider a success

        Returns:

            A function that given a response returns the JSON object
                in the given response. Raises a :class:`HeliumError` if
                the response code does not match.

        """
        def func(response):
            ret = None
            if cls.boolean(status_code)(response):
                ret = response.json() or {}
            return process(ret)
        return func


class Session(object):
    """Manages a session with Helium Service.

    A session with the Helium service. A session is mostly a front for
    an underlying adapter that implements the details of requesting
    and handling the responses. Using the adapters allows the use of
    different syncrhonous and asynchronous approaches. The default
    adapter is a synchronous `requests` based adapter.

    """

    def __init__(self,
                 adapter=None,
                 api_token=None,
                 base_url='https://api.helium.com/v1'):
        """Construct a session with the Helium API.

        This sets up the correct headers, content-types and
        authentication, if provided

        Keyword Args:
            adapter: The adapter to use for requests
            api_token: Your Helium API Token
            base_url: The base URL to the Helium API
        """
        super(Session, self).__init__()
        self.adapter = adapter
        if self.adapter is None:
            from helium.adapter.requests import Adapter
            self.adapter = Adapter()
        self.base_url = base_url
        if api_token:
            self.api_token = api_token

    @property
    def api_token(self):
        """The API token for to use for this session."""
        return self.adapter.api_token

    @api_token.setter
    def api_token(self, api_token):
        self.adapter.api_token = api_token

    def get(self, url, callback,
            params=None, json=None, headers=None):
        """Get a URL.

        Args:

            callback(func): The response callback function

        Keyword Args:

            params(dict): Parameters for the request

            json(dict): JSON body for the request

            headers(dict): Additional headers for the request

        Returns:

            The result of the callback handling the resopnse from the
                executed request

        """
        return self.adapter.get(url, callback,
                                params=params, json=json, headers=headers)

    def put(self, url, callback,
            params=None, json=None, headers=None):
        """Put to a URL.

        Args:

            url(string): URL for the request

            callback(func): The response callback function

        Keyword Args:

            params(dict): Parameters for the request

            json(dict): JSON body for the request

            headers(dict): HTTP headers for the request

        Returns:

            The result of the callback handling the resopnse from the
                executed request

        """
        return self.adapter.put(url, callback, params=params, json=json)

    def post(self, url, callback,
             params=None, json=None, headers=None, files=None):
        """Post to a URL.

        Args:

            url(string): URL for the request

            callback(func): The response callback function

            headers(dict): HTTP headers for the request

        Keyword Args:

            params(dict): Parameters for the request

            json(dict): JSON body for the request

        Returns:

            The result of the callback handling the resopnse from the
                executed request

        """
        return self.adapter.post(url, callback,
                                 params=params, json=json,
                                 headers=headers, files=files)

    def patch(self, url, callback,
              params=None, json=None, headers=None):
        """Patch a URL.

        Args:

            url(string): URL for the request

            callback(func): The response callback function

            headers(dict): HTTP headers for the request

        Keyword Args:

            params(dict): Parameters for the request

            json(dict): JSON body for the request

        Returns:

            The result of the callback handling the resopnse from the
                executed request

        """
        return self.adapter.patch(url, callback,
                                  params=params, json=json, headers=headers)

    def delete(self, url, callback, json=None):
        """Delete a URL.

        Args:

            url(string): URL for the request

            callback(func): The response callback function

        Keyword Args:

            json(dict): JSON body for the request

        Returns:

            The result of the callback handling the resopnse from the
                executed request

        """
        return self.adapter.delete(url, callback, json=json)

    def datapoints(self, timeseries):
        return self.adapter.datapoints(timeseries)

    def live(self, url, resource_class, resource_args, params=None):
        """Get a live endpoint.

        Args:

            url(string): URL for the request

            resource_class(class): The class to use for entries coming
                from the live endpoint.

            resource_args(dict): Additional arguments to pass to the
                `resource_class` constructor

        Keyword Args:

            params(dict): Request parameters for the live url

        Returns:

            An iterator over the live endpoint. Depending on the
                adapter the iterator will allow asynchronous
                behavior. The default adapter will block while
                iterating over the response of this method.

        """
        return self.adapter.live(self, url, resource_class, resource_args,
                                 params=params)

    def _build_url(self, *args, **kwargs):
        parts = [kwargs.get('base_url', self.base_url)]
        parts.extend([part for part in args if part is not None])
        return '/'.join(parts)
