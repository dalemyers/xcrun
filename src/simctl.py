#!/usr/bin/env python3

from __future__ import print_function

import json
import os
import subprocess
import sys

import runtime
import device_type
import device
import device_pair

class Simctl(object):
	
	def __init__(self):
		self.runtimes = [] # Just a list
		self.device_types = [] # Just a list
		self.devices = {} # A mapping of runtime to a list of devices
		self.device_pairs = []
		self._populate()

	def _populate(self):
		self._load_runtimes()
		self._load_device_types()
		self._load_devices()
		self._load_device_pairs()
	
	def dump(self):
		print("Runtimes: " + str(self.runtimes))
		print("Device Types: " + str(self.device_types))
		print("Devices: " + str(self.devices))
		print("Device Pairs: " + str(self.device_pairs))

	@staticmethod
	def _list(item):
		"""Run an `xcrun simctl` command with JSON output."""
		full_command = "xcrun simctl list %s --json" % (item,)
		# Deliberately don't catch the exception - we want it to bubble up
		output = subprocess.check_output(full_command, universal_newlines=True, shell=True)
		return json.loads(output)

	def _load_runtimes(self):
		runtime_info = Simctl._list("runtimes")
		self.runtimes = runtime.Runtime.create_from_xcrun_info(runtime_info)

	def _load_device_types(self):
		device_type_info = Simctl._list("devicetypes")
		self.device_types = device_type.DeviceType.create_from_xcrun_info(device_type_info)

	def _load_devices(self):
		device_info = Simctl._list("devices")
		self.devices = device.Device.create_from_xcrun_info(device_info)

	def _load_device_pairs(self):
		device_pair_info = Simctl._list("pairs")
		self.device_pairs = device_pair.DevicePair.create_from_xcrun_info(device_pair_info)