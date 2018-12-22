"""Test runtimes."""

import random
import subprocess
import unittest
import uuid

import isim

class TestRuntime(unittest.TestCase):
    """Test the isim runtimes wrapper."""

    def test_from_info(self):
        """Test that we create a runtime correctly from simctl info."""
        fake_runtime = {
            "buildversion" : "ABC123",
            "availability" : "(available)",
            "name" : "iOS 99.0",
            "identifier" : "io.myers.isim.runtime.iOS-99",
            "version" : "99.0"
        }

        fake_runtimes = {
            "runtimes": [fake_runtime]
        }

        runtimes = isim.runtime.from_simctl_info(fake_runtimes)
        self.assertEqual(len(runtimes), 1)
        runtime = runtimes[0]

        self.assertEqual(runtime.name, fake_runtime["name"])
        self.assertEqual(runtime.identifier, fake_runtime["identifier"])
        self.assertEqual(runtime.version, fake_runtime["version"])
        self.assertEqual(runtime.availability, fake_runtime["availability"])
        self.assertEqual(runtime.build_version, fake_runtime["buildversion"])

    def test_from_identifier(self):
        """Test that we can create a runtime reference from an existing runtime identifier."""
        # Get a random runtime
        command = "xcrun simctl list runtimes | tail -n +2 | sed 's/.* - //'"
        runtimes = subprocess.run(command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout
        runtimes = runtimes.split("\n")
        runtimes = [runtime for runtime in runtimes if len(runtime) > 0]
        self.assertTrue(len(runtimes) > 0)

        runtime_identifier = random.choice(runtimes)
        runtime = isim.runtime.from_id(runtime_identifier)

        self.assertIsNotNone(runtime)
        self.assertEqual(runtime.identifier, runtime_identifier)

    def test_from_name(self):
        """Test that we can create a runtime reference from an existing runtime name."""
        # Get a random runtime
        command = "xcrun simctl list runtimes | tail -n +2 | sed -e 's/ (.*//'"
        runtimes = subprocess.run(command, universal_newlines=True, shell=True, check=True, stdout=subprocess.PIPE).stdout
        runtimes = runtimes.split("\n")
        runtimes = [runtime for runtime in runtimes if len(runtime) > 0]
        self.assertTrue(len(runtimes) > 0)

        runtime_name = random.choice(runtimes)
        runtime = isim.runtime.from_name(runtime_name)

        self.assertIsNotNone(runtime)
        self.assertEqual(runtime.name, runtime_name)

    def test_invalid_identifier(self):
        """Test that we don't accidentially match on invalid identifiers."""
        # Identifiers are UUIDs, so let's use something totally different:
        with self.assertRaises(isim.runtime.RuntimeNotFoundError):
            _ = isim.runtime.from_id("Hodor")

    def test_invalid_name(self):
        """Test that we don't accidentially match on invalid names."""
        # It's unlikely that anyone would get the exact same UUID as we generate
        with self.assertRaises(isim.runtime.RuntimeNotFoundError):
            _ = isim.runtime.from_name(str(uuid.uuid4()))

    def test_equality(self):
        """Test that the equality check on runtimes is accurate."""
        all_runtimes = isim.runtime.list_all()

        # We need at least 2 runtimes to test
        self.assertTrue(len(all_runtimes) >= 2)

        # Select 2 random ones
        runtime_a, runtime_b = random.sample(all_runtimes, 2)

        # They should be different from each other
        self.assertNotEqual(runtime_a, runtime_b)

        # Checking one against something totally different should always be false
        self.assertNotEqual(runtime_a, ["Hello", "World"])

        # Checking one against itself should always be true
        self.assertEqual(runtime_a, runtime_a)

        # Checking a copy of one against itself should always be true
        identifier_copy_a = isim.runtime.from_id(runtime_a.identifier)
        self.assertEqual(runtime_a, identifier_copy_a)

    def test_string_representations(self):
        """Test that the string representations are unique."""
        all_runtimes = isim.runtime.list_all()
        strings = {str(runtime) for runtime in all_runtimes}
        self.assertEqual(len(strings), len(all_runtimes))
