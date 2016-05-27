#!/usr/bin/env python

import runtime

class DeviceState(object):
	shutdown = 0
	# TODO

class Device(object):
	"""Represents a device for the iOS simulator."""

	@staticmethod
	def create_from_xcrun_info(info):
		runtime_map = info["devices"]
		all_devices = {}
		for runtime_key in runtime_map.keys():
			runtime_devices_info = runtime_map[runtime_key]
			devices = []
			for device_info in runtime_devices_info:
				devices.append(Device(device_info, runtime_key))
			all_devices[runtime_key] = devices
		return all_devices

	def __init__(self, device_info, runtime_key):
		"""Construct a Device object from xcrun output and a runtime key.
		
		device_info: The dictionary representing the xcrun output for a device.
		runtime_key: A unique key representing the runtime that the device uses.
		"""

		self.raw_info = device_info
		self.state = device_info["state"]
		self.availability = device_info["availability"]
		self.name = device_info["name"]
		self.udid = device_info["udid"]
		self.runtime_key = runtime_key
		self.runtime = None

	def runtime(self):
		if self.runtime == None:
			self.runtime = runtime.Runtime.create_from_key(runtime_key)
		return self.runtime

	def __str__(self):
		"""Return the string representation of the object."""
		return self.name + ": " + self.udid

	def __repr__(self):
		"""Return the raw representation of the object."""
		return str([str(self.raw_info), self.runtime.__repr__()])
