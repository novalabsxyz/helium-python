"""The root entry point for a client to the Helium API."""

from __future__ import unicode_literals
import requests
from .__about__ import __version__
from .resources import Sensor, Label


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
        """Sets the authentication token for the session

        Args:
            api_token(str): Your Helium API token
        """
        self.headers.update({
            'Authorization': api_token
        })

    def _build_url(self, *args, **kwargs):
        """Builds an API URL"""
        parts = [kwargs.get('base_url', self.base_url)]
        parts.extend(args)
        return '/'.join(parts)


class Client(Session):
    """Construct a client to the Helium API.

    The Client offers up methods to retrieve the "roots" of Helium
    resources such as sensors and label.

    Once resources are retrieved they are attached to the client that
    constructed them and handle further requests independently.

    """
    def all_sensors(self):
        """Iterate over all sensors.

        Returns:
           iterable(Sensor): An iterator over sensor for the authorized api key
        """
        return Sensor.all(self)

    def find_sensor(self, sensor_id):
        """Find a single sensor.

        Args:
           sensor_id(str): The UUID of the sensor to look up
        Returns:
           Sensor: A sensor resource
        """
        return Sensor.find(self, sensor_id)

    def all_labels(self):
        """Iterate over all labels.

        Returns:
           iterable(Label): An iterable over labels for the authorized api key
        """
        return Label.all(self)

    def find_label(self, label_id):
        """Find a single label.

        Args:
           label_id(str): The UUID of the label to look up
        Returns:
           Label: A label resource
        """
        return Label.find(self, label_id)
