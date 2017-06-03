import time
from droneapi.lib import VehicleMode, Location, Command
from pymavlink import mavutil
from testlib import assert_equals

def cmp_objects(keys, a, b):
    for k in keys:
        assert_equals(getattr(a, k), getattr(b, k),
                      "object key %s is not equal: %s vs %s" % (k, getattr(a, k), getattr(b, k)))

def scommand(command, param1,param2,param3,param4,param5,param6,param7):
    """
    Short command format. Pre-fills all the values which are always the same. It also pre
    fills the frame setting to MAV_FRAME_GLOBAL_RELATIVE_ALT as in most case this is good
    to use
    """
    return Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                    command, 0, 0, 
                    param1, param2, param3, param4, param5, param6, param7)

def test_start(local_connect):
    api = local_connect()
    v = api.get_vehicles()[0]

    # Load command set.
    cmds = v.commands

    # Clear command set.
    cmds.clear()

    # NOTE Without this line, we create an inconsistent state!
    v.flush()

    # Download new set of commands. We should only have the home
    # waypoint.
    cmds.download()
    cmds.wait_valid()
    assert_equals(cmds.count, 1, 'downloaded commands should only list home, instead list %r commands' % (cmds.count,))

    # [1] Add a takeoff command
    altitude=10 #target altitude
    pitch=10 #take off pitch. Need to check if degrees or radians, and what is a reasonable valued.
    cmd = scommand( mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, pitch, 0, 0, 0, 0, 0, altitude)
    cmds.add(cmd)
                   
    # [2] Add normal waypoint
    lat = -10
    lon = 10
    altitude = 10
    cmd = scommand( mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, lat, lon, altitude)
    cmds.add(cmd)

    # [3] Add normal waypoint
    lat = -20
    lon = 20
    altitude = 20
    cmd = scommand( mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, lat, lon, altitude)
    cmds.add(cmd)

    # [4] Add loiter waypoint
    lat = -30
    lon = 30
    altitude = 30
    cmd = scommand( mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM, 0, 0, 0, 0, lat, lon, altitude)
    cmds.add(cmd)

    # Cache this set of commands in a list for later comparison.
    send_cmds=list()
    for cmd in cmds:
        send_cmds.append(cmd)

    # Send command set.
    v.flush()

    # Sleep briefly to read the APM response that waypoints are updated.
    time.sleep(5)

    # Get uploaded commands.
    cmds.download()
    cmds.wait_valid()

    # Assert the number of command send equals the number
    # of commands we receive.
    assert_equals(len(send_cmds), cmds.count)

    # Compare the first waypoint, in particular.
    cmp_objects(('frame', 'command', 'param1', 'x', 'y', 'z'), send_cmds[0], cmds[0])
