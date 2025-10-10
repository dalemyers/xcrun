"""Test devices."""

import os
import subprocess
import sys
import time
import tempfile
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import isim

# pylint: enable=wrong-import-position


class IncompatibleDeviceError(Exception):
    """Raised when a device is incompatible with the runtime."""


class TestDevice(unittest.TestCase):
    """Test device interaction."""

    available_runtimes: list[isim.Runtime] = []
    available_device_types: list[isim.DeviceType] = []

    @classmethod
    def setUpClass(cls):
        TestDevice.available_runtimes = isim.Runtime.list_all()
        TestDevice.available_device_types = isim.DeviceType.list_all()

    def run_device_test(self, available_device_type, available_runtime, callback):
        """Run the tests on a device."""

        # iDevices should run iOS, watch devices should run watchOS, etc.
        if (
            "iPhone" in available_device_type.identifier
            or "iPad" in available_device_type.identifier
            or "iPod" in available_device_type.identifier
        ):
            if "iOS" not in available_runtime.identifier:
                raise IncompatibleDeviceError()
        elif "Apple-Watch" in available_device_type.identifier:
            if "watchOS" not in available_runtime.identifier:
                raise IncompatibleDeviceError()
        elif "Apple-TV" in available_device_type.identifier:
            if "tvOS" not in available_runtime.identifier:
                raise IncompatibleDeviceError()
        else:
            raise ValueError("Unexpected device type: " + available_device_type.identifier)

        device_name = f"Test Device ({uuid.uuid4()})"

        try:
            device = isim.Device.create(device_name, available_device_type, available_runtime)
        except subprocess.CalledProcessError as ex:
            if ex.returncode in [isim.base_types.ErrorCodes.INCOMPATIBLE_DEVICE.value]:
                # This was an incompatible pairing. That's fine since
                # we could be matching watchOS with an iOS device, or
                # an iOS version with an older device, etc.
                raise IncompatibleDeviceError()
            else:
                raise ex

        self.assertIsNotNone(device)
        self.assertEqual(
            device.name,
            device_name,
            f"Name did not match: {device.name}, {device_name}",
        )

        try:
            callback(device)
        finally:
            device.delete()

    def test_installed_devices(self):
        """Test that we can parse all installed devices without error."""
        self.assertIsNotNone(isim.Device.list_all())

    def test_lifecycle(self):
        """Test that we can create new devices in a consistent manner."""

        def callback(device):
            state = "shutdown"
            availability = "(available)"

            self.assertEqual(device.state.lower(), state, "Device was not shutdown as expected")
            if device.availability is not None:
                self.assertEqual(
                    device.availability.lower(),
                    availability,
                    "Device was not available as expected",
                )
            self.assertEqual(
                device.runtime(),
                available_runtime,
                f"Runtimes did not match: {device.runtime()}, {available_runtime}",
            )

        for available_device_type in TestDevice.available_device_types:
            device_tested = False

            for available_runtime in TestDevice.available_runtimes:
                # We only need to test a device once. Doing it any more takes
                # too long
                if device_tested:
                    continue

                try:
                    self.run_device_test(available_device_type, available_runtime, callback)
                    # Mark that this device has been tested at least once
                    device_tested = True
                except IncompatibleDeviceError:
                    pass

    def test_record_video(self):
        """Test that we can record a video of a device."""

        def callback(device) -> bool:
            device.boot()
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, "video.mov")
                device.start_video_recording(video_path)
                time.sleep(10)
                device.stop_video_recording()
                assert os.path.exists(video_path), "Video file was not created"

        for available_device_type in TestDevice.available_device_types:
            for available_runtime in TestDevice.available_runtimes:
                try:
                    self.run_device_test(available_device_type, available_runtime, callback)
                    return
                except IncompatibleDeviceError:
                    # This device is incompatible with the runtime, so skip it
                    continue
