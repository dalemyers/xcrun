"""Core simctl methods."""

from __future__ import print_function

import subprocess


def _run_command(command):
    """Run an xcrun simctl command."""
    full_command = "xcrun simctl %s" % (command,)
    # Deliberately don't catch the exception - we want it to bubble up
    return subprocess.check_output(full_command, universal_newlines=True, shell=True)


def get_app_container(device, app_identifier, container=None):
    """Return the path of the installed app's container on the supplied device."""
    command = 'get_app_container "%s" "%s"' % (device.udid, app_identifier)

    if container is not None:
        command += ' "' + container + '"'

    path = _run_command(command)

    # The path has an extra new line at the end, so remove it when returning
    return path[:-1]


def openurl(device, url):
    """Open a URL in a device."""
    command = 'openurl "%s" "%s"' % (device.udid, url)
    _run_command(command)

def logverbose(device, enable):
    """Enable or disable verbose logging for a device."""
    command = 'logverbose "%s" "%s"' % (device.udid, "enable" if enable else "disable")
    _run_command(command)

def icloud_sync(device):
    """Trigger iCloud sync on a device."""
    command = 'icloud_sync "%s"' % (device.udid,)
    _run_command(command)

def getenv(device, variable_name):
    """Return an environment variable from a running device."""
    command = 'getenv "%s" "%s"' % (device.udid, variable_name)
    variable = _run_command(command)
    # The variable has an extra new line at the end, so remove it when returning
    return variable[:-1]

def addmedia(device, paths):
    """Add photos, live photos, or videos to the photo library of a device."""

    if isinstance(paths, str):
        paths = [paths]

    if len(paths) == 0:
        return

    command = 'addmedia "%s" ' % (device.udid)

    # Now we need to add the paths
    quoted_paths = ['"' + path + '"' for path in paths]
    paths_arg = " ".join(quoted_paths)
    command += paths_arg

    _run_command(command)

def terminate(device, app_identifier):
    """Terminate an application by identifier on a device."""
    command = 'terminate "%s" "%s"' % (device.udid, app_identifier)
    _run_command(command)

def create_device(name, device_type, runtime):
    """Create a new device."""
    command = 'create "%s" "%s" "%s"' % (name, device_type.identifier, runtime.identifier)
    device_id = _run_command(command)

    # The device ID has a new line at the end. Strip it when returning.
    return device_id[:-1]

def delete_device(device):
    """Delete a device."""
    command = 'delete "%s"' % (device.udid)
    _run_command(command)

def delete_unavailable_devices():
    """Delete all unavailable devices."""
    _run_command('delete unavailable')

def rename_device(device, name):
    """Renames a device."""
    command = 'rename "%s" "%s"' % (device.udid, name)
    _run_command(command)

def boot_device(device):
    """Boots a device."""
    command = 'boot "%s"' % (device.udid,)
    _run_command(command)

def shutdown_device(device):
    """Shuts down a device."""
    command = 'shutdown "%s"' % (device.udid,)
    _run_command(command)

def erase_device(device):
    """Erase a device's contents and settings.."""
    command = 'erase "%s"' % (device.udid,)
    _run_command(command)

def upgrade_device(device, runtime):
    """Upgrade a device to a newer runtime."""
    command = 'upgrade "%s" "%s"' % (device.udid, runtime.identifier)
    _run_command(command)
