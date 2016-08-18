"""The root entry point for a client to the Helium API."""

from __future__ import unicode_literals
import requests
from .__about__ import __version__


class Session(requests.Session):
    """Construct a basic session with the Helium API.

    This sets up the correct headers, content-types and
    authentication, if provided

    Keyword Args:
        api_token: Your Helium API Token
        base_url: The base URL to the Helium API
    """

    def __init__(self, api_token=None, base_url='https://api.helium.com/v1'):
        super(Session, self).__init__()
        self.headers.update({
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Content-Type': "application/json",
            'User-Agent': 'helium-python/{0}'.format(__version__)
        })
        self.base_url = base_url
        if api_token:
            self.token_auth(api_token)

    def token_auth(self, api_token):
        """Set the authentication token for the session.

        Args:
            api_token(str): Your Helium API token
        """
        self.headers.update({
            'Authorization': api_token
        })

    def _build_url(self, *args, **kwargs):
        parts = [kwargs.get('base_url', self.base_url)]
        parts.extend([part for part in args if part is not None])
        return '/'.join(parts)
