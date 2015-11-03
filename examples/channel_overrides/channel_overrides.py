"""
channel_overrides.py: 

Demonstrates how set and clear channel-override information.

# NOTE: 
Channel overrides (a.k.a "RC overrides") are highly discommended (they are primarily implemented 
for simulating user input and when implementing certain types of joystick control).

They are provided for development purposes. Please raise an issue explaining why you need them
and we will try to find a better alternative: https://github.com/dronekit/dronekit-python/issues


Full documentation is provided at http://python.dronekit.io/examples/channel_overrides.html
"""
from dronekit import connect
from dronekit.lib import VehicleMode
from pymavlink import mavutil
import time

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Example showing how to set and clear vehicle channel-override information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True)

#Override channels
print "\nOverriding RC channels for roll and yaw"
vehicle.channel_override = { "1" : 900, "4" : 1000 }
print " Current overrides are:", vehicle.channel_override

# Get all original channel values (before override)
print " Channel default values:", vehicle.channel_readback  

# Cancel override by setting channels to 0
print " Cancelling override"
vehicle.channel_override = { "1" : 0, "4" : 0 }

# Short wait before exiting
time.sleep(5)

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

print("Completed")
