#!/usr/bin/env python

import xcrun

#runtimes = xcrun.simctl.listall.runtimes()
#for runtime in runtimes:
#    print runtime

#devices = xcrun.simctl.list.devices()
#for runtime_id, runtime_devices in devices.iteritems():
#    for device in runtime_devices:
#        print runtime_id + ": " + str(device)

iOS10_3 = xcrun.simctl.runtime.from_id("com.apple.CoreSimulator.SimRuntime.iOS-10-3")
iPhone7 = xcrun.simctl.device.from_name("iPhone 7", iOS10_3)

print iPhone7.get_app_container("com.microsoft.Office.Outlook-wip")

iPhone7.openurl("http://google.com")

