"""Test devices using pytest."""

import os
import subprocess
import tempfile
import time
from typing import Generator
import uuid

import pytest

import isim


@pytest.fixture(scope="module", name="all_runtimes")
def fixture_all_runtimes() -> list[isim.Runtime]:
    """Fixture to get all available runtimes once per module."""
    return isim.Runtime.list_all()


@pytest.fixture(scope="module", name="all_device_types")
def fixture_all_device_types() -> list[isim.DeviceType]:
    """Fixture to get all available device types once per module."""
    return isim.DeviceType.list_all()


@pytest.fixture(scope="module", name="compatible_device_runtime")
def fixture_compatible_device_runtime(
    all_runtimes: list[isim.Runtime], all_device_types: list[isim.DeviceType]
) -> tuple[isim.DeviceType, isim.Runtime]:
    """Find a compatible device type and runtime pair for testing."""
    # Try to find an iPhone with iOS runtime
    for device_type in all_device_types:
        if "iPhone" not in device_type.identifier:
            continue
        for runtime in all_runtimes:
            if "iOS" not in runtime.identifier:
                continue
            return device_type, runtime

    # Fallback: try any compatible pair
    for device_type in all_device_types:
        for runtime in all_runtimes:
            if _is_compatible(device_type, runtime):
                return device_type, runtime

    pytest.skip("No compatible device type and runtime pair found")


@pytest.fixture(name="test_device")
def fixture_test_device(
    compatible_device_runtime: tuple[isim.DeviceType, isim.Runtime],
) -> Generator[isim.Device]:
    """Create a test device and clean it up after the test."""
    device_type, runtime = compatible_device_runtime
    device_name = f"Test Device ({uuid.uuid4()})"

    try:
        device = isim.Device.create(device_name, device_type, runtime)
    except subprocess.CalledProcessError as ex:
        if (
            ex.returncode
            # pylint: disable=line-too-long
            == isim.base_types.ErrorCodes.INCOMPATIBLE_DEVICE.value  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
            # pylint: enable=line-too-long
        ):
            pytest.skip("Incompatible device/runtime combination")
        raise

    yield device

    # Cleanup
    try:
        device.delete()
    except Exception:
        # Device might already be deleted or in bad state
        pass


def _is_compatible(device_type: isim.DeviceType, runtime: isim.Runtime) -> bool:
    """Check if a device type and runtime are compatible."""
    if (
        "iPhone" in device_type.identifier
        or "iPad" in device_type.identifier
        or "iPod" in device_type.identifier
    ):
        return "iOS" in runtime.identifier

    if "Apple-Watch" in device_type.identifier:
        return "watchOS" in runtime.identifier

    if "Apple-TV" in device_type.identifier:
        return "tvOS" in runtime.identifier

    return False


def test_list_installed_devices() -> None:
    """Test that we can parse all installed devices without error."""
    devices = isim.Device.list_all()
    assert devices is not None
    assert isinstance(devices, dict)


def test_create_and_delete_device(
    compatible_device_runtime: tuple[isim.DeviceType, isim.Runtime],
) -> None:
    """Test that we can create and delete a device."""
    device_type, runtime = compatible_device_runtime
    device_name = f"Test Device ({uuid.uuid4()})"

    try:
        device = isim.Device.create(device_name, device_type, runtime)
    except subprocess.CalledProcessError as ex:
        if (
            ex.returncode
            # pylint: disable=line-too-long
            == isim.base_types.ErrorCodes.INCOMPATIBLE_DEVICE.value  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
            # pylint: enable=line-too-long
        ):
            pytest.skip("Incompatible device/runtime combination")
        raise

    try:
        assert device is not None
        assert device.name == device_name
        assert device.udid
        assert isinstance(device.udid, str)
    finally:
        device.delete()


def test_device_lifecycle(test_device: isim.Device) -> None:
    """Test that we can create new devices in a consistent manner."""
    assert test_device.state.lower() == "shutdown", "Device should start shutdown"

    if test_device.availability is not None:
        assert test_device.availability.lower() == "(available)", "Device should be available"


def test_device_runtime(
    test_device: isim.Device, compatible_device_runtime: tuple[isim.DeviceType, isim.Runtime]
) -> None:
    """Test that device runtime matches expected runtime."""
    _, expected_runtime = compatible_device_runtime
    device_runtime = test_device.runtime()
    assert device_runtime == expected_runtime


def test_device_type(
    test_device: isim.Device, compatible_device_runtime: tuple[isim.DeviceType, isim.Runtime]
) -> None:
    """Test that device type matches expected type."""
    expected_device_type, _ = compatible_device_runtime
    device_type = test_device.device_type()
    assert device_type == expected_device_type


def test_device_from_identifier(test_device: isim.Device) -> None:
    """Test that we can retrieve a device by its identifier."""
    retrieved = isim.Device.from_identifier(test_device.udid)
    assert retrieved is not None
    assert retrieved.udid == test_device.udid
    assert retrieved.name == test_device.name


def test_device_rename(test_device: isim.Device) -> None:
    """Test that we can rename a device."""
    new_name = f"Renamed Device ({uuid.uuid4()})"
    test_device.rename(new_name)
    test_device.refresh_state()
    assert test_device.name == new_name


def test_device_clone(test_device: isim.Device) -> None:
    """Test that we can clone a device."""
    clone_name = f"Cloned Device ({uuid.uuid4()})"
    clone_udid = test_device.clone(clone_name)

    try:
        assert clone_udid
        assert isinstance(clone_udid, str)
        assert clone_udid != test_device.udid

        # Verify the clone exists
        cloned_device = isim.Device.from_identifier(clone_udid)
        assert cloned_device.name == clone_name
    finally:
        # Clean up the clone
        try:
            cloned_device = isim.Device.from_identifier(clone_udid)
            cloned_device.delete()
        except Exception:
            pass


def test_device_boot_and_shutdown(test_device: isim.Device) -> None:
    """Test that we can boot and shutdown a device."""
    # Boot the device
    test_device.boot()
    test_device.refresh_state()
    assert test_device.state.lower() in ["booting", "booted"]

    # Wait for boot to complete
    max_wait = 60
    start_time = time.time()
    while time.time() - start_time < max_wait:
        test_device.refresh_state()
        if test_device.state.lower() == "booted":
            break
        time.sleep(1)

    # Shutdown
    test_device.shutdown()
    test_device.refresh_state()
    assert test_device.state.lower() in ["shutting down", "shutdown"]


def test_device_erase(test_device: isim.Device) -> None:
    """Test that we can erase a device."""
    test_device.erase()
    test_device.refresh_state()
    # After erase, device should still exist
    assert test_device.udid


@pytest.mark.slow
def test_record_video(test_device: isim.Device) -> None:
    """Test that we can record a video of a device."""
    # Boot the device first
    test_device.boot()
    test_device.refresh_state()

    # Wait for device to boot
    max_wait = 60
    start_time = time.time()
    while time.time() - start_time < max_wait:
        test_device.refresh_state()
        if test_device.state.lower() == "booted":
            break
        time.sleep(1)

    assert test_device.state.lower() == "booted", "Device must be booted to record video"

    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, "test_video.mov")

        test_device.start_video_recording(video_path)
        time.sleep(5)  # Record for 5 seconds
        test_device.stop_video_recording()

        assert os.path.exists(video_path), "Video file should be created"
        assert os.path.getsize(video_path) > 0, "Video file should not be empty"


def test_device_screenshot(test_device: isim.Device) -> None:
    """Test that we can take a screenshot of a device."""
    with tempfile.TemporaryDirectory() as temp_dir:
        screenshot_path = os.path.join(temp_dir, "screenshot.png")
        test_device.screenshot(screenshot_path)

        assert os.path.exists(screenshot_path), "Screenshot file should be created"
        assert os.path.getsize(screenshot_path) > 0, "Screenshot should not be empty"


def test_device_attributes(test_device: isim.Device) -> None:
    """Test that device objects have expected attributes."""
    assert hasattr(test_device, "udid")
    assert hasattr(test_device, "name")
    assert hasattr(test_device, "state")
    assert hasattr(test_device, "runtime_id")
    assert hasattr(test_device, "device_type_id")
    assert hasattr(test_device, "is_available")

    # Check types
    assert isinstance(test_device.udid, str)
    assert isinstance(test_device.name, str)
    assert isinstance(test_device.state, str)
    assert isinstance(test_device.runtime_id, str)
    assert isinstance(test_device.device_type_id, str)


def test_device_str_repr(test_device: isim.Device) -> None:
    """Test string representations of devices."""
    str_repr = str(test_device)
    assert test_device.name in str_repr
    assert test_device.udid in str_repr

    repr_str = repr(test_device)
    assert "runtime_id" in repr_str


def test_delete_unavailable_devices() -> None:
    """Test that we can delete unavailable devices."""
    # This should not raise an error
    isim.Device.delete_unavailable()


def test_refresh_state(test_device: isim.Device) -> None:
    """Test that we can refresh device state."""
    _ = test_device.state
    test_device.refresh_state()
    # State should still be valid after refresh
    assert test_device.state
    assert isinstance(test_device.state, str)
