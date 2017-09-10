"""Handles simulator device types."""

class DeviceType(object):
    """Represents a device type for the iOS simulator."""

    def __init__(self, device_type_info):
        """Construct a DeviceType object from xcrun output.

        device_type_info: The dictionary representing the xcrun output for a device type.
        """
        self.raw_info = device_type_info
        self.name = device_type_info["name"]
        self.identifier = device_type_info["identifier"]

    def __str__(self):
        """Return a user readable string representing the device type."""
        return self.name + ": " + self.identifier

    def __repr__(self):
        """Return a string representation of the raw_info which can be used to reconstruct the device type."""
        return str(self.raw_info)


def from_xcrun_info(info):
    """Create a new device type from the xcrun info."""
    info = info["devicetypes"]
    device_types = []
    for device_type_info in info:
        device_types.append(DeviceType(device_type_info))
    return device_types
