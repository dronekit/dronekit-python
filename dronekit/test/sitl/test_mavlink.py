import time
import math
from dronekit import connect
from dronekit.mavlink import MAVConnection
from dronekit.test import with_sitl
from nose.tools import assert_not_equals, assert_equals


@with_sitl
def test_mavlink(connpath):
    vehicle = connect(connpath)
    out = MAVConnection('udpin:localhost:15668')
    vehicle._handler.pipe(out)
    out.start()

    vehicle2 = connect('udpout:localhost:15668')

    result = {'success': False}

    @vehicle2.on_attribute('location')
    def callback(*args):
        result['success'] = True

    i = 20
    while not result['success'] and i > 0:
        time.sleep(1)

    assert result['success']
