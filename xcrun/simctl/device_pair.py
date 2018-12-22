"""Handles simulator watch device pairs."""

from typing import Any, Dict, List

import xcrun.simctl

class DevicePair(xcrun.simctl.SimulatorControlBase):
    """Represents a device pair for the iOS simulator."""

    raw_info: Dict[str, Any]
    identifier: str
    watch_udid: str
    phone_udid: str

    def __init__(self, device_pair_identifier: str, device_pair_info: Dict[str, Any]) -> None:
        """Construct a DevicePair object from xcrun output.

        device_pair_identifier: The unique identifier for this device pair.
        device_pair_info: The dictionary representing the xcrun output for a device pair.
        """
        super().__init__(device_pair_info, xcrun.simctl.SimulatorControlType.device_pair)
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
        xcrun.simctl.unpair_devices(self)

    def activate(self) -> None:
        """Activate a pair."""
        xcrun.simctl.activate_pair(self)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return self.identifier


def from_xcrun_info(info: Dict[str, Any]) -> List[DevicePair]:
    """Create a new device pair using the info from xcrun."""
    device_pairs = []
    for device_pair_identifier, device_pair_info in info.items():
        device_pairs.append(DevicePair(device_pair_identifier, device_pair_info))
    return device_pairs
