import time
from dronekit import connect, VehicleMode, LocationGlobal
from dronekit.test import with_sitl
from nose.tools import assert_not_equals

@with_sitl
def test_timeout(connpath):
    vehicle = connect(connpath, wait_ready=True)

    # NOTE these are *very inappropriate settings*
    # to make on a real vehicle. They are leveraged
    # exclusively for simulation. Take heed!!!
    vehicle.parameters['ARMING_CHECK'] = 0

    # ARM
    vehicle.armed = True
    i = 60
    while not vehicle.armed and i > 0:
        time.sleep(1)
        i = i - 1

    # Await attributes
    time.sleep(3)
    
    # .north, .east, and .down are initialized to None.
    # Any other value suggests that a LOCAL_POSITION_NED was received and parsed.
    assert_not_equals(vehicle.location.local_frame.north, None)
    assert_not_equals(vehicle.location.local_frame.east, None)
    assert_not_equals(vehicle.location.local_frame.down, None)
