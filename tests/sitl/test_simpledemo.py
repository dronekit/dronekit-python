"""
This test represents a simple demo for testing.
Feel free to copy and modify at your leisure.
"""

from droneapi import local_connect
from droneapi.lib import VehicleMode
from droneapi.tools import with_sitl
from pymavlink import mavutil
import time
import sys
import os
from nose.tools import assert_equals

# This test runs first!
@with_sitl
def test_parameter():
    v = local_connect().get_vehicles()[0]

    # Perform a simple parameter check
    assert_equals(type(v.parameters['THR_MIN']), float)

# This test runs second. Add as many tests as you like
@with_sitl
def test_mode():
    v = local_connect().get_vehicles()[0]

    # Ensure Mode is an instance of VehicleMode
    assert isinstance(v.mode, VehicleMode)
