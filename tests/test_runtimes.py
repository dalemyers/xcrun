#!/usr/bin/env python

import random
import subprocess
import unittest
import uuid

import xcrun

class TestRuntime(unittest.TestCase):
    """Test the xcrun runtimes wrapper."""

    def test_from_info(self):
        """Test that we create a runtime correctly from xcrun info."""
        fake_runtime = {
            "buildversion" : "ABC123",
            "availability" : "(available)",
            "name" : "iOS 99.0",
            "identifier" : "io.myers.xcrun.runtime.iOS-99",
            "version" : "99.0"
        }

        fake_runtimes = {
            "runtimes": [fake_runtime]
        }

        runtimes = xcrun.simctl.runtime.from_xcrun_info(fake_runtimes)
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
        runtimes = subprocess.check_output(command, universal_newlines=True, shell=True)
        runtimes = runtimes.split("\n")
        runtimes = [runtime for runtime in runtimes if len(runtime) > 0]
        self.assertTrue(len(runtimes) > 0)

        runtime_identifier = random.choice(runtimes)
        runtime = xcrun.simctl.runtime.from_id(runtime_identifier)

        self.assertIsNotNone(runtime)
        self.assertEqual(runtime.identifier, runtime_identifier)

    def test_from_name(self):
        """Test that we can create a runtime reference from an existing runtime name."""
        # Get a random runtime
        command = "xcrun simctl list runtimes | tail -n +2 | sed -e 's/ (.*//'"
        runtimes = subprocess.check_output(command, universal_newlines=True, shell=True)
        runtimes = runtimes.split("\n")
        runtimes = [runtime for runtime in runtimes if len(runtime) > 0]
        self.assertTrue(len(runtimes) > 0)

        runtime_name = random.choice(runtimes)
        runtime = xcrun.simctl.runtime.from_name(runtime_name)

        self.assertIsNotNone(runtime)
        self.assertEqual(runtime.name, runtime_name)

    def test_invalid_identifier(self):
        """Test that we don't accidentially match on invalid identifiers."""
        # Identifiers are UUIDs, so let's use something totally different:
        with self.assertRaises(xcrun.simctl.runtime.RuntimeNotFoundError):
            _ = xcrun.simctl.runtime.from_id("Hodor")

    def test_invalid_name(self):
        """Test that we don't accidentially match on invalid names."""
        # It's unlikely that anyone would get the exact same UUID as we generate
        with self.assertRaises(xcrun.simctl.runtime.RuntimeNotFoundError):
            _ = xcrun.simctl.runtime.from_name(str(uuid.uuid4()))
