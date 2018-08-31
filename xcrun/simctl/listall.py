"""Used to run `xcrun simctl list X` commands."""

import json
import subprocess

import xcrun.simctl.runtime
import xcrun.simctl.device_type
import xcrun.simctl.device
import xcrun.simctl.device_pair

def _list(item):
    """Run an `xcrun simctl` command with JSON output."""
    full_command = "xcrun simctl list %s --json" % (item,)
    # Deliberately don't catch the exception - we want it to bubble up
    output = subprocess.check_output(full_command, universal_newlines=True, shell=True)
    return json.loads(output)

def runtimes():
    """Return all available runtimes."""
    runtime_info = _list("runtimes")
    return xcrun.simctl.runtime.from_xcrun_info(runtime_info)


def device_types():
    """Return all available device types."""
    device_type_info = _list("devicetypes")
    return xcrun.simctl.device_type.from_xcrun_info(device_type_info)

def devices():
    """Return all available devices."""
    device_info = device_raw_info()
    return xcrun.simctl.device.from_xcrun_info(device_info)

def device_raw_info():
    """Return all device info."""
    return _list("devices")

def device_pairs():
    """Return all available device pairs."""
    device_pair_info = _list("pairs")
    return xcrun.simctl.device_pair.from_xcrun_info(device_pair_info)
