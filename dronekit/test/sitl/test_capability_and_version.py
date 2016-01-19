import time

from dronekit import VehicleMode, connect
from dronekit.test import with_sitl
from nose.tools import assert_false, assert_true


@with_sitl
def test_capability_and_version(connpath):
    v = connect(connpath, wait_ready=True)
    time.sleep(5)
    assert_false(v.capabilities.ftp)
    assert_true(v.version.major is not None)

    #This will fail because of a problem in Copter3.3. TODO uncomment this line once dronekit sitl uses 3.4
    #assert_true(v.capabilities.mission_float)
