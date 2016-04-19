"""
Simple test to trigger a bug in Vehicle class: issue #610 fixed in PR #611
"""

import time
import sys
import os
from dronekit import connect, VehicleMode
from dronekit.test import with_sitl
from nose.tools import assert_equals

@with_sitl
def test_timeout(connpath):
    v = connect(connpath)
    
    # Set the vehicle and autopilot type to 'unsupported' types that MissionPlanner uses as of 17.Apr.2016
    v._vehicle_type = 6
    v._autopilot_type = 8

    # The above types trigger 'TypeError: argument of type 'NoneType' is not iterable' which is addressed in issue #610
    is_available = v._is_mode_available(0)

    v.close()
