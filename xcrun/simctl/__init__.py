"""Wrapper around `xcrun simctl`."""

import enum
import subprocess
from typing import Any, Dict, List, Optional

import xcrun.simctl.device_pair
import xcrun.simctl.device_type
import xcrun.simctl.device
import xcrun.simctl.listall
import xcrun.simctl.runtime


# Advanced:

#	pbsync              Sync the pasteboard content from one pasteboard to another.
#	pbcopy              Copy standard input onto the device pasteboard.
#	pbpaste             Print the contents of the device's pasteboard to standard output.
#	io                  Set up a device IO operation.
#	spawn               Spawn a process on a device.
#	launch              Launch an application by identifier on a device.


# DONE:

#	addmedia            Add photos, live photos, or videos to the photo library of a device
#	boot                Boot a device.
#	clone               Clone an existing device.
#	create              Create a new device.
#	delete              Delete a device or all unavailable devices.
#	erase               Erase a device's contents and settings.
#	get_app_container   Print the path of the installed app's container
#	getenv              Print an environment variable from a running device.
#	icloud_sync         Trigger iCloud sync on a device.
#	install             Install an app on a device.
#	list                List available devices, device types, runtimes, or device pairs.
#	logverbose          enable or disable verbose logging for a device
#	openurl             Open a URL in a device.
#	pair                Create a new watch and phone pair.
#	pair_activate       Set a given pair as active.
#	rename              Rename a device.
#	shutdown            Shutdown a device.
#	terminate           Terminate an application by identifier on a device.
#	uninstall           Uninstall an app from a device.
#	unpair              Unpair a watch and phone pair.
#	upgrade             Upgrade a device to a newer runtime.



# Won't Do:

#	diagnose            Collect diagnostic information and logs.
#	help                Prints the usage for a given subcommand.


class SimulatorControlType(enum.Enum):
    """Which type of simulator control type is it."""

    device_pair = "pair"
    runtime = "runtime"
    device_type = "device_type"
    device = "device"

    def list_key(self):
        """Define the key passed into the list function for the type."""
        # This will need to change if the types ever do, but it holds true for
        # now.
        return self.value + "s"


class SimulatorControlBase:
    """Types defined by simctl should inherit from this."""

    raw_info: Dict[str, Any]
    simctl_type: SimulatorControlType

    def __init__(self, raw_info: Dict[str, Any], simctl_type: SimulatorControlType) -> None:
        self.raw_info = raw_info
        self.simctl_type = simctl_type

    def __eq__(self, other: object) -> bool:
        """Override the default Equals behavior"""

        if not isinstance(other, self.__class__):
            return False

        if not self.simctl_type == other.simctl_type:
            return False

        return self.raw_info == other.raw_info

    def __ne__(self, other: object) -> bool:
        """Define a non-equality test"""
        return not self.__eq__(other)


def _run_command(command: str) -> str:
    """Run an xcrun simctl command."""
    full_command = "xcrun simctl %s" % (command,)
    # Deliberately don't catch the exception - we want it to bubble up
    return subprocess.run(full_command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout

def device_info(device_id: str) -> Optional[Dict[str, Any]]:
    """Return the info for the device with the matching identifier."""
    device_info_map = xcrun.simctl.listall.device_raw_info()
    for operating_system in device_info_map.keys():
        devices = device_info_map[operating_system]
        for device in devices:
            if device["udid"].lower() == device_id.lower():
                return device
    raise xcrun.simctl.device.DeviceNotFoundError("No device with ID: " + device_id)


def get_app_container(device: xcrun.simctl.device.Device, app_identifier: str, container: Optional[str] = None) -> str:
    """Return the path of the installed app's container on the supplied device."""
    command = 'get_app_container "%s" "%s"' % (device.udid, app_identifier)

    if container is not None:
        command += ' "' + container + '"'

    path = _run_command(command)

    # The path has an extra new line at the end, so remove it when returning
    #pylint: disable=unsubscriptable-object
    return path[:-1]
    #pylint: enable=unsubscriptable-object

def openurl(device: xcrun.simctl.device.Device, url: str) -> None:
    """Open a URL in a device."""
    command = 'openurl "%s" "%s"' % (device.udid, url)
    _run_command(command)

def logverbose(device: xcrun.simctl.device.Device, enable: bool) -> None:
    """Enable or disable verbose logging for a device."""
    command = 'logverbose "%s" "%s"' % (device.udid, "enable" if enable else "disable")
    _run_command(command)

def icloud_sync(device: xcrun.simctl.device.Device) -> None:
    """Trigger iCloud sync on a device."""
    command = 'icloud_sync "%s"' % (device.udid,)
    _run_command(command)

def getenv(device: xcrun.simctl.device.Device, variable_name: str) -> str:
    """Return an environment variable from a running device."""
    command = 'getenv "%s" "%s"' % (device.udid, variable_name)
    variable = _run_command(command)
    # The variable has an extra new line at the end, so remove it when returning
    #pylint: disable=unsubscriptable-object
    return variable[:-1]
    #pylint: enable=unsubscriptable-object

def addmedia(device: xcrun.simctl.device.Device, paths: List[str]) -> None:
    """Add photos, live photos, or videos to the photo library of a device."""

    if isinstance(paths, str):
        paths = [paths]

    if not paths:
        return

    command = 'addmedia "%s" ' % (device.udid)

    # Now we need to add the paths
    quoted_paths = ['"' + path + '"' for path in paths]
    paths_arg = " ".join(quoted_paths)
    command += paths_arg

    _run_command(command)

def create_device(name: str, device_type: xcrun.simctl.device_type.DeviceType, runtime: xcrun.simctl.runtime.Runtime):
    """Create a new device, returning the identifier."""
    command = 'create "%s" "%s" "%s"' % (name, device_type.identifier, runtime.identifier)
    device_id = _run_command(command)

    # The device ID has a new line at the end. Strip it when returning.
    #pylint: disable=unsubscriptable-object
    return device_id[:-1]
    #pylint: enable=unsubscriptable-object

def delete_device(device: xcrun.simctl.device.Device) -> None:
    """Delete a device."""
    command = 'delete "%s"' % (device.udid)
    _run_command(command)

def delete_unavailable_devices() -> None:
    """Delete all unavailable devices."""
    _run_command('delete unavailable')

def rename_device(device: xcrun.simctl.device.Device, name: str) -> None:
    """Renames a device."""
    command = 'rename "%s" "%s"' % (device.udid, name)
    _run_command(command)

def boot_device(device: xcrun.simctl.device.Device) -> None:
    """Boots a device."""
    command = 'boot "%s"' % (device.udid,)
    _run_command(command)

def shutdown_device(device: xcrun.simctl.device.Device) -> None:
    """Shuts down a device."""
    command = 'shutdown "%s"' % (device.udid,)
    _run_command(command)

def erase_device(device: xcrun.simctl.device.Device) -> None:
    """Erase a device's contents and settings.."""
    command = 'erase "%s"' % (device.udid,)
    _run_command(command)

def upgrade_device(device: xcrun.simctl.device.Device, runtime: xcrun.simctl.runtime.Runtime) -> None:
    """Upgrade a device to a newer runtime."""
    command = 'upgrade "%s" "%s"' % (device.udid, runtime.identifier)
    _run_command(command)

def clone_device(device: xcrun.simctl.device.Device, new_name: str) -> str:
    """Clone an existing device."""
    command = 'clone "%s" "%s"' % (device.udid, new_name)
    device_id = _run_command(command)

    # The device ID has a new line at the end. Strip it when returning.
    #pylint: disable=unsubscriptable-object
    return device_id[:-1]
    #pylint: enable=unsubscriptable-object

def terminate_app(device: xcrun.simctl.device.Device, app_identifier: str) -> None:
    """Terminate an application by identifier on a device."""
    command = 'terminate "%s" "%s"' % (device.udid, app_identifier)
    _run_command(command)

def install_app(device: xcrun.simctl.device.Device, path: str) -> None:
    """Install an application on device using the path."""
    command = 'install "%s" "%s"' % (device.udid, path)
    _run_command(command)

def uninstall_app(device: xcrun.simctl.device.Device, app_identifier: str) -> None:
    """Uninstall an application by identifier on a device."""
    command = 'uninstall "%s" "%s"' % (device.udid, app_identifier)
    _run_command(command)

def activate_pair(device_pair: xcrun.simctl.device_pair.DevicePair) -> None:
    """Set a given pair as active."""
    command = 'pair_activate "%s"' % (device_pair.identifier,)
    _run_command(command)

def unpair_devices(device_pair: xcrun.simctl.device_pair.DevicePair) -> None:
    """Terminate an application by identifier on a device."""
    command = 'unpair "%s"' % (device_pair.identifier,)
    _run_command(command)

def pair_devices(watch: xcrun.simctl.device.Device, phone: xcrun.simctl.device.Device) -> str:
    """Terminate an application by identifier on a device."""
    command = 'pair "%s" "%s"' % (watch.udid, phone.udid)
    pair_id = _run_command(command)

    # The pair ID has a new line at the end. Strip it when returning.
    #pylint: disable=unsubscriptable-object
    return pair_id[:-1]
    #pylint: enable=unsubscriptable-object
