import time

from dronekit import connect
from dronekit.test import with_sitl
from nose.tools import assert_false, assert_true


@with_sitl
def test_115(connpath):
    v = connect(connpath, wait_ready=True)
    time.sleep(5)
    assert_false(v.capabilities.ftp)

    # versions of ArduCopter prior to v3.3 will send out capabilities
    # flags before they are initialised.  Vehicle attempts to refetch
    # until capabilities are non-zero, but we may need to wait:
    start_time = time.time()
    slept = False
    while v.capabilities.mission_float == 0:
        if time.time() > start_time + 30:
            break
        time.sleep(0.1)
        slept = True
    if v.capabilities.mission_float:
        if slept:
            assert_true(v.version.major <= 3)
            assert_true(v.version_minor <= 3)
    else:
        # fail it
        assert_true(v.capabilities.mission_float)

    assert_true(v.version.major is not None)
    assert_true(len(v.version.release_type()) >= 2)
    assert_true(v.version.release_version() is not None)

    v.close()
