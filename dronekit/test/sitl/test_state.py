from dronekit import connect, SystemStatus
from dronekit.test import with_sitl
from nose.tools import assert_equals


@with_sitl
def test_state(connpath):
    vehicle = connect(connpath, wait_ready=['system_status'])

    assert_equals(type(vehicle.system_status), SystemStatus)
    assert_equals(type(vehicle.system_status.state), str)

    vehicle.close()
