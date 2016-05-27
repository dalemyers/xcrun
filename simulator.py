#!/usr/bin/env python

import subprocess
import sys
import argparse
import os

CURRENT_IOS_VERSION = "iOS 9.3"

#There is no way of mapping an app id to an app, so we search for known files instead.
#Bool flag is True if a file, False if a directory
KNOWN_FILES = {	"Acompli":("Library/Application Support/app-ios", False),
				"Word":("Documents/com.microsoft.Office.Word.plist", True),
				"Excel":("Documents/com.microsoft.Office.Excel.plist", True),
				"PowerPoint":("Documents/com.microsoft.Office.PowerPoint.plist", True)
			  }

def parseDeviceString(devString):
	data = {}
	parts = devString.split("(")
	#['AutomationDevice - iPhone 4s - iOS 8.1 ', '8F2909E9-AA0E-4FB0-8439-88C3B1B53CAD) ', 'Shutdown)']
	data["name"] = parts[0][:-1]
	data["id"] = parts[1][:-2]
	data["status"] = parts[2][:-1]
	return data

def getSimulatorData():

	p = subprocess.Popen(['xcrun','simctl', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	simdata,err = p.communicate()

	simdata = simdata.replace("\r","\n")
	simdata = simdata.replace("\n\n","\n")

	device_types = []
	runtimes = []
	devices = {}

	currentData = ""
	deviceOS = ""

	for line in simdata.split("\n"):
		if len(line) == 0:
			continue
		
		if line[:2] == "==": #It's a heading of "Device Types", "Runtimes", or "Devices"
			currentData = line[3:][:-3]
			continue
		
		if currentData == "Device Types":
			device_types.append(line)
		elif currentData == "Runtimes":
			if "unavailable" in line:
				continue
			runtimes.append(line)
		elif currentData == "Devices":
			if line[:2] == "--":
				deviceOS = line[3:][:-3]
				devices[deviceOS] = {}
				continue
		
			line = line[4:] #remove spaces
			deviceInfo = parseDeviceString(line)
			devices[deviceOS][deviceInfo["name"]] = {"id":deviceInfo["id"],"status":deviceInfo["status"]}
		 
	return device_types, runtimes, devices
	
def find_app_documents(simpath, appname):
	rootDir = os.path.join(simpath, "data/Containers/Data/Application/")
	knownSubPath, isFile = KNOWN_FILES[appname]
	
	#Get guids of apps
	allApps = os.listdir(rootDir)
	
	for appGuid in allApps:
		knownPath = os.path.join(rootDir, appGuid, knownSubPath)
		
		#Check if the directory or file exists as specified
		if os.path.exists(knownPath):
			if isFile and os.path.isfile(knownPath):
				return appGuid
			elif not isFile and not os.path.isfile(knownPath):
				return appGuid
	
	return None

def main():
	device_types, runtimes, devices = getSimulatorData()

	parser = argparse.ArgumentParser(description="iOS Simulator Helper")
	
	parser.add_argument('--device', action="store", default=None, dest='device_name', help="Device to get the information for")
	parser.add_argument('--os', action="store", default=CURRENT_IOS_VERSION, dest='os_version', help="Operating system filter for the device")
	parser.add_argument('--listdevices', action="store_true", default=False, dest='list_devices', help="List the available devices")
	parser.add_argument('--listtypes', action="store_true", default=False, dest='list_types', help="List the available device types")
	parser.add_argument('--listruntimes', action="store_true", default=False, dest='list_runtimes', help="List the available runtimes")
	parser.add_argument('--listos', action="store_true", default=False, dest='list_os', help="List the available operating system versions")
	parser.add_argument('--fullpath', action="store_true", default=False, dest='full_path', help="Display the full path of the simulator location")
	parser.add_argument('--appdocuments', action="store", default=None, dest='app_documents', help="Display the path to the provided app documents location")


	
	args = parser.parse_args()
	
	option = "devices"

	if len(sys.argv) > 1:
		option = sys.argv[1]
	
	if args.list_types:
		print device_types
		return
		
	if args.list_runtimes:
		print runtimes
		return
		
	for os_version in devices.keys():
		if os_version.startswith("Unavailable"):
			del devices[os_version]
		
	if args.list_os:
		for os_version in devices.keys():
			print "-- " + os_version + " --"
			for devicename in devices[os_version].keys():
				print devicename + " - " + devices[os_version][devicename]["id"]
		return
		
	if args.list_devices:
		for os_version in devices.keys():
			for devicename in devices[os_version].keys():
				print devicename + " - " + devices[os_version][devicename]["id"] + " - " + os_version
		return
		

			
	if args.os_version[:4] != "iOS ":
		args.os_version = "iOS " + args.os_version
		
	deviceid = "Unknown"
	if args.os_version != None and args.device_name != None and len(devices[args.os_version]) >= 1:
		deviceid = devices[args.os_version][args.device_name]["id"]

	devicepath = os.path.expanduser("~") + "/Library/Developer/CoreSimulator/Devices/" + deviceid
	
	if not args.app_documents:
		if args.full_path:
			print devicepath
		else:
			print deviceid
		
		return
		
	if deviceid == "Unknown":
		print "Could not find device. Unable to locate documents."
		return
		
	#This means we are looking for the app documents
	appid = find_app_documents(devicepath, args.app_documents)
	
	if appid:
		print devicepath + "/data/Containers/Data/Application/" + appid + "/Documents"
	else:
		print "Could not find the app container"

if __name__ == '__main__':
	main()