#!/usr/bin/env python

"""Utility functions for xcrun."""

import json
import subprocess
import sys
import time


def _find_best_match(name, values):
	"""Find the name in `values` with the highest number of matching components with `name`.

	e.g. If name is "Hello World" and values contains [{"name":"Hello Someone"},
	{"name": "Goodbye Someone"}] it will match on the first entry since it has
	"Hello" in common.
	"""

	name_components = set(name.split(" "))
	best_match = None
	best_match_count = 0
	for value in values:
		value_components = set(value["name"].split(" "))
		number_matching_components = len(list(name_components.intersection(value_components)))
		if number_matching_components > best_match_count:
			best_match = value
			best_match_count = number_matching_components
	return best_match
