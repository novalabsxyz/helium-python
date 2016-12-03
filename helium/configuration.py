"""A configuration resource."""

from __future__ import unicode_literals
from . import Resource


class Configuration(Resource):
    """Configuration holder.

    Helium devices are configurable. This resource holds those
    attributes. Configuration are not mutable for performance
    auditability purposes. In order to update a configuration you will
    need to create a new one and associate the new one with the device
    you're configuration.

    In order to apply a configuration to a device, use a
    `DeviceConfiguration`.

    For example to configure a `sensor` that takes a ``min`` and ``max``
    value

    .. code-block:: python

       config = Configuration(client, attributes={
           'min': 0,
           'max': 100
       })
       device_config = DeviceConfiguration.create(client,
                                                  device=sensor,
                                                  configuration=config)

    Once the device configuration is created it is in a ``pending``
    state until the system loads it for delivery to the given
    device. At any given time a device can have at most one pending
    and one loaded configuration.

    Note that a created configuration can be applied to multiple
    devices by creating multiple device configurations.

    """

    pass
