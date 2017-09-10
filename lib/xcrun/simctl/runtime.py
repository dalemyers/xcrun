#!/usr/bin/env python

import listall
import simctl

class RuntimeNotFoundError(Exception):
	"""Raised when a requested runtime is not found."""
	pass

class Runtime(object):
	"""Represents a runtime for the iOS simulator."""

	@staticmethod
	def create_from_xcrun_info(info):
		info = info["runtimes"]
		runtimes = []
		for runtime_info in info:
			runtimes.append(Runtime(runtime_info))
		return runtimes

	@staticmethod
	def create_from_key(key):
		all_info = simctl.Simctl._run_command("list runtimes")
		info = all_info["runtimes"]
		for runtime_info in info:
			if runtime_info["identifier"] == key:
				return Runtime(runtime_info)
		raise RuntimeNotFoundError(key)

	def __init__(self, runtime_info):
		"""Construct a Runtime object from xcrun output.
		
		runtime_info: The dictionary representing the xcrun output for a runtime.
		"""

		self.raw_info = runtime_info
		self.name = runtime_info["name"]
		self.identifier = runtime_info["identifier"]
		self.version = runtime_info["version"]
		self.availability = runtime_info["availability"]
		self.build_version = runtime_info["buildversion"]

	def __str__(self):
		"""Return the string representation of the object."""
		return self.name + ": " + self.identifier

	def __repr__(self):
		"""Return the raw representation of the object."""
		return str(self.raw_info)

def from_id(identifier):
	# Get all runtimes
	all_runtimes = listall.runtimes()

	for runtime in all_runtimes:
		if runtime.identifier == identifier:
			return runtime
	
	return None
