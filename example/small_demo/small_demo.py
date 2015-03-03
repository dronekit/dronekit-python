#
# This is a small example of the python drone API
# Usage:
# * mavproxy.py
# * module load api
# * api start small-demo.py
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil

def mavrx_debug_handler(message):
    """A demo of receiving raw mavlink messages"""
    print "Received", message

# First get an instance of the API endpoint
api = local_connect()
# get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
v = api.get_vehicles()[0]

def mode_callback(attribute):
    print "Mode changed: ", v.mode

# Print out some interesting stats about the vehicle
print "Mode: %s" % v.mode
print "Location: %s" % v.location
print "Attitude: %s" % v.attitude
print "Velocity: %s" % v.velocity
print "GPS: %s" % v.gps_0
print "Armed: %s" % v.armed
print "groundspeed: %s" % v.groundspeed
print "airspeed: %s" % v.airspeed

# Use of the following method is not recommended (it is better to add observer callbacks to attributes) but if you need it
# it is available...
# v.set_mavlink_callback(mavrx_debug_handler)

# You can read and write parameters
#print "Param: %s" % v.parameters['THR_MAX']

# Now download the vehicle waypoints
cmds = v.commands
cmds.download()
cmds.wait_valid()
print "Home WP: %s" % cmds[0]
print "Current dest: %s" % cmds.next

# Test custom commands
# Note: For mavlink messages that include a target_system & target_component, those values
# can just be filled with zero.  The API will take care of using the correct values
# For instance, from the xml for command_long:
#                Send a command with up to seven parameters to the MAV
#
#                target_system             : System which should execute the command (uint8_t)
#                target_component          : Component which should execute the command, 0 for all components (uint8_t)
#                command                   : Command ID, as defined by MAV_CMD enum. (uint16_t)
#                confirmation              : 0: First transmission of this command. 1-255: Confirmation transmissions (e.g. for kill command) (uint8_t)
#                param1                    : Parameter 1, as defined by MAV_CMD enum. (float)
#                param2                    : Parameter 2, as defined by MAV_CMD enum. (float)
#                param3                    : Parameter 3, as defined by MAV_CMD enum. (float)
#                param4                    : Parameter 4, as defined by MAV_CMD enum. (float)
#                param5                    : Parameter 5, as defined by MAV_CMD enum. (float)
#                param6                    : Parameter 6, as defined by MAV_CMD enum. (float)
#                param7                    : Parameter 7, as defined by MAV_CMD enum. (float)
#msg = v.message_factory.command_long_encode(0, 0,
#                                  mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
#                                  0, 0, 0, 0, 1, 0, 0)
#print "Created msg: %s" % msg
#v.send_mavlink(msg)

# v.add_attribute_observer('mode', mode_callback)

print "Disarming..."
v.armed = False
v.flush()

print "Arming..."
v.armed = True
v.flush()

print "Overriding a RC channel"
v.channel_override = { "1" : 900, "4" : 1000 }
v.flush()
print "Current overrides are:", v.channel_override

print "RC readback:", v.channel_readback

# To Cancel override send 0 to the channels
print "Cancelling override"
v.channel_override = { "1" : 0, "4" : 0 }
v.flush()

# Now change the vehicle into auto mode
v.mode = VehicleMode("AUTO")

# Always call flush to guarantee that previous writes to the vehicle have taken place
v.flush()
