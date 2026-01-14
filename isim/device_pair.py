"""Handles simulator watch device pairs."""

from __future__ import annotations

from typing import Any

from isim.base_types import SimulatorControlBase, SimulatorControlType
from isim.device import Device


class DevicePair(SimulatorControlBase):
    """Represents a device pair for the iOS simulator."""

    raw_info: dict[str, Any]
    identifier: str
    watch_udid: str
    phone_udid: str

    def __init__(self, device_pair_identifier: str, device_pair_info: dict[str, Any]) -> None:
        """Construct a DevicePair object from simctl output.

        device_pair_identifier: The unique identifier for this device pair.
        device_pair_info: The dictionary representing the simctl output for a device pair.
        """
        super().__init__(device_pair_info, SimulatorControlType.DEVICE_PAIR)
        self.raw_info = device_pair_info
        self.identifier = device_pair_identifier
        self.watch_udid = device_pair_info["watch"]["udid"]
        self.phone_udid = device_pair_info["phone"]["udid"]

    def watch(self) -> Device:
        """Return the device representing the watch in the pair."""
        return Device.from_identifier(self.watch_udid)

    def phone(self) -> Device:
        """Return the device representing the phone in the pair."""
        return Device.from_identifier(self.phone_udid)

    def unpair(self, **kwargs: Any) -> None:
        """Unpair a watch and phone pair."""
        command = ["unpair", self.identifier]
        self._run_command(command, **kwargs)

    def activate(self, **kwargs: Any) -> None:
        """Activate a pair."""
        command = ["pair_activate", self.identifier]
        self._run_command(command, **kwargs)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return self.identifier

    def __repr__(self) -> str:
        """Return the string programmatic representation of the object."""
        return str({"identifier": self.identifier, "raw_info": self.raw_info})

    @staticmethod
    def from_simctl_info(info: dict[str, Any]) -> list["DevicePair"]:
        """Create a new device pair using the info from simctl."""
        device_pairs: list[DevicePair] = []
        for device_pair_identifier, device_pair_info in info.items():
            device_pairs.append(DevicePair(device_pair_identifier, device_pair_info))
        return device_pairs

    @staticmethod
    def list_all(**kwargs: Any) -> list["DevicePair"]:
        """Return all available device pairs."""
        device_pair_info = SimulatorControlBase.list_type(
            SimulatorControlType.DEVICE_PAIR, **kwargs
        )
        return DevicePair.from_simctl_info(device_pair_info)
