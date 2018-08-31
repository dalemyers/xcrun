"""Handles simulator device types."""

import xcrun.simctl.listall

class DeviceTypeNotFoundError(Exception):
    """Raised when a requested device type is not found."""
    pass

class DeviceType(object):
    """Represents a device type for the iOS simulator."""

    def __init__(self, device_type_info):
        """Construct a DeviceType object from xcrun output.

        device_type_info: The dictionary representing the xcrun output for a device type.
        """
        self.raw_info = device_type_info
        self.name = device_type_info["name"]
        self.identifier = device_type_info["identifier"]

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if not isinstance(other, self.__class__):
            return False

        return self.raw_info == other.raw_info

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __str__(self):
        """Return a user readable string representing the device type."""
        return self.name + ": " + self.identifier


def from_xcrun_info(info):
    """Create a new device type from the xcrun info."""
    info = info["devicetypes"]
    device_types = []
    for device_type_info in info:
        device_types.append(DeviceType(device_type_info))
    return device_types

def from_id(identifier):
    """Get a device type from its identifier."""
    device_types = xcrun.simctl.listall.device_types()
    for device_type in device_types:
        if device_type.identifier == identifier:
            return device_type
    raise DeviceTypeNotFoundError("No device type matching identifier: " + identifier)

def from_name(name):
    """Create a device type by looking up the existing ones matching the supplied name."""
    # Get all device types
    device_types = xcrun.simctl.listall.device_types()

    for device_type in device_types:
        if device_type.name == name:
            return device_type

    raise DeviceTypeNotFoundError("No device type matching name: " + name)
