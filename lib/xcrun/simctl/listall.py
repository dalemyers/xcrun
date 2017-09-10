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

def _list(item):
	"""Run an `xcrun simctl` command with JSON output."""
	full_command = "xcrun simctl list %s --json" % (item,)
	# Deliberately don't catch the exception - we want it to bubble up
	output = subprocess.check_output(full_command, universal_newlines=True, shell=True)
	return json.loads(output)

def runtimes():
	runtime_info = _list("runtimes")
	return runtime.Runtime.create_from_xcrun_info(runtime_info)


def device_types():
	device_type_info = _list("devicetypes")
	return device_type.DeviceType.create_from_xcrun_info(device_type_info)

def devices():
	device_info = _list("devices")
	return device.Device.create_from_xcrun_info(device_info)

def device_pairs():
	device_pair_info = _list("pairs")
	return device_pair.DevicePair.create_from_xcrun_info(device_pair_info)