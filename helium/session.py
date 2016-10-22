"""The root entry point for a client to the Helium API."""

from __future__ import unicode_literals
from .exceptions import error_for


class CB(object):
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
                status_code = response.status_code
                if status_code == true_code:
                    return True
                if false_code is not None and status_code == false_code:
                    return False
                raise error_for(response)
        return func

    @classmethod
    def json(cls, status_code, extract='data'):
        """Callback to validate and extract a JSON object.

        The returned callback checks a given response for the given
        status_code using :function:`respnse_boolean`. On success the
        response JSON is extracted and the optional ``extract``
        attribute from the top level JSON object is returned.

        Args:

            status_code(int): The http status code to consider a success

        Keywords Args:

            extract(string): The optional JSON attribute to extract from the
                response JSON

        Returns:

            A function that given a response returns the JSON object
                in the given response or the ``extract``ed attribute
                from that response. Raises a :class:`HeliumError` if
                the response code does not match.

        """
        def func(response):
            ret = None
            if cls.boolean(status_code)(response) and response.content:
                ret = response.json()
                if extract is not None:
                    ret = ret.get(extract)
            return ret
        return func


class Session(object):
    """Construct a session with the Helium API.

    This sets up the correct headers, content-types and
    authentication, if provided

    Keyword Args:
        api_token: Your Helium API Token
        base_url: The base URL to the Helium API
    """

    def __init__(self,
                 adapter=None,
                 api_token=None,
                 base_url='https://api.helium.com/v1'):
        super(Session, self).__init__()
        if adapter is None:
            from helium.adapter.requests import Adapter
            self.adapter = Adapter()
        else:
            self.adapter = adapter
        self.base_url = base_url
        if api_token:
            self.api_token = api_token

    @property
    def api_token(self):
        return self.adapter.api_token

    @api_token.setter
    def api_token(self, api_token):
        self.adapter.api_token = api_token

    def get(self, url, callback, params=None, json=None,
            stream=False, headers=None):
        return self.adapter.get(url, callback,
                                params=params,
                                json=json,
                                headers=headers)

    def put(self, url, callback, params=None, json=None):
        return self.adapter.put(url, callback, params=params, json=json)

    def post(self, url, callback, params=None, json=None):
        return self.adapter.post(url, callback, params=params, json=json)

    def patch(self, url, callback, params=None, json=None):
        return self.adapter.patch(url, callback,
                                  params=params,
                                  json=json)

    def delete(self, url, callback, json=None):
        return self.adapter.delete(url, callback, json=json)

    def live(self, url, resource_class, resource_args):
        return self.adapter.live(self, url, resource_class, resource_args)

    def _build_url(self, *args, **kwargs):
        parts = [kwargs.get('base_url', self.base_url)]
        parts.extend([part for part in args if part is not None])
        return '/'.join(parts)
