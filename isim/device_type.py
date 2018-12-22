"""Handles simulator device types."""

from typing import Dict, List

import isim.listall

class DeviceTypeNotFoundError(Exception):
    """Raised when a requested device type is not found."""

class DeviceType(isim.SimulatorControlBase):
    """Represents a device type for the iOS simulator."""

    raw_info: Dict[str, str]
    name: str
    identifier: str

    def __init__(self, device_type_info: Dict[str, str]):
        """Construct a DeviceType object from simctl output.

        device_type_info: The dictionary representing the simctl output for a device type.
        """
        super().__init__(device_type_info, isim.SimulatorControlType.device_type)
        self.raw_info = device_type_info
        self.name = device_type_info["name"]
        self.identifier = device_type_info["identifier"]

    def __str__(self) -> str:
        """Return a user readable string representing the device type."""
        return self.name + ": " + self.identifier


def from_simctl_info(info: List[Dict[str, str]]) -> List[DeviceType]:
    """Create a new device type from the simctl info."""
    device_types = []
    for device_type_info in info:
        device_types.append(DeviceType(device_type_info))
    return device_types

def from_id(identifier):
    """Get a device type from its identifier."""
    device_types = isim.listall.device_types()
    for device_type in device_types:
        if device_type.identifier == identifier:
            return device_type
    raise DeviceTypeNotFoundError("No device type matching identifier: " + identifier)

def from_name(name: str) -> DeviceType:
    """Create a device type by looking up the existing ones matching the supplied name."""
    # Get all device types
    device_types = isim.listall.device_types()

    for device_type in device_types:
        if device_type.name == name:
            return device_type

    raise DeviceTypeNotFoundError("No device type matching name: " + name)
