# simctl

This is a Python wrapper around the `xcrun simctl` utility that Apple provides for interacting with the various Xcode developer tools. 

`xcrun simctl` is the tool for interacting with the iOS simulator and is the main focus of this module. The syntax is designed to remain as close to that which would be used on the command line as possible. For example, to list all runtimes on the command line you would do:

    xcrun simctl list runtimes

With this module you can simply do:

    from isim import Runtime
    print(Runtime.list_all())

Most functions are on the item that they affect. So instead of running something on a device like:

    xcrun simctl do_thing <DEVICE_ID> arg1 arg2 ...

You can do this:

    from isim import Device
    iPhone7 = Device.from_name("iPhone 7")
    iPhone7.do_thing(arg1, arg2, ...)

## Testing

To run the tests, all you need to do is run `python3 -m tox` (can be installed by running `python3 -m pip install tox`). 