"""
vehicle_state.py: 

Demonstrates how to get and set vehicle state and parameter information, 
and how to observe vehicle attribute (state) changes.

Full documentation is provided at http://python.dronekit.io/examples/vehicle_state.html
"""
from dronekit import connect
from dronekit.lib import VehicleMode
from pymavlink import mavutil
import time

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print "\nConnecting to vehicle on: %s" % args.connect
vehicle = connect(args.connect, wait_ready=True)

if vehicle.mode.name == "INITIALISING":
    print "Waiting for vehicle to initialise"
    time.sleep(1)

print "\nAccumulating vehicle attribute messages"
while vehicle.attitude.pitch==None:  #Attitude is fairly quick to propagate
    print " ..."    
    time.sleep(1)

# Get all vehicle attributes (state)
print "\nGet all vehicle attribute values:"
print " Global Location: %s" % vehicle.location.global_frame
print " Local Location: %s" % vehicle.location.local_frame
print " Attitude: %s" % vehicle.attitude
print " Velocity: %s" % vehicle.velocity
print " GPS: %s" % vehicle.gps_0
print " Groundspeed: %s" % vehicle.groundspeed
print " Airspeed: %s" % vehicle.airspeed
print " Mount status: %s" % vehicle.mount_status
print " Battery: %s" % vehicle.battery
print " EKF OK?: %s" % vehicle.ekf_ok
print " Rangefinder: %s" % vehicle.rangefinder
print " Rangefinder distance: %s" % vehicle.rangefinder.distance
print " Rangefinder voltage: %s" % vehicle.rangefinder.voltage
print " Heading: %s" % vehicle.heading
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " Mode: %s" % vehicle.mode.name    # settable
print " Armed: %s" % vehicle.armed    # settable


# Get Vehicle Home location - will be `None` until first set by autopilot
while not vehicle.home_location:
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    if not vehicle.home_location:
        print " Waiting for home location ..."
# We have a home location, so print it!        
print "\n Home location: %s" % vehicle.home_location

# Set vehicle home_location, mode, and armed attributes (the only settable attributes)

print "\nSet new home location"
# Home location must be within 50km of EKF home location (or setting will fail silently)
# In this case, just set value to current location with an easily recognisable altitude (222)
my_location_alt=vehicle.location.global_frame
my_location_alt.alt=222
vehicle.home_location=my_location_alt
print " New Home Location (from attribute - altitude should be 222): %s" % vehicle.home_location

#Confirm it is written out (note that you must re-download commands)
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print " New Home Location (from vehicle - altitude should be 222): %s" % vehicle.home_location


print "\nSet Vehicle.mode=GUIDED (currently: %s)" % vehicle.mode.name 
vehicle.mode = VehicleMode("GUIDED")
while not vehicle.mode.name=='GUIDED':  #Wait until mode has changed
    print " Waiting for mode change ..."
    time.sleep(1)


# Check we have a good gps fix (required to arm)
while vehicle.gps_0.fix_type < 2:
    print "Waiting for GPS fix=3 (needed to arm):", vehicle.gps_0.fix_type
    time.sleep(1)
    
    
print "\nSet Vehicle.armed=True (currently: %s)" % vehicle.armed 
vehicle.armed = True
while not vehicle.armed:
    print " Waiting for arming..."
    time.sleep(1)


# Add and remove and attribute callbacks (using mode as example)     
def mode_callback(self, attr_name, value):
    # `attr_name` is the observed attribute (used if callback is used for multiple attributes)
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `value` is the updated attribute value.
    print " CALLBACK: Mode changed to", value

print "\nAdd attribute callback/observer on `vehicle` for `mode` attribute"     
vehicle.add_attribute_listener('mode', mode_callback)


print " Set mode=STABILIZE (currently: %s)" % vehicle.mode.name 
vehicle.mode = VehicleMode("STABILIZE")

print " Wait 2s so callback invoked before observer removed"
time.sleep(2)

print " Remove Vehicle.mode observer"    
# Remove observer added with `add_attribute_listener()`  - specifying the attribute and callback function
vehicle.remove_attribute_listener('mode', mode_callback)


                
# Add mode attribute callback using decorator (callbacks added this way cannot be removed).
print "\nAdd attribute callback/observer `mode` attribute using decorator" 
last_published_mode=''
@vehicle.on_attribute('mode')
def mode_decorated_callback(self, attr_name, value):
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `self` - the associated vehicle object (used if a callback is different for multiple vehicles)
    # `value` is the updated attribute value.
    global last_published_mode
    # Only publish when mode changes
    if value!=last_published_mode:
        print " CALLBACK: Mode changed to", value
        last_published_mode=value


print " Set mode=GUIDED (currently: %s)" % vehicle.mode.name 
vehicle.mode = VehicleMode("GUIDED")

print " Wait 2s so callback invoked before observer removed"
time.sleep(2)

print "\n Attempt to remove observer added with `on_attribute` decorator (should fail)" 
try:
    vehicle.remove_attribute_listener('mode', mode_decorated_callback)
except:
    print " Exception: Cannot add observer added using decorator"


 
# Demonstrate getting callback on any attribute change
def wildcard_callback(self, attr_name, value):
    # `attr_name` - attribute name (useful if callback is used for multiple attributes)
    # `self` - associated vehicle object (used if callback behaviour is different for multiple vehicles)
    # `value` - updated attribute value.
    print " CALLBACK: (%s): %s" % (attr_name,value)

print "\nAdd attribute calback detecting any attribute change"     
vehicle.add_attribute_listener('*', wildcard_callback)


print " Wait 1s so callback invoked before observer removed"
time.sleep(1)

print " Remove Vehicle attribute observer"    
# Remove observer added with `add_attribute_listener()`
vehicle.remove_attribute_listener('*', wildcard_callback)
    
    
    

# Get/Set Vehicle Parameters
print "\nRead vehicle param 'THR_MIN': %s" % vehicle.parameters['THR_MIN']
print "Write vehicle param 'THR_MIN' : 10"
vehicle.parameters['THR_MIN']=10
print "Read new value of param 'THR_MIN': %s" % vehicle.parameters['THR_MIN']


## Reset variables to sensible values.
print "\nReset vehicle attributes/parameters and exit"
vehicle.mode = VehicleMode("STABILIZE")
vehicle.armed = False
vehicle.parameters['THR_MIN']=130


#Close vehicle object before exiting script
print "\nClose vehicle object"
vehicle.close()

print("Completed")
