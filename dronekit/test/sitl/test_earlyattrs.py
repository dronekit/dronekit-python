from dronekit import connect
from dronekit.test import with_sitl
from nose.tools import assert_equals, assert_not_equals


@with_sitl
def test_battery_none(connpath):
    vehicle = connect(connpath, _initialize=False)

    # Ensure we can get (possibly unpopulated) battery object without throwing error.
    assert_equals(vehicle.battery, None)

    vehicle.initialize()

    # Ensure we can get battery object without throwing error.
    vehicle.wait_ready('battery')
    assert_not_equals(vehicle.battery, None)

    vehicle.close()
