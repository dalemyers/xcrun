#!/usr/bin/env python

import random
import subprocess
import unittest
import uuid

import xcrun.simctl

class TestDeviceTypes(unittest.TestCase):
    """Test the device types wrapper."""

    def test_from_info(self):
        """Test that we create a device type correctly from xcrun info."""
        fake_device_type = {
            "name" : "Apple Fridge 1.0",
            "identifier" : "io.myers.xcrun.device-type.Apple-Fridge"
        }

        fake_device_types = {
            "devicetypes": [fake_device_type]
        }

        device_types = xcrun.simctl.device_type.from_xcrun_info(fake_device_types)
        self.assertEqual(len(device_types), 1)
        device_type = device_types[0]

        self.assertEqual(device_type.name, fake_device_type["name"])
        self.assertEqual(device_type.identifier, fake_device_type["identifier"])

    def test_from_identifier(self):
        """Test that we can create a device type reference from an existing device type
        identifier.
        """

        # Get a random device type identifier
        command = "xcrun simctl list devicetypes | tail -n +2 | sed 's/.* (\\(.*\\))/\\1/'"
        device_type_identifiers = subprocess.check_output(
            command, universal_newlines=True, shell=True)
        device_type_identifiers = device_type_identifiers.split("\n")
        device_type_identifiers = [identifier for identifier in device_type_identifiers
                                   if len(identifier) > 0]
        self.assertTrue(len(device_type_identifiers) > 0)

        device_type_identifier = random.choice(device_type_identifiers)
        device_type = xcrun.simctl.device_type.from_id(device_type_identifier)

        self.assertIsNotNone(device_type)
        self.assertEqual(device_type.identifier, device_type_identifier)

    def test_from_name(self):
        """Test that we can create a device type reference from an existing device type name."""
        # Get a random device type name
        command = "xcrun simctl list devicetypes | tail -n +2 | sed 's/\\(.*\\) (.*)/\\1/'"
        device_type_names = subprocess.check_output(command, universal_newlines=True, shell=True)
        device_type_names = device_type_names.split("\n")
        device_type_names = [name for name in device_type_names if len(name) > 0]
        self.assertTrue(len(device_type_names) > 0)

        device_type_name = random.choice(device_type_names)
        device_type = xcrun.simctl.device_type.from_name(device_type_name)

        self.assertIsNotNone(device_type)
        self.assertEqual(device_type.name, device_type_name)

    def test_invalid_identifier(self):
        """Test that we don't accidentially match on invalid identifiers."""
        # Identifiers are UUIDs, so let's use something totally different:
        with self.assertRaises(xcrun.simctl.device_type.DeviceTypeNotFoundError):
            _ = xcrun.simctl.device_type.from_id("Hodor")

    def test_invalid_name(self):
        """Test that we don't accidentially match on invalid names."""
        # It's unlikely that anyone would get the exact same UUID as we generate
        with self.assertRaises(xcrun.simctl.device_type.DeviceTypeNotFoundError):
            _ = xcrun.simctl.device_type.from_name(str(uuid.uuid4()))
