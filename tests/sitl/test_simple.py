from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import sys
import os
from testlib import assert_equals

def test_parameters(local_connect):
    v = local_connect().get_vehicles()[0]

    # Simple parameter checks
    assert_equals(type(v.parameters['THR_MIN']), float)
