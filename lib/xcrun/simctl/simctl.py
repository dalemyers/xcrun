#!/usr/bin/env python3

from __future__ import print_function

import subprocess
import device as simulator_device

def _run_command(command):
	full_command = "xcrun simctl %s" % (command,)
	# Deliberately don't catch the exception - we want it to bubble up
	return subprocess.check_output(full_command, universal_newlines=True, shell=True)


def get_app_container(device, app_identifier, container=None):
	command = 'get_app_container "%s" "%s"' % (device.udid, app_identifier)

	if container is not None:
		command += ' "' + container + '"'

	path = _run_command(command)

	# The path has an extra new line at the end, so remove it when returning
	return path[:-1]


def openurl(device, url):
	command = 'openurl "%s" "%s"' % (device.udid, url)
	_run_command(command)

def logverbose(device, enable):
	command = 'logverbose "%s" "%s"' % (device.udid, "enable" if enable else "disable")
	_run_command(command)

def icloud_sync(device):
	command = 'icloud_sync "%s"' % (device.udid,)
	_run_command(command)

def getenv(device, variable_name):
	command = 'getenv "%s" "%s"' % (device.udid, variable_name)
	variable = _run_command(command)
	# The variable has an extra new line at the end, so remove it when returning
	return variable[:-1]

def addmedia(device, paths):
	if isinstance(paths, str):
		paths = [paths]

	if len(paths) == 0:
		return

	command = 'addmedia "%s" ' % (device.udid)

	# Now we need to add the paths
	quoted_paths = ['"' + path + '"' for path in paths]
	paths_arg = " ".join(quoted_paths)
	command += paths_arg

	_run_command(command)