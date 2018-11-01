import time
from dronekit import connect, Vehicle
from dronekit.test import with_sitl


class DummyVehicle(Vehicle):
    def __init__(self, *args):
        super(DummyVehicle, self).__init__(*args)

        self.success = False

        def success_fn(self, name, m):
            self.success = True

        self.add_message_listener('HEARTBEAT', success_fn)


@with_sitl
def test_timeout(connpath):
    v = connect(connpath, vehicle_class=DummyVehicle)

    while not v.success:
        time.sleep(0.1)

    v.close()
