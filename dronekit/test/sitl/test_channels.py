import time
from dronekit import connect
from dronekit.test import with_sitl
from nose.tools import assert_equals


def assert_readback(vehicle, values):
    i = 10
    while i > 0:
        time.sleep(.1)
        i -= .1
        for k, v in values.items():
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
    assert_equals(type(vehicle.channels['3']), int)
    assert_equals(type(vehicle.channels['4']), int)
    assert_equals(type(vehicle.channels['5']), int)
    assert_equals(type(vehicle.channels['6']), int)
    assert_equals(type(vehicle.channels['7']), int)
    assert_equals(type(vehicle.channels['8']), int)
    assert_equals(type(vehicle.channels[1]), int)
    assert_equals(type(vehicle.channels[2]), int)
    assert_equals(type(vehicle.channels[3]), int)
    assert_equals(type(vehicle.channels[4]), int)
    assert_equals(type(vehicle.channels[5]), int)
    assert_equals(type(vehicle.channels[6]), int)
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

    # test
    try:
        vehicle.channels['9']
        assert False, "Can read over end of channels"
    except:
        pass

    try:
        vehicle.channels['0']
        assert False, "Can read over start of channels"
    except:
        pass

    try:
        vehicle.channels['1'] = 200
        assert False, "can write a channel value"
    except:
        pass

    # Set Ch1 to 100 using braces syntax
    vehicle.channels.overrides = {'1': 1000}
    assert_readback(vehicle, {'1': 1000})

    # Set Ch2 to 200 using bracket
    vehicle.channels.overrides['2'] = 200
    assert_readback(vehicle, {'1': 200, '2': 200})

    # Set Ch2 to 1010
    vehicle.channels.overrides = {'2': 1010}
    assert_readback(vehicle, {'1': 1500, '2': 1010})

    # Set Ch3,4,5,6,7 to 300,400-700 respectively
    vehicle.channels.overrides = {'3': 300, '4': 400, '5': 500, '6': 600, '7': 700}
    assert_readback(vehicle, {'3': 300, '4': 400, '5': 500, '6': 600, '7': 700})

    # Set Ch8 to 800 using braces
    vehicle.channels.overrides = {'8': 800}
    assert_readback(vehicle, {'8': 800})

    # Set Ch8 to 800 using brackets
    vehicle.channels.overrides['8'] = 810
    assert_readback(vehicle, {'8': 810})

    try:
        # Try to write channel 9 override to a value with brackets
        vehicle.channels.overrides['9'] = 900
        assert False, "can write channels.overrides 9"
    except:
        pass

    try:
        # Try to write channel 9 override to a value with braces
        vehicle.channels.overrides = {'9': 900}
        assert False, "can write channels.overrides 9 with braces"
    except:
        pass

    # Clear channel 3 using brackets
    vehicle.channels.overrides['3'] = None
    assert '3' not in vehicle.channels.overrides, 'overrides hould not contain None'

    # Clear channel 2 using braces
    vehicle.channels.overrides = {'2': None}
    assert '2' not in vehicle.channels.overrides, 'overrides hould not contain None'

    # Clear all channels
    vehicle.channels.overrides = {}
    assert_equals(len(vehicle.channels.overrides.keys()), 0)

    # Set Ch2 to 33, clear channel 6
    vehicle.channels.overrides = {'2': 33, '6': None}
    assert_readback(vehicle, {'2': 33, '6': 1500})
    assert_equals(list(vehicle.channels.overrides.keys()), ['2'])

    # Callbacks
    result = {'success': False}
    vehicle.channels.overrides = {}

    def channels_callback(vehicle, name, channels):
        if channels['3'] == 55:
            result['success'] = True

    vehicle.add_attribute_listener('channels', channels_callback)
    vehicle.channels.overrides = {'3': 55}

    i = 5
    while not result['success'] and i > 0:
        time.sleep(.1)
        i -= 1
    assert result['success'], 'channels callback should be invoked.'

    vehicle.close()
