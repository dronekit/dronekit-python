import time
import math
from dronekit import connect, VehicleMode, LocationGlobal, Command
from dronekit.tools import with_sitl
from nose.tools import assert_not_equals, assert_equals

@with_sitl
def test_empty_clear(connpath):
    vehicle = connect(connpath)

    # Calling clear() on an empty object should not crash.
    vehicle.commands.clear()
    vehicle.commands.upload()

    assert_equals(len(vehicle.commands), 0)

@with_sitl
def test_set_home(connpath):
    vehicle = connect(connpath, await_params=True)

    # Wait for home position to be real and not 0, 0, 0
    # once we request it via cmds.download()
    time.sleep(10)
    vehicle.commands.download()
    vehicle.commands.wait_valid()
    assert_not_equals(vehicle.home_location, None)

    # Note: If the GPS values differ heavily from EKF values, this command
    # will basically fail silently. This GPS coordinate is tailored for that
    # the with_sitl initializer uses to not fail.
    vehicle.home_location = LocationGlobal(-35, 149, 600)
    vehicle.commands.download()
    vehicle.commands.wait_valid()

    assert_equals(vehicle.home_location.lat, -35)
    assert_equals(vehicle.home_location.lon, 149)
    assert_equals(vehicle.home_location.alt, 600)

@with_sitl
def test_parameter(connpath):
    vehicle = connect(connpath, await_params=True)

    # Home should be None at first.
    assert_equals(vehicle.home_location, None)
    
    # Wait for home position to be real and not 0, 0, 0
    # once we request it via cmds.download()
    time.sleep(10)

    # Initial
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    assert_equals(len(cmds), 1)

    # After clearing
    cmds.clear()
    vehicle.flush()
    cmds.download()
    cmds.wait_ready()
    assert_equals(len(cmds), 1)

    # Upload
    for command in [
        Command(0, 0, 0, 0, 16, 1, 1, 0.0, 0.0, 0.0, 0.0, -35.3605, 149.172363, 747.0),
        Command(0, 0, 0, 3, 22, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.359831, 149.166334, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.363489, 149.167213, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355491, 149.169595, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355071, 149.175839, 100.0),
        Command(0, 0, 0, 3, 113, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.362666, 149.178715, 22222.0),
        Command(0, 0, 0, 3, 115, 0, 1, 2.0, 22.0, 1.0, 3.0, 0.0, 0.0, 0.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]:
        vehicle.commands.add(command)
    vehicle.commands.upload()

    # After upload
    cmds.download()
    cmds.wait_ready()
    assert_equals(len(cmds), 9)
