"""The Helium Client."""


from __future__ import unicode_literals
from . import Session, Sensor, Label
from . import Organization, User


class Client(Session):
    """Construct a client to the Helium API.

    The Client offers up methods to retrieve the "roots" of Helium
    resources such as sensors and label.

    Once resources are retrieved they are attached to the client that
    constructed them and handle further requests independently.

    """

    def sensors(self):
        """Iterate over all sensors.

        Returns:

           iterable(Sensor): An iterator over sensor for the authorized API key
        """
        return Sensor.all(self)

    def sensor(self, sensor_id):
        """Find a single sensor.

        Args:
           sensor_id(str): The UUID of the sensor to look up
        Returns:
           Sensor: A sensor resource
        """
        return Sensor.find(self, sensor_id)

    def labels(self):
        """Iterate over all labels.

        Returns:

           iterable(Label): An iterable over labels for the authorized API key
        """
        return Label.all(self)

    def label(self, label_id):
        """Find a single label.

        Args:

           label_id(str): The UUID of the label to look up

        Returns:

           Label: A label resource
        """
        return Label.find(self, label_id)

    def authorized_organization(self):
        """Get the authorized organization.

        Returns:

          Organization: The organization for the authorized API key
        """
        return Organization.singleton(self)

    def authorized_user(self):
        """Get the authorized user.

        Returns:

          User: The user for the authorized API key
        """
        return User.singleton(self)
