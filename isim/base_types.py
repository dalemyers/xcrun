"""Base types for `xcrun simctl`."""

import enum
import json
from typing import Any, Dict
import subprocess


class ErrorCodes(enum.Enum):
    """Simple lookup for all known error codes."""

    # Tried to access a file or directory (such as by searching for an app
    # container) that doesn't exist
    no_such_file_or_directory = 2

    # Trying to perform an action on a device type, but supplied an invalid
    # device type
    invalid_device_type = 161

    # Tried to perform an action on the device, but there was an
    # incompatibility, such as when trying to create a new Apple TV device with
    # a watchOS runtime.
    incompatible_device = 162

    # The device was in a state where it can't be shutdown. e.g. already
    # shutdown
    unable_to_shutdown_device_in_current_state = 164

class SimulatorControlType(enum.Enum):
    """Which type of simulator control type is it."""

    device_pair = "pair"
    runtime = "runtime"
    device_type = "device_type"
    device = "device"

    def list_key(self):
        """Define the key passed into the list function for the type."""
        # Disable this false positive
        #pylint: disable=comparison-with-callable
        if self.name == "device_type":
            return "devicetypes"
        #pylint: enable=comparison-with-callable
        return self.value + "s"


class SimulatorControlBase:
    """Types defined by simctl should inherit from this."""

    raw_info: Dict[str, Any]
    simctl_type: SimulatorControlType

    def __init__(self, raw_info: Dict[str, Any], simctl_type: SimulatorControlType) -> None:
        self.raw_info = raw_info
        self.simctl_type = simctl_type

    #pylint: disable=no-self-use
    def _run_command(self, command: str) -> str:
        """Convenience method for running an xcrun simctl command."""
        return SimulatorControlBase.run_command(command)
    #pylint: enable=no-self-use

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

    @staticmethod
    def run_command(command: str) -> str:
        """Run an xcrun simctl command."""
        full_command = "xcrun simctl %s" % (command,)
        # Deliberately don't catch the exception - we want it to bubble up
        return subprocess.run(full_command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout

    @staticmethod
    def list_type(item: SimulatorControlType) -> Any:
        """Run an `xcrun simctl` command with JSON output."""
        full_command = "xcrun simctl list %s --json" % (item.list_key(),)
        # Deliberately don't catch the exception - we want it to bubble up
        output = subprocess.run(full_command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout

        json_output = json.loads(output)

        if not isinstance(json_output, dict):
            raise Exception("Unexpected list type: " + str(type(json_output)))

        if not json_output.get(item.list_key()):
            raise Exception("Unexpected format for " + item.list_key() + " list type: " + str(json_output))

        return json_output[item.list_key()]
