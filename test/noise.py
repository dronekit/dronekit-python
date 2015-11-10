from dronekit import connect, VehicleMode
#from dronekit.lib import VehicleMode
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

# Check for channel access.
vehicle.channels['1']
vehicle.channels['2']
vehicle.channels['3']
vehicle.channels['4']
vehicle.channels['5']
vehicle.channels['6']
vehicle.channels['7']
vehicle.channels['8']

#test 
try:
    print "Ch9: %s" % vehicle.channels['9']
    assert False, "Can read over end of channels"
except:
    pass

try:
    print "Ch0: %s" % vehicle.channels['0']
    assert False, "Can read over start of channels"
except:
    pass

try:
    vehicle.channels['1'] = 200
    assert False, "can write a channel value"
except:
    pass

print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch1 to 100 using braces syntax
vehicle.channels.overrides = {'1': 1000}
print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch2 to 200 using bracket
vehicle.channels.overrides['2'] = 200
print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch2 to 1010
vehicle.channels.overrides = {'2': 1010}
print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch3,4,5,6,7 to 300,400-700 respectively
vehicle.channels.overrides = {'3': 300, '4':400, '5':500,'6':600,'7':700}
print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch8 to 800 using braces
vehicle.channels.overrides = {'8': 800}
print "Channel overrides: %s" % vehicle.channels.overrides
print "succeed - can write channel 8 using braces"

# Set Ch8 to 800 using brackets
vehicle.channels.overrides['8'] = 800
print "Channel overrides: %s" % vehicle.channels.overrides

try:    
    # Try to write channel 9 override to a value with brackets
    vehicle.channels.overrides['9']=900
    assert False, "can write channels.overrides 9"
except:
    pass

try:    
    # Try to write channel 9 override to a value with braces
    vehicle.channels.overrides={'9': 900}
    assert False, "can write channels.overrides 9 with braces"
except:
    pass

# Clear channel 3 using brackets
vehicle.channels.overrides['3'] = None
print "Channel overrides: %s" % vehicle.channels.overrides

# Clear channel 2 using braces
vehicle.channels.overrides = {'2': None}
print "Channel overrides: %s" % vehicle.channels.overrides

# Clear all channels
vehicle.channels.overrides = {}
print "Channel overrides: %s" % vehicle.channels.overrides

# Set Ch2 to 33, clear channel 6
vehicle.channels.overrides = {'2': 33, '6':None}
print "Channel overrides: %s" % vehicle.channels.overrides

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

print("Completed")
