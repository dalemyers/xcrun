"""Wrapper around the xcrun command."""

import warnings

import xcrun.simctl

warnings.warn("This package is deprecated. It has been replaced by the `isim` package.", DeprecationWarning)
