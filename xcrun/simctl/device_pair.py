"""Handles simulator watch device pairs."""

import xcrun.simctl

class DevicePair(object):
    """Represents a device pair for the iOS simulator."""

    def __init__(self, device_pair_identifier, device_pair_info):
        """Construct a DevicePair object from xcrun output.

        device_pair_identifier: The unique identifier for this device pair.
        device_pair_info: The dictionary representing the xcrun output for a device pair.
        """

        self.raw_info = device_pair_info
        self.identifier = device_pair_identifier
        self.watch_udid = device_pair_info["watch"]["udid"]
        self.phone_udid = device_pair_info["phone"]["udid"]

    def watch(self):
        """Return the device representing the watch in the pair."""
        raise NotImplementedError()

    def phone(self):
        """Return the device representing the phone in the pair."""
        raise NotImplementedError()

    def unpair(self):
        """Unpair a watch and phone pair."""
        xcrun.simctl.unpair_devices(self)

    def activate(self):
        """Activate a pair."""
        xcrun.simctl.activate_pair(self)

    def __str__(self):
        """Return the string representation of the object."""
        return self.identifier


def from_xcrun_info(info):
    """Create a new device pair using the info from xcrun."""
    device_pairs = []
    pair_info = info["pairs"]
    for device_pair_identifier, device_pair_info in pair_info.items():
        device_pairs.append(DevicePair(device_pair_identifier, device_pair_info))
    return device_pairs
