"""Represents a device for simctl."""

#pylint: disable=too-many-public-methods

from typing import Any, Dict, List, Optional, Union

from isim.runtime import Runtime
from isim.device_type import DeviceType
from isim.base_types import SimulatorControlBase, SimulatorControlType

class MultipleMatchesException(Exception):
    """Raised when we have multiple matches, but only expect a single one."""

class DeviceNotFoundError(Exception):
    """Raised when a requested device is not found."""

class InvalidDeviceError(Exception):
    """Raised when a device is not of the correct type."""

class Device(SimulatorControlBase):
    """Represents a device for the iOS simulator."""

    runtime_name: str
    raw_info: Dict[str, Any]
    state: str
    availability: str
    name: str
    udid: str
    _runtime: Optional[Runtime]

    def __init__(self, device_info: Dict[str, Any], runtime_name: str) -> None:
        """Construct a Device object from simctl output and a runtime key.

        device_info: The dictionary representing the simctl output for a device.
        runtime_name: The name of the runtime that the device uses.
        """

        super().__init__(device_info, SimulatorControlType.device)
        self.runtime_name = runtime_name
        self._runtime = None
        self.raw_info = device_info
        self.state = device_info["state"]
        self.availability = device_info["availability"]
        self.name = device_info["name"]
        self.udid = device_info["udid"]

    def refresh_state(self) -> None:
        """Refreshes the state by consulting simctl."""
        device = Device.from_identifier(self.udid)
        self.raw_info = device.raw_info
        self.state = device.state
        self.availability = device.availability
        self.name = device.name
        self.udid = device.udid

    def runtime(self) -> Runtime:
        """Return the runtime of the device."""
        if self._runtime is None:
            self._runtime = Runtime.from_name(self.runtime_name)

        return self._runtime

    def get_app_container(self, app_identifier: str, container: Optional[str] = None) -> str:
        """Get the path of the installed app's container."""
        command = 'get_app_container "%s" "%s"' % (self.udid, app_identifier)

        if container is not None:
            command += ' "' + container + '"'

        path = self._run_command(command)

        # The path has an extra new line at the end, so remove it when returning
        #pylint: disable=unsubscriptable-object
        return path[:-1]
        #pylint: enable=unsubscriptable-object

    def openurl(self, url: str) -> None:
        """Open the url on the device."""
        command = 'openurl "%s" "%s"' % (self.udid, url)
        self._run_command(command)

    def logverbose(self, enable: bool) -> None:
        """Enable or disable verbose logging."""
        command = 'logverbose "%s" "%s"' % (self.udid, "enable" if enable else "disable")
        self._run_command(command)

    def icloud_sync(self) -> None:
        """Trigger iCloud sync."""
        command = 'icloud_sync "%s"' % (self.udid,)
        self._run_command(command)

    def getenv(self, variable_name: str) -> str:
        """Return the specified environment variable."""
        command = 'getenv "%s" "%s"' % (self.udid, variable_name)
        variable = self._run_command(command)
        # The variable has an extra new line at the end, so remove it when returning
        #pylint: disable=unsubscriptable-object
        return variable[:-1]
        #pylint: enable=unsubscriptable-object

    def addmedia(self, paths: Union[str, List[str]]) -> None:
        """Add photos, live photos, or videos to the photo library."""
        if isinstance(paths, str):
            paths = [paths]

        if not paths:
            return

        command = 'addmedia "%s" ' % (self.udid)

        # Now we need to add the paths
        quoted_paths = ['"' + path + '"' for path in paths]
        paths_arg = " ".join(quoted_paths)
        command += paths_arg

        self._run_command(command)

    def terminate(self, app_identifier: str) -> None:
        """Terminate an application by identifier."""
        command = 'terminate "%s" "%s"' % (self.udid, app_identifier)
        self._run_command(command)

    def install(self, path: str) -> None:
        """Install an application from path."""
        command = 'install "%s" "%s"' % (self.udid, path)
        self._run_command(command)

    def uninstall(self, app_identifier: str) -> None:
        """Uninstall an application by identifier."""
        command = 'uninstall "%s" "%s"' % (self.udid, app_identifier)
        self._run_command(command)

    def delete(self) -> None:
        """Delete the device."""
        command = 'delete "%s"' % (self.udid)
        self._run_command(command)

    def rename(self, name: str) -> None:
        """Rename the device."""
        command = 'rename "%s" "%s"' % (self.udid, name)
        self._run_command(command)

    def boot(self) -> None:
        """Boot the device."""
        command = 'boot "%s"' % (self.udid,)
        self._run_command(command)

    def shutdown(self) -> None:
        """Shutdown the device."""
        command = 'shutdown "%s"' % (self.udid,)
        self._run_command(command)

    def erase(self) -> None:
        """Erases the device's contents and settings."""
        command = 'erase "%s"' % (self.udid,)
        self._run_command(command)

    def upgrade(self, runtime: Runtime) -> None:
        """Upgrade the device to a newer runtime."""
        command = 'upgrade "%s" "%s"' % (self.udid, runtime.identifier)
        self._run_command(command)
        self._runtime = None
        self.runtime_name = runtime.name

    def clone(self, new_name: str) -> str:
        """Clone the device."""
        command = 'clone "%s" "%s"' % (self.udid, new_name)
        device_id = self._run_command(command)

        # The device ID has a new line at the end. Strip it when returning.
        #pylint: disable=unsubscriptable-object
        return device_id[:-1]
        #pylint: enable=unsubscriptable-object

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

        command = 'pair "%s" "%s"' % (watch.udid, phone.udid)
        pair_id = self._run_command(command)

        # The pair ID has a new line at the end. Strip it when returning.
        #pylint: disable=unsubscriptable-object
        return pair_id[:-1]
        #pylint: enable=unsubscriptable-object

    def __str__(self):
        """Return the string representation of the object."""
        return self.name + ": " + self.udid

    @staticmethod
    def from_simctl_info(info: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List['Device']]:
        """Create a new device from the simctl info."""
        all_devices: Dict[str, List[Device]] = {}
        for runtime_name in info.keys():
            runtime_devices_info = info[runtime_name]
            devices: List['Device'] = []
            for device_info in runtime_devices_info:
                devices.append(Device(device_info, runtime_name))
            all_devices[runtime_name] = devices
        return all_devices

    @staticmethod
    def from_identifier(identifier: str) -> 'Device':
        """Create a new device from the simctl info."""
        for _, devices in Device.list_all().items():
            for device in devices:
                if device.udid == identifier:
                    return device

        raise DeviceNotFoundError("No device with ID: " + identifier)

    @staticmethod
    def from_name(
            name: str,
            runtime: Optional[Runtime] = None
        ) -> Optional['Device']:
        """Get a device from the existing devices using the name.

        If the name matches multiple devices, the runtime is used as a secondary filter (if supplied).
        If there are still multiple matching devices, an exception is raised.
        """

        # Only get the ones matching the name (keep track of the runtime_id in case there are multiple)
        matching_name_devices = []

        for runtime_name, runtime_devices in Device.list_all().items():
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

    @staticmethod
    def create(
            name: str,
            device_type: DeviceType,
            runtime: Runtime
        ) -> 'Device':
        """Create a new device."""
        command = 'create "%s" "%s" "%s"' % (name, device_type.identifier, runtime.identifier)
        device_id = SimulatorControlBase.run_command(command)

        # The device ID has a new line at the end, so strip it.
        #pylint: disable=unsubscriptable-object
        device_id = device_id[:-1]
        #pylint: enable=unsubscriptable-object

        return Device.from_identifier(device_id)

    @staticmethod
    def delete_unavailable() -> None:
        """Delete all unavailable devices."""
        SimulatorControlBase.run_command("delete unavailable")

    @staticmethod
    def list_all() -> Dict[str, List['Device']]:
        """Return all available devices."""
        raw_info = Device.list_all_raw()
        return Device.from_simctl_info(raw_info)

    @staticmethod
    def list_all_raw() -> Dict[str, List[Dict[str, Any]]]:
        """Return all device info."""
        return SimulatorControlBase.list_type(SimulatorControlType.device)
