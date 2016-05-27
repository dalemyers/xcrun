#!/usr/bin/env python3

from __future__ import print_function

import subprocess
import sys
import argparse
import os

class DeviceType(object):
	unknown = 0
	iphone = 1
	ipad = 2
	tv = 3
	watch = 4
	

class OSType(object):
	unknown = 0
	ios = 1
	tvos = 2
	watchos = 3
	

class SimulatorType(object):
	def __init__(self, name, key):
		self.name = name
		self.key = key
		self.device_type = self.__device_type_from_key(key)
		
	def __device_type_from_key(self, key):
		parts = key.split(".") # ["com", "apple", "CoreSimulator", "SimDeviceType", "iPhone-4s"]
		if len(parts) < 5:
			return DeviceType.unknown
			
		device_type = parts[4].lower()
		
		if device_type.startswith("iphone"):
			return DeviceType.iphone
		elif device_type.startswith("ipad"):
			return DeviceType.ipad
		elif device_type.startswith("apple-tv"):
			return DeviceType.tv
		elif device_type.startswith("apple-watch"):
			return DeviceType.watch
		else:
			return DeviceType.unknown
	
	@staticmethod
	def create_from_type_entry(entry):
		#Example: iPhone 4s (com.apple.CoreSimulator.SimDeviceType.iPhone-4s)
		entry = entry[:-1] #Drop last )
		parts = entry.split("(")
		if len(parts) != 2:
			return None
		return SimulatorType(parts[0].strip(), parts[1].strip())
	
	def __repr__(self):
		return str({"name":self.name, "key":self.key, "device_type":self.device_type})
	
	def __str__(self):
		return self.__repr__()
		
class Runtime(object):
	def __init__(self, name, key):
		self.name = name
		self.key = key
	
	@staticmethod
	def create_from_runtime_entry(entry):
		# Example line: iOS 9.3 (9.3 - 13E230) (com.apple.CoreSimulator.SimRuntime.iOS-9-3)
		entry = entry[:-1] #Drop last )
		parts = entry.split("(")
		if len(parts) != 3:
			return None
		return Runtime(parts[0].strip(), parts[2].strip())
		
	def __repr__(self):
		return str({"name":self.name, "key":self.key})
	
	def __str__(self):
		return self.__repr__()

class Simulator(object):
	def __init__(self, name, unique_id, state, os_name):
		self.name = name
		self.unique_id = unique_id
		self.state = state
		self.os_name = os_name
	
	@staticmethod
	def create_from_entry(entry, os_name):
		# iPhone 4s (7D0BB3DF-39C2-4A07-A4B6-CB28D607C814) (Shutdown)
		entry = entry.replace(")", "")
		parts = entry.split("(")
		parts = map(lambda x : x.strip(), parts)
		if len(parts) != 3:
			return None
		
		return Simulator(parts[0], parts[1], parts[2], os_name)

	def __repr__(self):
		return str({"name": self.name, "uid":self.unique_id, "state":self.state, "os_name":self.os_name})
	
	def __str__(self):
		return self.__repr__()

class SimCtl(object):
	
	def __init__(self):
		self.populated = False
		self.simulator_types = []
		self.simulators = []
		self.runtimes = []

	def populate(self):
		self.simulator_types = self.__simulator_types()
		self.runtimes = self.__runtimes()
		self.simulators = self.__simulators()
		self.populated = False

	def __get_simctl_output(self, command):
	
		if type(command) != list:
			command = command.split(" ")
	
		p = subprocess.Popen(['xcrun','simctl'] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		simdata,err = p.communicate()
	
		simdata = simdata.replace("\r","\n")
		simdata = simdata.replace("\n\n","\n")
	
		return simdata.split("\n")
		
	def get_devices(self):
		if not self.populated:
			self.populate()
		return self.devices[:] #Let's not let the user change anything
		
	def get_runtimes(self):
		if not self.populated:
			self.populate()
		return self.runtimes[:] #Let's not let the user change anything
	
	def get_simulators(self):
		if not self.populated:
			self.populate()
		return self.simulators[:]
	
	def __simulator_types(self):
		lines = self.__get_simctl_output("list devicetypes")
		simulators = map(lambda line : SimulatorType.create_from_type_entry(line), lines[1:])
		return filter(lambda x : x != None, simulators)

	def __runtimes(self):
		lines = self.__get_simctl_output("list runtimes")
		runtimes = map(lambda line : Runtime.create_from_runtime_entry(line), lines[1:])
		return filter(lambda x : x != None, runtimes)
	
	def __simulators(self):
		lines = self.__get_simctl_output("list devices")
		lines = lines[1:]
		simulators = {}
		current_simulator_type = None
		for line in lines:

			if line.startswith("-- "): # -- iOS 9.3 --
				current_simulator_type = line[3:][:-3]
				continue
			
			if current_simulator_type == None:
				continue
			
			if "unavailable" in current_simulator_type.lower():
				continue
			
			if "(unavailable," in line.lower(): 
				#TODO make this more secure since the name can be set by the user
				continue
			
			if current_simulator_type not in simulators.keys():
				simulators[current_simulator_type] = []
			
			simulators[current_simulator_type].append(line.strip())
		
		all_simulators = []
		
		for sim_type in simulators.keys():
			for simulator_entry in simulators[sim_type]:
				all_simulators.append(Simulator.create_from_entry(simulator_entry, sim_type))
		
		return all_simulators