#!/usr/bin/env python3

import subprocess
import unittest
import uuid

import xcrun.simctl


class TestDevice(unittest.TestCase):
    """Test device interaction."""

    available_runtimes = []
    available_device_types = []

    @classmethod
    def setUpClass(cls):
        TestDevice.available_runtimes = xcrun.simctl.listall.runtimes()
        TestDevice.available_device_types = xcrun.simctl.listall.device_types()


    def run_device_test(self, available_device_type, available_runtime):
        """Run the tests on a device."""

        # iDevices should run iOS, watch devices should run watchOS, etc.
        if "iPhone" in available_device_type.identifier or "iPad" in available_device_type.identifier:
            if "iOS" not in available_runtime.identifier:
                return False
        elif "Apple-Watch" in available_device_type.identifier:
            if "watchOS" not in available_runtime.identifier:
                return False
        elif "Apple-TV" in available_device_type.identifier:
            if "tvOS" not in available_runtime.identifier:
                return False
        else:
            raise Exception("Unexpected device type: " + available_device_type.identifier)

        device_name = "Test Device (%s)" % (uuid.uuid4(),)
        state = "shutdown"
        availability = "(available)"

        try:
            device = xcrun.simctl.device.create(device_name, available_device_type, available_runtime)
        except subprocess.CalledProcessError as ex:
            if ex.returncode == 162:
                # This was an incompatible pairing. That's fine since
                # we could be matching watchOS with an iOS device, or
                # an iOS version with an older device, etc.
                return False
            else:
                raise ex

        self.assertIsNotNone(device)
        self.assertEqual(device.name, device_name, "Name did not match: %s, %s" % (device.name, device_name))
        self.assertEqual(device.state.lower(), state, "Device was not shutdown as expected")
        self.assertEqual(device.availability.lower(), availability, "Device was not available as expected")
        self.assertEqual(
            device.runtime(),
            available_runtime,
            "Runtimes did not match: %s, %s" % (device.runtime(), available_runtime)
        )

        device.delete()

        return True

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
