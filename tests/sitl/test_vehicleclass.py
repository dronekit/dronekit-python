from dronekit import connect, Vehicle
from dronekit.tools import with_sitl
import time
from nose.tools import assert_equals

class DummyVehicle(Vehicle):
	def __init__(self, *args):
		super(DummyVehicle, self).__init__(*args)

		self.success = False
		def success_fn(self, name, m):
			self.success = True
		self.on_message('HEARTBEAT', success_fn)

@with_sitl
def test_timeout(connpath):
    v = connect(connpath, vehicle_class=DummyVehicle)

    while not v.success:
    	time.sleep(0.1)
