from dronekit import connect
from dronekit.lib import VehicleMode
from pymavlink import mavutil
import time
from dronekit import connect, VehicleMode, LocationGlobal
from dronekit.test import with_sitl
from nose.tools import assert_equals, assert_not_equals

def assert_readback(vehicle, values):
    i = 10
    while i > 0:
        time.sleep(.1)
        i -= .1
        for k, v in values.iteritems():
            if vehicle.channels[k] != v:
                continue
        break
    if i <= 0:
        raise Exception('Did not match in channels readback %s' % values)

@with_sitl
def test_timeout(connpath):
    vehicle = connect(connpath, wait_ready=True)

    assert_equals(len(vehicle.channels), 8)
    assert_equals(len(vehicle.channels.overrides), 8)

    assert_equals(sorted(vehicle.channels.keys()), [str(x) for x in range(1, 9)])
    assert_equals(sorted(vehicle.channels.overrides.keys()), [])

    assert_equals(type(vehicle.channels['1']), int)
    assert_equals(type(vehicle.channels['2']), int)
    assert_equals(type(vehicle.channels['7']), int)
    assert_equals(type(vehicle.channels['8']), int)
    assert_equals(type(vehicle.channels[1]), int)
    assert_equals(type(vehicle.channels[2]), int)
    assert_equals(type(vehicle.channels[7]), int)
    assert_equals(type(vehicle.channels[8]), int)
    
    vehicle.channels.overrides = {'1': 1010}
    assert_readback(vehicle, {'1': 1010})

    vehicle.channels.overrides = {'2': 1020}
    assert_readback(vehicle, {'1': 1500, '2': 1010})

    vehicle.channels.overrides['1'] = 1010
    assert_readback(vehicle, {'1': 1010, '2': 1020})

    del vehicle.channels.overrides['1']
    assert_readback(vehicle, {'1': 1500, '2': 1020})

    vehicle.channels.overrides = {'1': 1010, '2': None}
    assert_readback(vehicle, {'1': 1010, '2': 1500})

    vehicle.channels.overrides['1'] = None
    assert_readback(vehicle, {'1': 1500, '2': 1500})

    vehicle.close()
