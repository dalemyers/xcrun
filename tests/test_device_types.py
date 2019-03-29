"""Test device types."""

import os
import random
import subprocess
import sys
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import isim
#pylint: enable=wrong-import-position


class TestDeviceTypes(unittest.TestCase):
    """Test the device types wrapper."""

    def test_installed_device_types(self):
        """Test that we can parse all installed runtimes without error."""
        self.assertIsNotNone(isim.Runtime.list_all())

    def test_from_info(self):
        """Test that we create a device type correctly from simctl info."""

        #pylint: disable=line-too-long
        fake_device_type = {
            "name": "Apple Fridge 1.0",
            "bundlePath": "\\/Applications\\/Xcode_10.1.app\\/Contents\\/Developer\\/Platforms\\/WatchOS.platform\\/Developer\\/Library\\/CoreSimulator\\/Profiles\\/DeviceTypes\\/Apple Watch Series 4 - 40mm.simdevicetype",
            "identifier": "io.myers.isim.device-type.Apple-Fridge"
        }
        #pylint: enable=line-too-long

        device_types = isim.DeviceType.from_simctl_info([fake_device_type])
        self.assertEqual(len(device_types), 1)
        device_type = device_types[0]

        self.assertEqual(device_type.name, fake_device_type["name"])
        self.assertEqual(device_type.bundle_path, fake_device_type["bundlePath"].replace("\\/", "/"))
        self.assertEqual(device_type.identifier, fake_device_type["identifier"])

    def test_from_identifier(self):
        """Test that we can create a device type reference from an existing device type
        identifier.
        """

        # Get a random device type identifier
        command = "xcrun simctl list devicetypes | tail -n +2 | sed 's/.* (\\(.*\\))/\\1/'"
        device_type_identifiers = subprocess.run(command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout

        device_type_identifiers = device_type_identifiers.split("\n")
        device_type_identifiers = [identifier for identifier in device_type_identifiers
                                   if len(identifier) > 0]
        self.assertTrue(len(device_type_identifiers) > 0)

        device_type_identifier = random.choice(device_type_identifiers)
        device_type = isim.DeviceType.from_id(device_type_identifier)

        self.assertIsNotNone(device_type)
        self.assertEqual(device_type.identifier, device_type_identifier)

    def test_from_name(self):
        """Test that we can create a device type reference from an existing device type name."""
        # Get a random device type name
        command = "xcrun simctl list devicetypes | tail -n +2 | sed 's/\\(.*\\) (.*)/\\1/'"
        device_type_names = subprocess.run(command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout
        device_type_names = device_type_names.split("\n")
        device_type_names = [name for name in device_type_names if len(name) > 0]
        self.assertTrue(len(device_type_names) > 0)

        device_type_name = random.choice(device_type_names)
        device_type = isim.DeviceType.from_name(device_type_name)

        self.assertIsNotNone(device_type)
        self.assertEqual(device_type.name, device_type_name)

    def test_invalid_identifier(self):
        """Test that we don't accidentially match on invalid identifiers."""
        # Identifiers are UUIDs, so let's use something totally different:
        with self.assertRaises(isim.DeviceTypeNotFoundError):
            _ = isim.DeviceType.from_id("Hodor")

    def test_invalid_name(self):
        """Test that we don't accidentially match on invalid names."""
        # It's unlikely that anyone would get the exact same UUID as we generate
        with self.assertRaises(isim.DeviceTypeNotFoundError):
            _ = isim.DeviceType.from_name(str(uuid.uuid4()))

    def test_equality(self):
        """Test that the equality check on device types is accurate."""
        all_device_types = isim.DeviceType.list_all()

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
        identifier_copy_a = isim.DeviceType.from_id(device_type_a.identifier)
        self.assertEqual(device_type_a, identifier_copy_a)

    def test_string_representations(self):
        """Test that the string representations are unique."""
        all_device_types = isim.DeviceType.list_all()
        strings = {str(device_type) for device_type in all_device_types}
        self.assertEqual(len(strings), len(all_device_types))
