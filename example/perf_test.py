#
# This is a small example of the python drone API
# Usage:
# * mavproxy.py
# * module load api
# * api start small-demo.py
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
from datetime import datetime
import traceback

from matplotlib import pyplot
from numpy import arange
import bisect

findings = """
Reception latency:
* due to a top level select() on the udp port, the latency for calling process_master seems to be sub 1ms (limit of python timer resolution)

Reception periodicity:
TBD

Background processing perodicity:
TBD

Sending perodicity:
TBD

Computation efficency:
FIXME

Max closed loop rate:
* 20ms+/-300us when talking to SITL (every time we recieve a cmd_ack we immediately send a pair of ROI related msgs)
* The less than 300us variablity makes me think SITL has some 20ms poll rate

"""

global v

def scatterplot(x,y):
    pyplot.plot(x,y,'b.')
    pyplot.xlim(min(x)-1,max(x)+1)
    pyplot.ylim(min(y)-1,max(y)+1)
    pyplot.show()


def mavrx_debug_handler(message):
    """Measure heartbeat periodically"""
    mtype = message.get_type()
    # t = time.time()
    dt = datetime.now()
    t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)

    #if mtype == 'HEARTBEAT':
    if mtype == 'COMMAND_ACK':
        #traceback.print_stack()
        print "Received", t
        send_testpackets()


def send_testpackets():
        print "send ROI cmds"

        # create the SET_POSITION_TARGET_GLOBAL_INT command
        msg = v.message_factory.set_position_target_global_int_encode(
                                                                                 0,       # time_boot_ms (not used)
                                                                                 0, 0,    # target system, target component
                                                                                 mavutil.mavlink.MAV_FRAME_GLOBAL, # frame
                                                                                 0b1000000011000111,       # type_mask - enable velocity only
                                                                                 0, 0, 0, # x, y, z positions (not used)
                                                                                 0, 0, 0.0, # x, y, z velocity in m/s
                                                                                 0, 0, 0, # x, y, z acceleration (not used)
                                                                                 0, 0)    # yaw, yaw_rate (not used)

        # send command to vehicle
        v.send_mavlink(msg)

        # set ROI
        msg = v.message_factory.command_long_encode(
                                                        0, 0,    # target system, target component
                                                        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                        0, #confirmation
                                                        0, 0, 0, 0, #params 1-4
                                                        0,
                                                        0,
                                                        0
                                                        )

        v.send_mavlink(msg)

        # Always call flush to guarantee that previous writes to the vehicle have taken place
        v.flush()

# First get an instance of the API endpoint
api = local_connect()
# get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
v = api.get_vehicles()[0]
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
v.set_mavlink_callback(mavrx_debug_handler)

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

print "Disarming..."
v.armed = False
v.flush()


