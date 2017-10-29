#!/usr/bin/env python

import time

import xcrun

iOS10_2 = xcrun.simctl.runtime.from_id("com.apple.CoreSimulator.SimRuntime.iOS-10-2")
iOS10_3 = xcrun.simctl.runtime.from_id("com.apple.CoreSimulator.SimRuntime.iOS-10-3")

iPhone7Type = xcrun.simctl.device_type.from_id("com.apple.CoreSimulator.SimDeviceType.iPhone-7")

iPhone7 = xcrun.simctl.device.from_name("iPhone 7", iOS10_3)

app_id = "io.myers.testapp"

iPhone7.refresh_state()


#print iPhone7.get_app_container(app_id)
#iPhone7.openurl("http://google.com")
#iPhone7.addmedia(["/Users/dalemy/Desktop/Screen Shot 2017-09-07 at 22.22.24.png"])

#iPhone7.terminate(app_id)


#test_device = xcrun.simctl.device.create("xcrun test device", iPhone7Type, iOS10_3)
#print test_device
#test_device.delete()


# Upgrade flow
#upgrade_device = xcrun.simctl.device.create("Upgrade Device", iPhone7Type, iOS10_2)
#print upgrade_device.__repr__()

#print "Waiting..."
#time.sleep(10)

#upgrade_device.upgrade(iOS10_3)
#print upgrade_device.__repr__()

#print "Waiting..."
#time.sleep(10)

#upgrade_device.delete()