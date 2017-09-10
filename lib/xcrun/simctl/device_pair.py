#!/usr/bin/env python

import runtime

class DevicePair(object):
	"""Represents a device pair for the iOS simulator."""

	@staticmethod
	def create_from_xcrun_info(info):
		device_pairs = []
		pair_info = info["pairs"]
		for device_pair_identifier, device_pair_info in pair_info.iteritems():
			device_pairs.append(DevicePair(device_pair_identifier, device_pair_info))
		return device_pairs

	def __init__(self, device_pair_identifier, device_pair_info):
		"""Construct a DevicePair object from xcrun output.

		device_pair_identifier: The unique identifier for this device pair.
		device_pair_info: The dictionary representing the xcrun output for a device pair.
		"""

		self.raw_info = device_pair_info
		self.identifier = device_pair_identifier
		self.watch_udid = device_pair_info["watch"]["udid"]
		self.phone_udid = device_pair_info["phone"]["udid"]

	def watch(self):
		raise NotImplementedError()
	
	def phone(self):
		raise NotImplementedError()

	def __str__(self):
		"""Return the string representation of the object."""
		return self.identifier

	def __repr__(self):
		"""Return the raw representation of the object."""
		return str({
			"identifier": self.identifier,
			"watch_udid": self.watch_udid,
			"phone_udid": self.phone_udid
		})
