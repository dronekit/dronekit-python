import time

from dronekit import VehicleMode, connect
from dronekit.test import with_sitl
from nose.tools import assert_false, assert_true


@with_sitl
def test_115(connpath):
    v = connect(connpath, wait_ready=True)
    time.sleep(5)
    assert_false(v.capabilities.ftp)
    assert_true(v.capabilities.mission_float)
    assert_true(v.version.major is not None)
