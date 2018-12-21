#!/usr/bin/env python3

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

    def test_equality(self):
        """Test that the equality check on device types is accurate."""
        all_device_types = xcrun.simctl.listall.device_types()

        # We need at least 2 device types to test
        self.assertTrue(len(all_device_types) >= 2)

        # Select 2 random ones
        device_type_a, device_type_b = random.sample(all_device_types, 2)

        # They should be different from each other
        self.assertNotEqual(device_type_a, device_type_b)

        # Checking one against something totally different should always be false
        self.assertNotEqual(device_type_a, ["Hello", "World"])

        # Checking one against itself should always be true
        self.assertEqual(device_type_a, device_type_a)

        # Checking a copy of one against itself should always be true
        identifier_copy_a = xcrun.simctl.device_type.from_id(device_type_a.identifier)
        self.assertEqual(device_type_a, identifier_copy_a)

    def test_string_representations(self):
        """Test that the string representations are unique."""
        all_device_types = xcrun.simctl.listall.device_types()
        strings = set([device_type.__str__() for device_type in all_device_types])
        self.assertEqual(len(strings), len(all_device_types))
