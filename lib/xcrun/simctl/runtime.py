"""Handles the runtimes for xcrun."""

import xcrun.simctl.listall
import xcrun.simctl.simctl

class RuntimeNotFoundError(Exception):
    """Raised when a requested runtime is not found."""
    pass

class Runtime(object):
    """Represents a runtime for the iOS simulator."""

    def __init__(self, runtime_info):
        """Construct a Runtime object from xcrun output.

        runtime_info: The dictionary representing the xcrun output for a runtime.
        """

        self.raw_info = runtime_info
        self.name = runtime_info["name"]
        self.identifier = runtime_info["identifier"]
        self.version = runtime_info["version"]
        self.availability = runtime_info["availability"]
        self.build_version = runtime_info["buildversion"]

    def __str__(self):
        """Return a string representation of the runtime."""
        return "%s: %s" % (self.name, self.identifier)

    def __repr__(self):
        """Return the raw info of the runtime."""
        return str(self.raw_info)


def from_xcrun_info(info):
    """Create a runtime from the xcrun info."""
    info = info["runtimes"]
    runtimes = []
    for runtime_info in info:
        runtimes.append(Runtime(runtime_info))
    return runtimes


def from_id(identifier):
    """Create a runtime by looking up the existing ones matching the supplied identifier."""
    # Get all runtimes
    all_runtimes = xcrun.simctl.listall.runtimes()

    for runtime in all_runtimes:
        if runtime.identifier == identifier:
            return runtime

    return None
