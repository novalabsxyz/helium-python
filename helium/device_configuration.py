"""A device-configuration resource."""

from __future__ import unicode_literals
from . import Resource, Configuration
from . import Device, Sensor, Element
from . import to_one, to_many, build_request_relationship


@to_one(Configuration, reverse=to_many)
@to_one(Device, resource_classes=[Element, Sensor], reverse=to_many)
class DeviceConfiguration(Resource):
    """Association between a device and a configuration.

    A device configuration is the association between a device and a
    `Configuration`.

    """

    @classmethod
    def _resource_type(cls):
        return 'device-configuration'

    @classmethod
    def create(cls, session, device=None, configuration=None, **kwargs):
        """Create a device configuration.

        Create a device configuration with the given device and
        configuration.

        Args:

            session(Session): The session to use for the request

        Keyword Args:

            device(Device): The device to configure, such as an
                `Element` or a `Sensor`

            configuration(Configuration): The configuration to apply
                to the device.

        Returns:

            The created device configuration. Throws an exception if
            any failure occurs.

        """
        rels = kwargs.setdefault('relationships', {})
        if configuration is not None:
            rel = build_request_relationship(configuration._resource_type(),
                                             configuration.id)
            rels['configuration'] = rel

        if device is not None:
            rel = build_request_relationship(device._resource_type(),
                                             device.id)
            rels['device'] = rel

        return super(DeviceConfiguration, cls).create(session,
                                                      **kwargs)

    def is_loaded(self):
        """Check is a device configuration is loaded.

        Returns:

            True if the device configuration was loaded by Helium,
            False if the device configuraiton is still pending.``

        """
        return getattr(self.meta, 'loaded', False)
