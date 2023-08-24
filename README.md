# isim

![Python Version](https://img.shields.io/pypi/pyversions/isim.svg) ![Xcode 15.0](https://img.shields.io/badge/Xcode-15.0+-blue.svg)

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

To run the tests, all you need to do is run `python -m pytest tests` from the root directory.

## isim and Xcode Versioning

`isim` follows the current supported version of Xcode for its version scheme.

For example, if the currently supported version of Xcode is 11, then isim will be versioned as `11.minor.patch`. The `minor` version will only be increased if there is a breaking change in Xcode requiring it (which is unlikely). The patch version will be increased with each patch that is made.

There is no expectation of backwards compatibility. If you need to support an older version of Xcode, you'll almost always need an older major version.

_Note:_ The Xcode developer tools are installed with new betas. That means that if you are running Xcode 10.2.1, but then install the Xcode 11 beta, the simulator tools will be for Xcode 11, rather than Xcode 10, even if you run `xcode-select -s`. That means that as soon as you install a beta on your machine, you will need to use that version of isim.
