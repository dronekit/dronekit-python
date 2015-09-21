"""
This test represents a simple demo for testing.
Feel free to copy and modify at your leisure.
"""

from droneapi import connect
from droneapi.lib import VehicleMode
from droneapi.tools import with_sitl
from pymavlink import mavutil
import time
import sys
import os
from nose.tools import assert_equals

# This test runs first!
@with_sitl
def test_parameter(connpath):
    v = connect(connpath, await_params=True)

    # Perform a simple parameter check
    assert_equals(type(v.parameters['THR_MIN']), float)

# This test runs second. Add as many tests as you like
@with_sitl
def test_mode(connpath):
    v = connect(connpath, await_params=True)

    # Ensure Mode is an instance of VehicleMode
    assert isinstance(v.mode, VehicleMode)
