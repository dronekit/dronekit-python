from dronekit import connect
from dronekit.tools import with_sitl
import time
from nose.tools import assert_not_equals

@with_sitl
def test_timeout(connpath):
    v = connect(connpath, await_params=True)

    # print "Basic pre-arm checks"
    # Don't let the user try to fly autopilot is booting
    if v.mode.name == "INITIALISING":
        # print "Waiting for vehicle to initialise"
        time.sleep(1)
    while v.gps_0.fix_type < 2:
        # print "Waiting for GPS...:", vehicle.gps_0.fix_type
        time.sleep(1)

    v.armed = True
    v.flush()
    
    while not v.armed:
        time.sleep(1)

    time.sleep(1)
    
    #north, east, and down are initialized to None.  Any other value suggests that a LOCAL_POSITION_NED was received and parsed.
    assert_not_equals(v.location_local.north, None)
    assert_not_equals(v.location_local.east, None)
    assert_not_equals(v.location_local.down, None)
