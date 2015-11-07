import time
import sys
import os
import socket
from dronekit import connect, VehicleMode
from dronekit.test import with_sitl
from nose.tools import assert_equals

@with_sitl
def test_battery_none(connpath):
    vehicle = connect(connpath)

    # Ensure we can get (possibly unpopulated) battery object without throwing error.
    b1 = vehicle.battery

    vehicle.wait_ready('battery')

    # Ensure we can get battery object without throwing error.
    b2 = vehicle.battery

    assert b1 == b2 or b1 == None

    vehicle.close()
