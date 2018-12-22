"""Represents a device for xcrun simctl."""

from typing import Any, Dict, List, Optional

import xcrun.simctl.runtime
import xcrun.simctl.listall
import xcrun.simctl

class MultipleMatchesException(Exception):
    """Raised when we have multiple matches, but only expect a single one."""

class DeviceNotFoundError(Exception):
    """Raised when a requested device is not found."""

class InvalidDeviceError(Exception):
    """Raised when a device is not of the correct type."""

class Device(xcrun.simctl.SimulatorControlBase):
    """Represents a device for the iOS simulator."""

    runtime_name: str
    raw_info: Dict[str, Any]
    state: str
    availability: str
    name: str
    udid: str
    _runtime: Optional[xcrun.simctl.runtime.Runtime]

    def __init__(self, device_info: Dict[str, Any], runtime_name: str):
        """Construct a Device object from xcrun output and a runtime key.

        device_info: The dictionary representing the xcrun output for a device.
        runtime_name: The name of the runtime that the device uses.
        """

        super().__init__(device_info, xcrun.simctl.SimulatorControlType.device)
        self.runtime_name = runtime_name
        self._runtime = None
        self._update_info(device_info)

    def _update_info(self, device_info: Dict[str, Any]) -> None:
        self.raw_info = device_info
        self.state = device_info["state"]
        self.availability = device_info["availability"]
        self.name = device_info["name"]
        self.udid = device_info["udid"]

    def refresh_state(self) -> None:
        """Refreshes the state by consulting xcrun."""
        device_info = xcrun.simctl.device_info(self.udid)

        if device_info is None:
            raise Exception("Could not determine device info.")

        self._update_info(device_info)

    def runtime(self) -> xcrun.simctl.runtime.Runtime:
        """Return the runtime of the device."""
        if self._runtime is None:
            self._runtime = xcrun.simctl.runtime.from_name(self.runtime_name)

        return self._runtime

    def get_app_container(self, app_identifier: str, container: Optional[str] = None) -> str:
        """Get the path of the installed app's container."""
        return xcrun.simctl.get_app_container(self, app_identifier, container)

    def openurl(self, url: str) -> None:
        """Open the url on the device."""
        xcrun.simctl.openurl(self, url)

    def logverbose(self, enable: bool) -> None:
        """Enable or disable verbose logging."""
        xcrun.simctl.logverbose(self, enable)

    def icloud_sync(self) -> None:
        """Trigger iCloud sync."""
        xcrun.simctl.icloud_sync(self)

    def getenv(self, variable_name: str) -> str:
        """Return the specified environment variable."""
        return xcrun.simctl.getenv(self, variable_name)

    def addmedia(self, paths: List[str]) -> None:
        """Add photos, live photos, or videos to the photo library."""
        return xcrun.simctl.addmedia(self, paths)

    def terminate(self, app_identifier: str) -> None:
        """Terminate an application by identifier."""
        xcrun.simctl.terminate_app(self, app_identifier)

    def install(self, path: str) -> None:
        """Install an application from path."""
        xcrun.simctl.install_app(self, path)

    def uninstall(self, app_identifier: str) -> None:
        """Uninstall an application by identifier."""
        xcrun.simctl.uninstall_app(self, app_identifier)

    def delete(self) -> None:
        """Delete the device."""
        xcrun.simctl.delete_device(self)

    def rename(self, name: str) -> None:
        """Rename the device."""
        xcrun.simctl.rename_device(self, name)

    def boot(self) -> None:
        """Boot the device."""
        xcrun.simctl.boot_device(self)

    def shutdown(self) -> None:
        """Shutdown the device."""
        xcrun.simctl.shutdown_device(self)

    def erase(self) -> None:
        """Erases the device's contents and settings."""
        xcrun.simctl.erase_device(self)

    def upgrade(self, runtime: xcrun.simctl.runtime.Runtime) -> None:
        """Upgrade the device to a newer runtime."""
        xcrun.simctl.upgrade_device(self, runtime)
        self._runtime = None
        self.runtime_name = runtime.name

    def clone(self, new_name: str) -> str:
        """Clone the device."""
        return xcrun.simctl.clone_device(self, new_name)

    def pair(self, other_device: 'Device') -> str:
        """Create a new watch and phone pair."""
        watch = None
        phone = None

        if "iOS" in self.runtime_name:
            phone = self

        if "iOS" in other_device.runtime_name:
            phone = other_device

        if "watchOS" in self.runtime_name:
            watch = self

        if "watchOS" in other_device.runtime_name:
            watch = other_device

        if watch is None or phone is None:
            raise InvalidDeviceError("One device should be a watch and the other a phone")

        return xcrun.simctl.pair_devices(watch, phone)

    def __str__(self):
        """Return the string representation of the object."""
        return self.name + ": " + self.udid


def from_xcrun_info(info: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[xcrun.simctl.device.Device]]:
    """Create a new device from the xcrun info."""
    all_devices: Dict[str, List[xcrun.simctl.device.Device]] = {}
    for runtime_name in info.keys():
        runtime_devices_info = info[runtime_name]
        devices: List[xcrun.simctl.device.Device] = []
        for device_info in runtime_devices_info:
            devices.append(Device(device_info, runtime_name))
        all_devices[runtime_name] = devices
    return all_devices


def from_identifier(identifier: str) -> xcrun.simctl.device.Device:
    """Create a new device from the xcrun info."""
    all_devices = xcrun.simctl.listall.devices()
    for _, devices in all_devices.items():
        for device in devices:
            if device.udid == identifier:
                return device

    raise DeviceNotFoundError("No device with ID: " + identifier)


def from_name(
        name: str,
        runtime: Optional[xcrun.simctl.runtime.Runtime] = None
    ) -> Optional[xcrun.simctl.device.Device]:
    """Get a device from the existing devices using the name.

    If the name matches multiple devices, the runtime is used as a secondary filter (if supplied).
    If there are still multiple matching devices, an exception is raised.
    """

    # Get all devices
    all_devices = xcrun.simctl.listall.devices()

    # Now only get the ones matching the name (keep track of the runtime_id in case there are
    # multiple)
    matching_name_devices = []

    for runtime_name, runtime_devices in all_devices.items():
        for device in runtime_devices:
            if device.name == name:
                matching_name_devices.append((device, runtime_name))

    # If there were none, then we have none to return
    if not matching_name_devices:
        return None

    # If there was 1, then we return it
    if len(matching_name_devices) == 1:
        return matching_name_devices[0][0]

    # If we have more than one, we need a run time in order to differentate between them
    if runtime is None:
        raise MultipleMatchesException("Multiple device matches, but no runtime supplied")

    # Get devices where the runtime name matches
    matching_devices = [device for device in matching_name_devices if device[1] == runtime.name]

    if not matching_devices:
        return None

    # We should only have one
    if len(matching_devices) > 1:
        raise MultipleMatchesException("Multiple device matches even with runtime supplied")

    return matching_devices[0][0]

def create(
        name: str,
        device_type: xcrun.simctl.device_type.DeviceType,
        runtime: xcrun.simctl.runtime.Runtime
    ) -> xcrun.simctl.device.Device:
    """Create a new device."""
    device_id = xcrun.simctl.create_device(name, device_type, runtime)
    return from_identifier(device_id)

def delete_unavailable() -> None:
    """Delete all unavailable devices."""
    xcrun.simctl.delete_unavailable_devices()
