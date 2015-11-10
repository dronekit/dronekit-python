import time
import sys
import os
from dronekit import connect, VehicleMode
from dronekit.test import with_sitl
from nose.tools import assert_equals, assert_not_equals

@with_sitl
def test_parameters(connpath):
    vehicle = connect(connpath)

    # When called on startup, parameter (may!) be none.
    # assert_equals(vehicle.parameters.get('THR_MIN', wait_ready=False), None)

    # With wait_ready, it should not be none.
    assert_not_equals(vehicle.parameters.get('THR_MIN', wait_ready=True), None)
  
    try:
        assert_not_equals(vehicle.parameters['THR_MIN'], None)
    except:
        assert False

    # Garbage value after all parameters are downloaded should be None.
    assert_equals(vehicle.parameters.get('xXx_extreme_garbage_value_xXx', wait_ready=True), None)

    vehicle.close()

@with_sitl
def test_parameters(connpath):
    vehicle = connect(connpath, wait_ready=True)

    # Iterate over parameters.
    for k, v in vehicle.parameters.iteritems():
        break
    for value in vehicle.parameters:
        break

    vehicle.close()
