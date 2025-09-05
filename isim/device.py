"""Represents a device for simctl."""

# pylint: disable=too-many-public-methods

import os
import re
import shlex
import signal
import subprocess
from typing import Any, Optional

from isim.runtime import Runtime
from isim.device_type import DeviceType
from isim.base_types import SimulatorControlBase, SimulatorControlType


class MultipleMatchesException(Exception):
    """Raised when we have multiple matches, but only expect a single one."""


class DeviceNotFoundError(Exception):
    """Raised when a requested device is not found."""


class InvalidDeviceError(Exception):
    """Raised when a device is not of the correct type."""


# pylint: disable=too-many-instance-attributes
class Device(SimulatorControlBase):
    """Represents a device for the iOS simulator."""

    raw_info: dict[str, Any]

    availability: str | None
    is_available: str
    name: str
    runtime_id: str
    device_type_id: str
    state: str
    udid: str

    _runtime: Runtime | None
    _device_type: DeviceType | None
    _video_recording_process: subprocess.Popen | None = None

    def __init__(self, device_info: dict[str, Any], runtime_id: str) -> None:
        """Construct a Device object from simctl output and a runtime key.

        device_info: The dictionary representing the simctl output for a device.
        runtime_id: The ID of the runtime that the device uses.
        """

        super().__init__(device_info, SimulatorControlType.DEVICE)
        self._runtime = None
        self._device_type = None
        self._video_recording_process = None
        self.raw_info = device_info
        self.availability = device_info.get("availability")
        self.is_available = device_info["isAvailable"]
        self.name = device_info["name"]
        self.device_type_id = device_info["deviceTypeIdentifier"]
        self.runtime_id = runtime_id
        self.state = device_info["state"]
        self.udid = device_info["udid"]

    def refresh_state(self) -> None:
        """Refreshes the state by consulting simctl."""
        device = Device.from_identifier(self.udid)
        self.raw_info = device.raw_info
        self.availability = device.availability
        self.is_available = device.is_available
        self.name = device.name
        self.state = device.state
        self.udid = device.udid

    def runtime(self) -> Runtime:
        """Return the runtime of the device."""
        if self._runtime is None:
            self._runtime = Runtime.from_id(self.runtime_id)

        return self._runtime

    def device_type(self) -> DeviceType:
        """Return the device type of the device."""
        if self._device_type is None:
            self._device_type = DeviceType.from_id(self.device_type_id)

        return self._device_type

    def get_app_container(self, app_identifier: str, container: str | None = None, **kwargs) -> str:
        """Get the path of the installed app's container."""
        command = f'get_app_container "{self.udid}" "{app_identifier}"'

        if container is not None:
            command += f' "{container}"'

        path = self._run_command(command, **kwargs)

        # The path has an extra new line at the end, so remove it when returning
        # pylint: disable=unsubscriptable-object
        return path[:-1]
        # pylint: enable=unsubscriptable-object

    def get_data_directory(self, app_identifier: str) -> str | None:
        """Get the path of the data directory for the app. (The location where
        the app can store data, files, etc.)

        There's no real way of doing this. This method works by scanning the
        installation logs for the simulator to try and find out where the app
        actually lives.
        """
        app_container = self.get_app_container(app_identifier)

        # Drop the *.app
        app_container = os.path.dirname(app_container)

        data_folder = os.path.join(app_container, "..", "..", "..", "..")
        mobile_installation_folder = os.path.join(
            data_folder, "Library", "Logs", "MobileInstallation"
        )
        mobile_installation_folder = os.path.abspath(mobile_installation_folder)

        log_file_names = os.listdir(mobile_installation_folder)

        # We sort these since we want the latest file (.0) first
        log_file_names = sorted(log_file_names)

        container_pattern = re.compile(f".*Data container for {app_identifier} is now at (.*)")

        # We are looking for the last match in the file
        for log_file in log_file_names:
            log_path = os.path.join(mobile_installation_folder, log_file)

            with open(log_path, "r", encoding="utf-8") as log_file_handle:
                log_lines = log_file_handle.readlines()

            # We want the last mention in the file (i.e. the latest)
            log_lines.reverse()

            for line in log_lines:
                matches = container_pattern.findall(line.strip())

                if not matches:
                    continue

                # We found a match, so return it
                return matches[0]

        return None

    def openurl(self, url: str, **kwargs) -> None:
        """Open the url on the device."""
        command = f'openurl "{self.udid}" "{url}"'
        self._run_command(command, **kwargs)

    def logverbose(self, enable: bool, **kwargs) -> None:
        """Enable or disable verbose logging."""
        command = f'logverbose "{self.udid}" "{"enable" if enable else "disable"}"'
        self._run_command(command, **kwargs)

    def icloud_sync(self, **kwargs) -> None:
        """Trigger iCloud sync."""
        command = f'icloud_sync "{self.udid}"'
        self._run_command(command, **kwargs)

    def getenv(self, variable_name: str, **kwargs) -> str:
        """Return the specified environment variable."""
        command = f'getenv "{self.udid}" "{variable_name}"'
        variable = self._run_command(command, **kwargs)
        # The variable has an extra new line at the end, so remove it when returning
        # pylint: disable=unsubscriptable-object
        return variable[:-1]
        # pylint: enable=unsubscriptable-object

    def addmedia(self, paths: str | list[str], **kwargs) -> None:
        """Add photos, live photos, or videos to the photo library."""
        if isinstance(paths, str):
            paths = [paths]

        if not paths:
            return

        command = f'addmedia "{self.udid}" '

        # Now we need to add the paths
        quoted_paths = ['"' + path + '"' for path in paths]
        paths_arg = " ".join(quoted_paths)
        command += paths_arg

        self._run_command(command, **kwargs)

    def terminate(self, app_identifier: str, **kwargs) -> None:
        """Terminate an application by identifier."""
        command = f'terminate "{self.udid}" "{app_identifier}"'
        self._run_command(command, **kwargs)

    def install(self, path: str, **kwargs) -> None:
        """Install an application from path."""
        command = f'install "{self.udid}" "{path}"'
        self._run_command(command, **kwargs)

    def uninstall(self, app_identifier: str, **kwargs) -> None:
        """Uninstall an application by identifier."""
        command = f'uninstall "{self.udid}" "{app_identifier}"'
        self._run_command(command, **kwargs)

    def delete(self, **kwargs) -> None:
        """Delete the device."""
        command = f'delete "{self.udid}"'
        self._run_command(command, **kwargs)

    def rename(self, name: str, **kwargs) -> None:
        """Rename the device."""
        command = f'rename "{self.udid}" "{name}"'
        self._run_command(command, **kwargs)

    def boot(self, **kwargs) -> None:
        """Boot the device."""
        command = f'boot "{self.udid}"'
        self._run_command(command, **kwargs)

    def boot_status(self, **kwargs) -> None:
        """Get the boot status of the device."""
        command = f'bootstatus "{self.udid}"'
        self._run_command(command, **kwargs)

    def shutdown(self, **kwargs) -> None:
        """Shutdown the device."""
        command = f'shutdown "{self.udid}"'
        self._run_command(command, **kwargs)

    def erase(self, **kwargs) -> None:
        """Erases the device's contents and settings."""
        command = f'erase "{self.udid}"'
        self._run_command(command, **kwargs)

    def upgrade(self, runtime: Runtime, **kwargs) -> None:
        """Upgrade the device to a newer runtime."""
        command = f'upgrade "{self.udid}" "{runtime.identifier}"'
        self._run_command(command, **kwargs)
        self._runtime = None
        self.runtime_id = runtime.identifier

    def clone(self, new_name: str, **kwargs) -> str:
        """Clone the device."""
        command = f'clone "{self.udid}" "{new_name}"'
        device_id = self._run_command(command, **kwargs)

        # The device ID has a new line at the end. Strip it when returning.
        # pylint: disable=unsubscriptable-object
        return device_id[:-1]
        # pylint: enable=unsubscriptable-object

    def pair(self, other_device: "Device", **kwargs) -> str:
        """Create a new watch and phone pair."""
        watch = None
        phone = None

        if "com.apple.CoreSimulator.SimRuntime.iOS" in self.runtime_id:
            phone = self

        if "com.apple.CoreSimulator.SimRuntime.iOS" in other_device.runtime_id:
            phone = other_device

        if "com.apple.CoreSimulator.SimRuntime.watchOS" in self.runtime_id:
            watch = self

        if "com.apple.CoreSimulator.SimRuntime.watchOS" in other_device.runtime_id:
            watch = other_device

        if watch is None or phone is None:
            raise InvalidDeviceError("One device should be a watch and the other a phone")

        command = f'pair "{watch.udid}" "{phone.udid}"'
        pair_id = self._run_command(command, **kwargs)

        # The pair ID has a new line at the end. Strip it when returning.
        # pylint: disable=unsubscriptable-object
        return pair_id[:-1]
        # pylint: enable=unsubscriptable-object

    def screenshot(self, output_path: str, **kwargs) -> None:
        """Take a screenshot of the device and save to `output_path`."""

        if os.path.exists(output_path):
            raise FileExistsError("Output file path already exists")

        self._run_command(f"io {self.udid} screenshot {shlex.quote(output_path)}", **kwargs)

    def start_video_recording(self, output_path: str, force: bool = True, **kwargs) -> None:
        """Start video recording of the device and save to `output_path`.

        If `force` is True, it will overwrite the file if it already exists.
        """
        if os.path.exists(output_path) and not force:
            raise FileExistsError("Output file path already exists")

        # We can't use the `run_command` method here because we need to keep a reference to the
        # process in order to stop the recording later.
        command = ["xcrun", "simctl", "io", self.udid, "recordVideo"]

        if force:
            command.append("--force")

        command.append(output_path)

        self._video_recording_process = subprocess.Popen(
            command,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            encoding="utf-8",
            **kwargs,
        )

        if not self._video_recording_process:
            raise ChildProcessError("Failed to start video recording process")

        for line in self._video_recording_process.stdout:
            if "Recording started" in line:
                return

    def stop_video_recording(self) -> None:
        """Stop the video recording of the device."""
        if self._video_recording_process is None:
            raise RuntimeError("No video recording process is running")

        self._video_recording_process.send_signal(signal.SIGINT)

        self._video_recording_process.wait()
        self._video_recording_process = None

    def spawn(self, executable: str, **kwargs) -> str:
        """Spawn a process by executing a given executable on a device."""
        command = f'spawn "{self.udid}" {executable}'
        return self._run_command(command, **kwargs)

    def launch(self, identifier: str, **kwargs) -> str:
        """Launch an application by identifier on a device."""
        command = f'launch "{self.udid}" "{identifier}"'
        return self._run_command(command, **kwargs)

    def __str__(self):
        """Return the string representation of the object."""
        return self.name + ": " + self.udid

    def __repr__(self) -> str:
        """Return the string programmatic representation of the object."""
        return str({"runtime_id": self.runtime_id, "raw_info": self.raw_info})

    @staticmethod
    def from_simctl_info(
        info: dict[str, list[dict[str, Any]]],
    ) -> dict[str, list["Device"]]:
        """Create a new device from the simctl info."""
        all_devices: dict[str, list[Device]] = {}
        for runtime_id, runtime_devices_info in info.items():
            devices: list["Device"] = []
            for device_info in runtime_devices_info:
                if not device_info.get("isAvailable", False):
                    continue
                devices.append(Device(device_info, runtime_id))
            all_devices[runtime_id] = devices
        return all_devices

    @staticmethod
    def from_identifier(identifier: str) -> "Device":
        """Create a new device from the simctl info."""
        for _, devices in Device.list_all().items():
            for device in devices:
                if device.udid == identifier:
                    return device

        raise DeviceNotFoundError("No device with ID: " + identifier)

    @staticmethod
    def from_name(name: str, runtime: Runtime | None = None) -> Optional["Device"]:
        """Get a device from the existing devices using the name.

        If the name matches multiple devices, the runtime is used as a secondary filter (if supplied).
        If there are still multiple matching devices, an exception is raised.
        """

        # Only get the ones matching the name (keep track of the runtime_id in case there are multiple)
        matching_name_devices = []

        for runtime_id, runtime_devices in Device.list_all().items():
            for device in runtime_devices:
                if device.name == name:
                    matching_name_devices.append((device, runtime_id))

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
        matching_devices = [
            device for device in matching_name_devices if device[1] == runtime.identifier
        ]

        if not matching_devices:
            return None

        # We should only have one
        if len(matching_devices) > 1:
            raise MultipleMatchesException("Multiple device matches even with runtime supplied")

        return matching_devices[0][0]

    @staticmethod
    def create(name: str, device_type: DeviceType, runtime: Runtime, **kwargs) -> "Device":
        """Create a new device."""
        command = f'create "{name}" {device_type.identifier} {runtime.identifier}'
        device_id = SimulatorControlBase.run_command(command, **kwargs)

        # The device ID has a new line at the end, so strip it.
        # pylint: disable=unsubscriptable-object
        device_id = device_id[:-1]
        # pylint: enable=unsubscriptable-object

        return Device.from_identifier(device_id)

    @staticmethod
    def delete_unavailable(**kwargs) -> None:
        """Delete all unavailable devices."""
        SimulatorControlBase.run_command("delete unavailable", **kwargs)

    @staticmethod
    def delete_all(**kwargs) -> None:
        """Delete all devices."""
        SimulatorControlBase.run_command("delete all", **kwargs)

    @staticmethod
    def erase_all(**kwargs) -> None:
        """Erase all devices."""
        SimulatorControlBase.run_command("erase all", **kwargs)

    @staticmethod
    def list_all() -> dict[str, list["Device"]]:
        """Return all available devices."""
        raw_info = Device.list_all_raw()
        return Device.from_simctl_info(raw_info)

    @staticmethod
    def list_all_raw(**kwargs) -> dict[str, list[dict[str, Any]]]:
        """Return all device info."""
        return SimulatorControlBase.list_type(SimulatorControlType.DEVICE, **kwargs)
