from dronekit import connect
import time
import math
from dronekit import connect
from dronekit.tools import with_sitl
from dronekit.lib import VehicleMode, LocationGlobal
import time
from nose.tools import assert_not_equals

# This test runs first!
@with_sitl
def test_parameter(connpath):
    # Connect to the Vehicle
    vehicle = connect(connpath, await_params=True)

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_valid()

    vehicle.commands.clear()
    vehicle.flush()
