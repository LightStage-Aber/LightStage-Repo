#!/bin/bash
# Requires:
#       - The Python Nose2 package
#           - It will find unit tests in suitable modules starting with `test_*.py` with classes that extend a class from the Python `unittest` module.
#
# Alternatively:
#       - Run each test class individually, e.g.:
#           cd tests/
#           python test_BrightnessControl.py


nose2