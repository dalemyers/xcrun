"""Used to run `xcrun simctl list X` commands."""

import json
import subprocess
from typing import Any, Dict, List

import isim.runtime
import isim.device_type
import isim.device
import isim.device_pair

def _list(item: str) -> Any:
    """Run an `xcrun simctl` command with JSON output."""
    full_command = "xcrun simctl list %s --json" % (item,)
    # Deliberately don't catch the exception - we want it to bubble up
    output = subprocess.run(full_command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout

    json_output = json.loads(output)

    if not isinstance(json_output, dict):
        raise Exception("Unexpected list type: " + str(type(json_output)))

    if not json_output.get(item):
        raise Exception("Unexpected format for " + item + " list type: " + str(json_output))

    return json_output[item]

def runtimes() -> List[isim.runtime.Runtime]:
    """Return all available runtimes."""
    runtime_info = _list(isim.SimulatorControlType.runtime.list_key())
    return isim.runtime.from_simctl_info(runtime_info)


def device_types() -> List[isim.device_type.DeviceType]:
    """Return all available device types."""
    device_type_info = _list(isim.SimulatorControlType.device_type.list_key())
    return isim.device_type.from_simctl_info(device_type_info)

def devices() -> Dict[str, List[isim.device.Device]]:
    """Return all available devices."""
    device_info = device_raw_info()
    return isim.device.from_simctl_info(device_info)

def device_raw_info() -> Dict[str, List[Dict[str, Any]]]:
    """Return all device info."""
    return _list(isim.SimulatorControlType.device.list_key())

def device_pairs() -> List[isim.device_pair.DevicePair]:
    """Return all available device pairs."""
    device_pair_info = _list(isim.SimulatorControlType.device_pair.list_key())
    return isim.device_pair.from_simctl_info(device_pair_info)
