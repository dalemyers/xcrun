"""Handles simulator watch device pairs."""

from typing import Any, Dict, List

from isim.base_types import SimulatorControlBase, SimulatorControlType

class DevicePair(SimulatorControlBase):
    """Represents a device pair for the iOS simulator."""

    raw_info: Dict[str, Any]
    identifier: str
    watch_udid: str
    phone_udid: str

    def __init__(self, device_pair_identifier: str, device_pair_info: Dict[str, Any]) -> None:
        """Construct a DevicePair object from simctl output.

        device_pair_identifier: The unique identifier for this device pair.
        device_pair_info: The dictionary representing the simctl output for a device pair.
        """
        super().__init__(device_pair_info, SimulatorControlType.device_pair)
        self.raw_info = device_pair_info
        self.identifier = device_pair_identifier
        self.watch_udid = device_pair_info["watch"]["udid"]
        self.phone_udid = device_pair_info["phone"]["udid"]

    def watch(self) -> None:
        """Return the device representing the watch in the pair."""
        raise NotImplementedError()

    def phone(self) -> None:
        """Return the device representing the phone in the pair."""
        raise NotImplementedError()

    def unpair(self) -> None:
        """Unpair a watch and phone pair."""
        command = 'unpair "%s"' % (self.identifier,)
        self._run_command(command)

    def activate(self) -> None:
        """Activate a pair."""
        command = 'pair_activate "%s"' % (self.identifier,)
        self._run_command(command)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return self.identifier

    def __repr__(self) -> str:
        """Return the string programmatic representation of the object."""
        return str({"identifier": self.identifier, "raw_info": self.raw_info})

    @staticmethod
    def from_simctl_info(info: Dict[str, Any]) -> List['DevicePair']:
        """Create a new device pair using the info from simctl."""
        device_pairs = []
        for device_pair_identifier, device_pair_info in info.items():
            device_pairs.append(DevicePair(device_pair_identifier, device_pair_info))
        return device_pairs

    @staticmethod
    def list_all() -> List['DevicePair']:
        """Return all available device pairs."""
        device_pair_info = SimulatorControlBase.list_type(SimulatorControlType.device_pair)
        return DevicePair.from_simctl_info(device_pair_info)
