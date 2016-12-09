"""A device resource."""

from __future__ import unicode_literals
from . import Resource


class Device(Resource):
    """Common behavior for devices.

    Devices are physical resources that share common behavior such as
    `DeviceConfiguration`

    """

    def device_configuration(self, pending=False, use_included=False):
        """Get a specific device configuration.

        A device can have at most one loaded and one pending device
        configuration. This returns that device_configuration based on
        a given flag.

        Keyword Args:

            pending(bool): Fetch the pending configuration or return
                the loaded one.

            use_included(bool): Use included resources in this device
                configuration.

        Returns:

            The requested loaded or pending configuration or None if
            no device configuration is found.

        """
        device_configs = self.device_configurations(use_included=use_included)
        for device_config in device_configs:
            if device_config.is_loaded() is not pending:
                return device_config
        return None
