"""Handles the runtimes for simctl."""

from typing import Any, Dict, List

import isim

class RuntimeNotFoundError(Exception):
    """Raised when a requested runtime is not found."""

class Runtime(isim.SimulatorControlBase):
    """Represents a runtime for the iOS simulator."""

    raw_info: Dict[str, Any]
    name: str
    identifier: str
    version: str
    availability: str
    build_version: str

    def __init__(self, runtime_info: Dict[str, Any]) -> None:
        """Construct a Runtime object from simctl output.

        runtime_info: The dictionary representing the simctl output for a runtime.
        """

        super().__init__(runtime_info, isim.SimulatorControlType.runtime)
        self.raw_info = runtime_info
        self.name = runtime_info["name"]
        self.identifier = runtime_info["identifier"]
        self.version = runtime_info["version"]
        self.availability = runtime_info["availability"]
        self.build_version = runtime_info["buildversion"]

    def __str__(self) -> str:
        """Return a string representation of the runtime."""
        return "%s: %s" % (self.name, self.identifier)


def from_simctl_info(info: List[Dict[str, Any]]) -> List[Runtime]:
    """Create a runtime from the simctl info."""
    runtimes = []
    for runtime_info in info:
        runtimes.append(Runtime(runtime_info))
    return runtimes


def from_id(identifier: str) -> Runtime:
    """Create a runtime by looking up the existing ones matching the supplied identifier."""
    # Get all runtimes
    for runtime in list_all():
        if runtime.identifier == identifier:
            return runtime

    raise RuntimeNotFoundError()

def from_name(name: str) -> Runtime:
    """Create a runtime by looking up the existing ones matching the supplied name."""
    for runtime in list_all():
        if runtime.name == name:
            return runtime

    raise RuntimeNotFoundError()


def list_all() -> List[Runtime]:
    """Return all available runtimes."""
    runtime_info = isim.list_type(isim.SimulatorControlType.runtime)
    return from_simctl_info(runtime_info)
