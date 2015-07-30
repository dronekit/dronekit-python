from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import sys
import os
from testlib import assert_equals

def current_milli_time():
    return int(round(time.time() * 1000))

def test_timeout(local_connect):
    v = local_connect().get_vehicles()[0]

    value = v.parameters['THR_MIN']
    assert_equals(type(value), float)

    start = current_milli_time()
    v.parameters['THR_MIN'] = value + 10
    end = current_milli_time()

    newvalue = v.parameters['THR_MIN']
    assert_equals(type(newvalue), float)
    assert_equals(newvalue, value + 10)

    # TODO once this issue is fixed
    # assert end - start < 1000, 'time to set parameter was %s, over 1s' % (end - start,)
