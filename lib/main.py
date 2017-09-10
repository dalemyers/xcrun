#!/usr/bin/env python

import xcrun

#runtimes = xcrun.simctl.listall.runtimes()
#for runtime in runtimes:
#    print runtime

#devices = xcrun.simctl.list.devices()
#for runtime_id, runtime_devices in devices.iteritems():
#    for device in runtime_devices:
#        print runtime_id + ": " + str(device)

app_id = "io.myers.testapp"
iOS10_3 = xcrun.simctl.runtime.from_id("com.apple.CoreSimulator.SimRuntime.iOS-10-3")
iPhone7Type = xcrun.simctl.device_type.from_id("com.apple.CoreSimulator.SimDeviceType.iPhone-7")
iPhone7 = xcrun.simctl.device.from_name("iPhone 7", iOS10_3)

#print iPhone7.get_app_container(app_id)
#iPhone7.openurl("http://google.com")
#iPhone7.addmedia(["/Users/dalemy/Desktop/Screen Shot 2017-09-07 at 22.22.24.png"])

#iPhone7.terminate(app_id)


test_device = xcrun.simctl.device.create("xcrun test device", iPhone7Type, iOS10_3)
print test_device
test_device.delete()
