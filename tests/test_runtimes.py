"""Test runtimes using pytest."""

import uuid

import pytest

import isim


@pytest.fixture(scope="module")
def all_runtimes():
    """Fixture to get all available runtimes once per module."""
    return isim.Runtime.list_all()


def test_from_info():
    """Test that we create a runtime correctly from simctl info."""
    fake_runtime = {
        "availability": "(available)",
        "buildversion": "ABC123",
        "bundlePath": (
            "\\/Applications\\/Xcode_10.1.app\\/Contents\\/Developer\\/Platforms\\/"
            "iPhoneOS.platform\\/Developer\\/Library\\/CoreSimulator\\/Profiles\\/"
            "Runtimes\\/iOS.simruntime"
        ),
        "identifier": "io.myers.isim.runtime.iOS-99",
        "isAvailable": True,
        "name": "iOS 99.0",
        "version": "99.0",
    }

    runtimes = isim.Runtime.from_simctl_info([fake_runtime])
    assert len(runtimes) == 1
    
    runtime = runtimes[0]
    assert (
        runtime.availability == fake_runtime["availability"]
        or runtime.availability is None
    )
    assert runtime.build_version == fake_runtime["buildversion"]
    assert runtime.bundle_path == fake_runtime["bundlePath"].replace("\\/", "/")
    assert runtime.identifier == fake_runtime["identifier"]
    assert runtime.is_available == fake_runtime["isAvailable"]
    assert runtime.name == fake_runtime["name"]
    assert runtime.version == fake_runtime["version"]


def test_list_installed_runtimes(all_runtimes):
    """Test that we can parse all installed runtimes without error."""
    assert all_runtimes is not None
    assert len(all_runtimes) > 0, "Should have at least one runtime installed"


def test_from_identifier(all_runtimes):
    """Test that we can create a runtime reference from an existing runtime identifier."""
    assert len(all_runtimes) > 0, "Need at least one runtime to test"
    
    # Get a runtime identifier from the list
    runtime_identifier = all_runtimes[0].identifier
    runtime = isim.Runtime.from_id(runtime_identifier)
    
    assert runtime is not None
    assert runtime.identifier == runtime_identifier


def test_from_name(all_runtimes):
    """Test that we can create a runtime reference from an existing runtime name."""
    assert len(all_runtimes) > 0, "Need at least one runtime to test"
    
    # Get a runtime name from the list
    runtime_name = all_runtimes[0].name
    runtime = isim.Runtime.from_name(runtime_name)
    
    assert runtime is not None
    assert runtime.name == runtime_name


def test_invalid_identifier():
    """Test that we don't accidentally match on invalid identifiers."""
    with pytest.raises(isim.RuntimeNotFoundError):
        isim.Runtime.from_id("Hodor")


def test_invalid_name():
    """Test that we don't accidentally match on invalid names."""
    # It's unlikely that anyone would get the exact same UUID as we generate
    with pytest.raises(isim.RuntimeNotFoundError):
        isim.Runtime.from_name(str(uuid.uuid4()))


def test_equality(all_runtimes):
    """Test that the equality check on runtimes is accurate."""
    # We need at least 2 runtimes to test
    assert len(all_runtimes) >= 2, "Need at least 2 runtimes for equality testing"
    
    runtime_a = all_runtimes[0]
    runtime_b = all_runtimes[1]
    
    # They should be different from each other
    assert runtime_a != runtime_b
    
    # Checking one against something totally different should always be false
    assert runtime_a != ["Hello", "World"]
    
    # Checking one against itself should always be true
    assert runtime_a == runtime_a  # noqa: PLR0124
    
    # Checking a copy of one against itself should always be true
    identifier_copy_a = isim.Runtime.from_id(runtime_a.identifier)
    assert runtime_a == identifier_copy_a


def test_string_representations(all_runtimes):
    """Test that all runtimes have string representations."""
    # Note: Multiple runtime builds can have the same name/identifier
    # (e.g., different beta builds of iOS 26.0)
    for runtime in all_runtimes:
        str_repr = str(runtime)
        assert str_repr  # Not empty
        assert runtime.name in str_repr
        assert runtime.identifier in str_repr


def test_runtime_attributes(all_runtimes):
    """Test that runtime objects have expected attributes."""
    assert len(all_runtimes) > 0
    
    runtime = all_runtimes[0]
    assert hasattr(runtime, "identifier")
    assert hasattr(runtime, "name")
    assert hasattr(runtime, "version")
    assert hasattr(runtime, "build_version")
    assert hasattr(runtime, "bundle_path")
    assert hasattr(runtime, "is_available")
    
    # Check types
    assert isinstance(runtime.identifier, str)
    assert isinstance(runtime.name, str)
    assert isinstance(runtime.version, str)
    assert isinstance(runtime.build_version, str)
    assert isinstance(runtime.bundle_path, str)
    assert isinstance(runtime.is_available, bool)
