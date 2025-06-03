"""Handles simulator device types."""

from isim.base_types import SimulatorControlBase, SimulatorControlType


class DeviceTypeNotFoundError(Exception):
    """Raised when a requested device type is not found."""


class DeviceType(SimulatorControlBase):
    """Represents a device type for the iOS simulator."""

    raw_info: dict[str, str]
    bundle_path: str
    identifier: str
    name: str

    def __init__(self, device_type_info: dict[str, str]):
        """Construct a DeviceType object from simctl output.

        device_type_info: The dictionary representing the simctl output for a device type.
        """
        super().__init__(device_type_info, SimulatorControlType.DEVICE_TYPE)
        self.raw_info = device_type_info
        self.bundle_path = device_type_info["bundlePath"].replace("\\/", "/")
        self.identifier = device_type_info["identifier"]
        self.name = device_type_info["name"]

    def __str__(self) -> str:
        """Return a user readable string representing the device type."""
        return self.name + ": " + self.identifier

    def __repr__(self) -> str:
        """Return the string programmatic representation of the object."""
        return str(self.raw_info)

    @staticmethod
    def from_simctl_info(info: list[dict[str, str]]) -> list["DeviceType"]:
        """Create a new device type from the simctl info."""
        device_types = []
        for device_type_info in info:
            device_types.append(DeviceType(device_type_info))
        return device_types

    @staticmethod
    def from_id(identifier: str) -> "DeviceType":
        """Get a device type from its identifier."""
        for device_type in DeviceType.list_all():
            if device_type.identifier == identifier:
                return device_type
        raise DeviceTypeNotFoundError("No device type matching identifier: " + identifier)

    @staticmethod
    def from_name(name: str) -> "DeviceType":
        """Create a device type by looking up the existing ones matching the supplied name."""
        # Get all device types
        device_types = DeviceType.list_all()

        for device_type in device_types:
            if device_type.name == name:
                return device_type

        raise DeviceTypeNotFoundError("No device type matching name: " + name)

    @staticmethod
    def list_all() -> list["DeviceType"]:
        """Return all available device types."""
        device_type_info = SimulatorControlBase.list_type(SimulatorControlType.DEVICE_TYPE)
        return DeviceType.from_simctl_info(device_type_info)
