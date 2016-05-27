#!/usr/bin/env python

class DeviceType(object):
	"""Represents a device type for the iOS simulator."""

	@staticmethod
	def create_from_xcrun_info(info):
		info = info["devicetypes"]
		device_types = []
		for device_type_info in info:
			device_types.append(DeviceType(device_type_info))
		return device_types

	def __init__(self, device_type_info):
		"""Construct a DeviceType object from xcrun output.
		
		device_type_info: The dictionary representing the xcrun output for a device type.
		"""
		self.raw_info = device_type_info
		self.name = device_type_info["name"]
		self.identifier = device_type_info["identifier"]

	def __str__(self):
		"""Return the string representation of the object."""
		return self.name + ": " + self.identifier

	def __repr__(self):
		"""Return the raw representation of the object."""
		return str(self.raw_info)
