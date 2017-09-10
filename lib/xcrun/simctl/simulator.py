#!/usr/bin/env python
"""Handles Xcode simulator actions."""

import json
import subprocess
import sys
import time

class Simulator(object):
	"""Represents an instance of an iOS simulator."""

	def __init__(self, identifier, name, device_type, runtime):
		"""Construct a Simulator object."""
		self.identifier = identifier
		self.device_type = device_type
		self.runtime = runtime
		self.name = name

	def _run_base_command(self, command):
		"""Run a command on xcrun simctl, throwing an exception on failure."""
		full_command = "xcrun simctl %s %s" % (command, self.identifier)
		subprocess.check_output(full_command, universal_newlines=True, shell=True).replace("\n", "")

	def boot(self):
		"""Boot the simulator."""
		self._run_base_command("boot")

	def shutdown(self):
		"""Shutdown the simulator."""
		self._run_base_command("shutdown")

	def delete(self):
		"""Delete the simulator."""
		self._run_base_command("delete")

	def __str__(self):
		"""Return the string representation of the object."""
		return str({
			"identifier": self.identifier,
			"device_type": str(self.device_type),
			"runtime": str(self.runtime),
			"name": self.name
		})