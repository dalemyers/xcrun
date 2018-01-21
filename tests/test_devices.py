#!/usr/bin/env python

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

    def test_lifecycle(self):
        """Test that we can create new devices in a consistent manner."""

        for available_device_type in TestDevice.available_device_types:
            for available_runtime in TestDevice.available_runtimes:

                # iDevices should run iOS, watch devices should run watchOS, etc.
                if "iPhone" in available_device_type.identifier or "iPad" in available_device_type.identifier:
                    if "iOS" not in available_runtime.identifier:
                        continue
                elif "Apple-Watch" in available_device_type.identifier:
                    if "watchOS" not in available_runtime.identifier:
                        continue
                elif "Apple-TV" in available_device_type.identifier:
                    if "tvOS" not in available_runtime.identifier:
                        continue
                else:
                    raise Exception("Unexpected device type: " + available_device_type.identifier)

                device_name = "Test Device (%s)" % (uuid.uuid4(),)
                state = "shutdown"
                availability = "(available)"

                print "DEVICE TYPE:", available_device_type
                print "RUNTIME:", available_runtime

                try:
                    device = xcrun.simctl.device.create(device_name, available_device_type, available_runtime)
                except subprocess.CalledProcessError as ex:
                    if ex.returncode == 162:
                        # This was an incompatible pairing. That's fine since 
                        # we could be matching watchOS with an iOS device, or
                        # an iOS version with an older device, etc.
                        continue
                    else:
                        raise ex

                self.assertIsNotNone(device)
                self.assertEqual(device.name, device_name, "Name did not match: %s, %s" % (device.name, device_name))
                self.assertEqual(device.state.lower(), state, "Device was not shutdown as expected")
                self.assertEqual(device.availability.lower(), availability, "Device was not available as expected")
                self.assertEqual(device.runtime(), available_runtime, "Runtimes did not match: %s, %s" % (device.runtime(), available_runtime))

                device.delete()
