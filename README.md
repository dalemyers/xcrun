# xcrun

This is a Python wrapper around the `xcrun` utility that Apple provides for interacting with the various Xcode developer tools. This module has been tested against python 2.7, 3.6 & 3.7.

## simctl

`simctl` is the tool for interacting with the iOS simulator and is the main focus of this module. The syntax is designed to remain as close to that which would be used on the command line as possible. For example, to list all runtimes on the command line you would do:

    xcrun simctl list runtimes

With this module you can print the result of:

    xcrun.simctl.listall.runtimes()

Most functions are on the item that they affect. So instead of running something on a device like:

    xcrun simctl do_thing <DEVICE_ID> arg1 arg2 ...

You can do this:

    iPhone7 = xcrun.simctl.device.from_name("iPhone 7")
    iPhone7.do_thing(arg1, arg2, ...)

## Testing

* `python3 -m tox` to run the tests. Tox can be installed by running `python3 -m pip install tox`.
  * If using pyenv you need to make sure you have 2.7, 3.6, 3.7 activated with `pyenv local 2.7, 3.6, 3.7 && pyenv rehash`. See this [pyenv/pyenv92](https://github.com/pyenv/pyenv/issues/92) for more details.
* `python3 -m pytest -m slow` to run the slow tests.

