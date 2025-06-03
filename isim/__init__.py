"""Wrapper around `xcrun simctl`."""

import os
import shlex
import subprocess

from isim.device import Device, DeviceNotFoundError
from isim.device_pair import DevicePair
from isim.device_type import DeviceType, DeviceTypeNotFoundError
from isim.runtime import Runtime, RuntimeNotFoundError

# Advanced:

# 	pbsync              Sync the pasteboard content from one pasteboard to another.
# 	pbcopy              Copy standard input onto the device pasteboard.
# 	pbpaste             Print the contents of the device's pasteboard to standard output.
# 	io                  Set up a device IO operation.
# 	spawn               Spawn a process on a device.
# 	launch              Launch an application by identifier on a device.


# DONE:

# 	addmedia            Add photos, live photos, or videos to the photo library of a device
# 	boot                Boot a device.
# 	clone               Clone an existing device.
# 	create              Create a new device.
# 	delete              Delete a device or all unavailable devices.
# 	erase               Erase a device's contents and settings.
# 	get_app_container   Print the path of the installed app's container
# 	getenv              Print an environment variable from a running device.
# 	icloud_sync         Trigger iCloud sync on a device.
# 	install             Install an app on a device.
# 	list                List available devices, device types, runtimes, or device pairs.
# 	logverbose          enable or disable verbose logging for a device
# 	openurl             Open a URL in a device.
# 	pair                Create a new watch and phone pair.
# 	pair_activate       Set a given pair as active.
# 	rename              Rename a device.
# 	shutdown            Shutdown a device.
# 	terminate           Terminate an application by identifier on a device.
# 	uninstall           Uninstall an app from a device.
# 	unpair              Unpair a watch and phone pair.
# 	upgrade             Upgrade a device to a newer runtime.


# Won't Do:

# 	help                Prints the usage for a given subcommand.


def diagnose(
    *,
    output_path: str,
    all_logs: bool = False,
    include_data_directory: bool = False,
    archive: bool = True,
    timeout: int = 300,
    udids: list[str] | str | None = None,
) -> str:
    """Run the xcrun simctl diagnose command.

    By default, this will run only for booted devices. Set all_logs to True to
    gather data for non-booted devices.

    To include the data directory, set include_data_directory to True.

    If udid is set, it will only connect diagnostics from that device. However,
    if all_logs is set, that will override this setting.

    Returns the location of the archive.
    """

    output_archive = f"{output_path}.tar.gz"

    if os.path.exists(output_path):
        raise FileExistsError("The output directory already exists")

    if os.path.exists(output_archive):
        raise FileExistsError(f'The output archive file already exists: "{output_archive}"')

    # I'm not entirely sure what the '-l' flag does. It's not documented, but if
    # I don't set it, the command just waits forever without doing anything.
    # LinkedIn use this flag for their Bluepill tool.
    full_command = [
        "xcrun",
        "simctl",
        "diagnose",
        "-l",
        "-b",
        f"--timeout={timeout}",
        f"--output={shlex.quote(output_path)}",
    ]

    if not archive:
        full_command.append("--no-archive")

    if include_data_directory:
        full_command.append("--data-container")

    if all_logs:
        full_command.append("--all-logs")

    if udids is not None:
        if isinstance(udids, str):
            full_command.append(f"--udid={udids}")
        else:
            full_command += [f"--udid={udid}" for udid in udids]

    command_string = " ".join(full_command)

    # Let the exception bubble up
    _ = subprocess.run(
        command_string,
        universal_newlines=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )

    return output_archive
