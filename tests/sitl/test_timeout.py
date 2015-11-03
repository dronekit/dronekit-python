import time
import sys
import os
from dronekit import connect, VehicleMode
from dronekit.tools import with_sitl
from nose.tools import assert_equals

@with_sitl
def test_timeout(connpath):
	vehicle = connect(connpath, await_params=True)

	# Stall input and lower error threshold to 10 seconds.
	vehicle._heartbeat_error = 10
	vehicle._handler._accept_input = False

	start = time.time()
	while vehicle._handler._alive and time.time() - start < 20:
		time.sleep(.1)

	assert_equals(vehicle._handler._alive, False)
