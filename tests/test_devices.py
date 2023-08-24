"""Test devices."""

import os
import subprocess
import sys
from typing import List
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import isim

# pylint: enable=wrong-import-position


class TestDevice(unittest.TestCase):
    """Test device interaction."""

    available_runtimes: List[isim.Runtime] = []
    available_device_types: List[isim.DeviceType] = []

    @classmethod
    def setUpClass(cls):
        TestDevice.available_runtimes = isim.Runtime.list_all()
        TestDevice.available_device_types = isim.DeviceType.list_all()

    def run_device_test(self, available_device_type, available_runtime):
        """Run the tests on a device."""

        # iDevices should run iOS, watch devices should run watchOS, etc.
        if (
            "iPhone" in available_device_type.identifier
            or "iPad" in available_device_type.identifier
            or "iPod" in available_device_type.identifier
        ):
            if "iOS" not in available_runtime.identifier:
                return False
        elif "Apple-Watch" in available_device_type.identifier:
            if "watchOS" not in available_runtime.identifier:
                return False
        elif "Apple-TV" in available_device_type.identifier:
            if "tvOS" not in available_runtime.identifier:
                return False
        else:
            raise ValueError("Unexpected device type: " + available_device_type.identifier)

        device_name = f"Test Device ({uuid.uuid4()})"
        state = "shutdown"
        availability = "(available)"

        try:
            device = isim.Device.create(device_name, available_device_type, available_runtime)
        except subprocess.CalledProcessError as ex:
            if ex.returncode in [isim.base_types.ErrorCodes.INCOMPATIBLE_DEVICE.value]:
                # This was an incompatible pairing. That's fine since
                # we could be matching watchOS with an iOS device, or
                # an iOS version with an older device, etc.
                return False

            raise ex

        self.assertIsNotNone(device)
        self.assertEqual(
            device.name, device_name, f"Name did not match: {device.name}, {device_name}"
        )
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

        device.delete()

        return True

    def test_installed_devicess(self):
        """Test that we can parse all installed devices without error."""
        self.assertIsNotNone(isim.Device.list_all())

    def test_lifecycle(self):
        """Test that we can create new devices in a consistent manner."""

        for available_device_type in TestDevice.available_device_types:
            device_tested = False

            for available_runtime in TestDevice.available_runtimes:
                # We only need to test a device once. Doing it any more takes
                # too long
                if device_tested:
                    continue

                if self.run_device_test(available_device_type, available_runtime):
                    # Mark that this device has been tested at least once
                    device_tested = True
