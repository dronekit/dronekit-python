#
# This is a small example of the python drone API
#
from dronekit import connect
from dronekit.lib import VehicleMode
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
* The less than 300us variablity makes me think SITL has some 20ms poll rate - need to try with real vehicle

SITL copter load
Interval (sec) 0.019865
MaxInterval (sec) 0.021927
MinInterval (sec) 0.018421

AVR plane load: 20ms+/-7ms
Interval 0.02061
MaxInterval 0.025496
MinInterval 0.011533

PX4 quad load on Edsion: 20ms +60ms -5ms (VERY HIGH VARIABILITY - mostly due to px4 side - see below)
Interval 0.0281970000001
MaxInterval 0.0786720000001
MinInterval 0.0161290000001

PX4 quad load on a pixhawk (a9defa35) talking to my desktop - similar variability as with an Edison:
Interval 0.01989
MaxInterval 0.0688479999999
MinInterval 0.00722900000005
Interval 0.019929
MaxInterval 0.0688479999999
MinInterval 0.00722900000005
Interval 0.0189700000001
MaxInterval 0.0688479999999
MinInterval 0.00722900000005

or here's 20ish of the interval values seen on the px4 (a9defa35) Test
Interval 0.020012
Interval 0.0199689999999
Interval 0.0229640000002
Interval 0.0171049999999
Interval 0.0198150000001
Interval 0.0211049999998
Interval 0.0199740000003
Interval 0.0199459999999
Interval 0.0199590000002
Interval 0.0200379999997
Interval 0.0200850000001
Interval 0.0198839999998
Interval 0.0200420000001
Interval 0.0199539999999
Interval 0.0200760000002
Interval 0.0199029999999
Interval 0.0200950000003
Interval 0.0517199999999

now testing with a plane load with a px4 (a9defa35) at 56kbps - highly variable 25 to 82ms
Interval 0.0589850000001
MaxInterval 0.0829760000001
MinInterval 0.0258819999999

but change to 115kbps and things are much better
Interval 0.0201160000001
MaxInterval 0.044656
MinInterval 0.0150279999998

and changing things to 500kbps everything is just peachie - 18ms
Interval 0.018119
MaxInterval 0.02527
MinInterval 0.015737

Recommendations:
Run link as fast as you can 1500kbps?
Turn on hw flow control (and use --rtscts on mavproxy)

mavproxy.py --master=/dev/ttyMFD1,115200 --cmd="api start perf_test.py"
"""

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Example that demonstrates mission import/export from a file. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True)

#global vehicle


def scatterplot(x,y):
    pyplot.plot(x,y,'b.')
    pyplot.xlim(min(x)-1,max(x)+1)
    pyplot.ylim(min(y)-1,max(y)+1)
    pyplot.show()


def cur_usec():
    """Return current time in usecs"""
    # t = time.time()
    dt = datetime.now()
    t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)
    return t

class MeasureTime(object):
    def __init__(self):
        self.prevtime = cur_usec()
        self.previnterval = 0
        self.numcount = 0
        self.reset()

    def reset(self):
        self.maxinterval = 0
        self.mininterval = 10000

    def update(self):
        now = cur_usec()
        self.numcount = self.numcount + 1
        self.previnterval = now - self.prevtime
        self.prevtime = now
        self.maxinterval = max(self.previnterval, self.maxinterval)
        self.mininterval = min(self.mininterval, self.previnterval)

        #print "Interval", self.previnterval
        if (self.numcount % 100) == 0:
            if self.numcount == 200:
                # Ignore delays during startup
                self.reset()
            print "Interval", self.previnterval
            print "MaxInterval", self.maxinterval
            print "MinInterval", self.mininterval


acktime = MeasureTime()

def mavrx_debug_handler(message):
    """Measure heartbeat periodically"""
    mtype = message.get_type()
    global sendtime

    #if mtype == 'HEARTBEAT':
    if mtype == 'COMMAND_ACK':
        #traceback.print_stack()
        #print "GOT ACK", message
        acktime.update()
        send_testpackets()


def send_testpackets():
        #print "send ROI cmds"

        # create the SET_POSITION_TARGET_GLOBAL_INT command
        msg = vehicle.message_factory.set_position_target_global_int_encode(
                                                                                 0,       # time_boot_ms (not used)
                                                                                 1, 1,    # target system, target component
                                                                                 mavutil.mavlink.MAV_FRAME_GLOBAL, # frame
                                                                                 0b1000000011000111,       # type_mask - enable velocity only
                                                                                 0, 0, 0, # x, y, z positions (not used)
                                                                                 0, 0, 0.0, # x, y, z velocity in m/s
                                                                                 0, 0, 0, # x, y, z acceleration (not used)
                                                                                 0, 0)    # yaw, yaw_rate (not used)

        # send command to vehicle
        vehicle.send_mavlink(msg)

        # set ROI
        msg = vehicle.message_factory.command_long_encode(
                                                        1, 1,    # target system, target component
                                                        #mavutil.mavlink.MAV_CMD_DO_SET_RELAY, #command
                                                        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                        0, #confirmation
                                                        0, 0, 0, 0, #params 1-4
                                                        0,
                                                        0,
                                                        0
                                                        )

        vehicle.send_mavlink(msg)


# Print out some interesting stats about the vehicle
print "Mode: %s" % vehicle.mode
print "Location: %s" % vehicle.location
print "Attitude: %s" % vehicle.attitude
print "Velocity: %s" % vehicle.velocity
print "GPS: %s" % vehicle.gps_0
print "Armed: %s" % vehicle.armed
print "groundspeed: %s" % vehicle.groundspeed
print "airspeed: %s" % vehicle.airspeed

import time
time.sleep(30)

# Use of the following method is not recommended (it is better to add observer callbacks to attributes) but if you need it
# it is available...
vehicle.set_mavlink_callback(mavrx_debug_handler)

# You can read and write parameters
#print "Param: %s" % vehicle.parameters['THR_MAX']

# Now download the vehicle waypoints
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print "Home WP: %s" % cmds[0]
print "Current dest: %s" % cmds.next


print "Disarming..."
vehicle.armed = False

