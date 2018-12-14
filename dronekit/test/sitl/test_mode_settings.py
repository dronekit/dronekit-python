from dronekit import connect
from dronekit.test import with_sitl
from nose.tools import assert_equals


@with_sitl
def test_modes_set(connpath):
    vehicle = connect(connpath)

    def listener(self, name, m):
        assert_equals('STABILIZE', self._flightmode)

    vehicle.add_message_listener('HEARTBEAT', listener)

    vehicle.close()
