"""Handles the runtimes for simctl."""

from typing import Any, Dict, List, Optional

from isim.base_types import SimulatorControlBase, SimulatorControlType

class RuntimeNotFoundError(Exception):
    """Raised when a requested runtime is not found."""

#pylint: disable=too-many-instance-attributes
class Runtime(SimulatorControlBase):
    """Represents a runtime for the iOS simulator."""

    raw_info: Dict[str, Any]
    availability: Optional[str]
    availability_error: str
    build_version: str
    bundle_path: str
    identifier: str
    is_available: bool
    name: str
    version: str

    def __init__(self, runtime_info: Dict[str, Any]) -> None:
        """Construct a Runtime object from simctl output.

        runtime_info: The dictionary representing the simctl output for a runtime.
        """

        super().__init__(runtime_info, SimulatorControlType.runtime)
        self.raw_info = runtime_info
        self.availability = runtime_info.get("availability", None)
        self.availability_error = runtime_info["availabilityError"]
        self.build_version = runtime_info["buildversion"]
        self.bundle_path = runtime_info["bundlePath"].replace("\\/", "/")
        self.identifier = runtime_info["identifier"]
        self.is_available = runtime_info["isAvailable"]
        self.name = runtime_info["name"]
        self.version = runtime_info["version"]

    def __str__(self) -> str:
        """Return a string representation of the runtime."""
        return "%s: %s" % (self.name, self.identifier)

    def __repr__(self) -> str:
        """Return the string programmatic representation of the object."""
        return str(self.raw_info)

    @staticmethod
    def from_simctl_info(info: List[Dict[str, Any]]) -> List['Runtime']:
        """Create a runtime from the simctl info."""
        runtimes = []
        for runtime_info in info:
            runtimes.append(Runtime(runtime_info))
        return runtimes

    @staticmethod
    def from_id(identifier: str) -> 'Runtime':
        """Create a runtime by looking up the existing ones matching the supplied identifier."""
        # Get all runtimes
        for runtime in Runtime.list_all():
            if runtime.identifier == identifier:
                return runtime

        raise RuntimeNotFoundError()

    @staticmethod
    def from_name(name: str) -> 'Runtime':
        """Create a runtime by looking up the existing ones matching the supplied name."""
        for runtime in Runtime.list_all():
            if runtime.name == name:
                return runtime

        raise RuntimeNotFoundError()

    @staticmethod
    def list_all() -> List['Runtime']:
        """Return all available runtimes."""
        runtime_info = SimulatorControlBase.list_type(SimulatorControlType.runtime)
        return Runtime.from_simctl_info(runtime_info)
