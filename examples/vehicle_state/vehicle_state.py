#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
vehicle_state.py: 

Demonstrates how to get and set vehicle state and parameter information, 
and how to observe vehicle attribute (state) changes.

Full documentation is provided at http://python.dronekit.io/examples/vehicle_state.html
"""
from dronekit import connect, VehicleMode
import time

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle. 
#   Set `wait_ready=True` to ensure default attributes are populated before `connect()` returns.
print "\nConnecting to vehicle on: %s" % connection_string
vehicle = connect(connection_string, wait_ready=True)

vehicle.wait_ready('autopilot_version')

# Get all vehicle attributes (state)
print "\nGet all vehicle attribute values:"
print " Autopilot Firmware version: %s" % vehicle.version
print "   Major version number: %s" % vehicle.version.major
print "   Minor version number: %s" % vehicle.version.minor
print "   Patch version number: %s" % vehicle.version.patch
print "   Release type: %s" % vehicle.version.release_type()
print "   Release version: %s" % vehicle.version.release_version()
print "   Stable release?: %s" % vehicle.version.is_stable()
print " Autopilot capabilities"
print "   Supports MISSION_FLOAT message type: %s" % vehicle.capabilities.mission_float
print "   Supports PARAM_FLOAT message type: %s" % vehicle.capabilities.param_float
print "   Supports MISSION_INT message type: %s" % vehicle.capabilities.mission_int
print "   Supports COMMAND_INT message type: %s" % vehicle.capabilities.command_int
print "   Supports PARAM_UNION message type: %s" % vehicle.capabilities.param_union
print "   Supports ftp for file transfers: %s" % vehicle.capabilities.ftp
print "   Supports commanding attitude offboard: %s" % vehicle.capabilities.set_attitude_target
print "   Supports commanding position and velocity targets in local NED frame: %s" % vehicle.capabilities.set_attitude_target_local_ned
print "   Supports set position + velocity targets in global scaled integers: %s" % vehicle.capabilities.set_altitude_target_global_int
print "   Supports terrain protocol / data handling: %s" % vehicle.capabilities.terrain
print "   Supports direct actuator control: %s" % vehicle.capabilities.set_actuator_target
print "   Supports the flight termination command: %s" % vehicle.capabilities.flight_termination
print "   Supports mission_float message type: %s" % vehicle.capabilities.mission_float
print "   Supports onboard compass calibration: %s" % vehicle.capabilities.compass_calibration
print " Global Location: %s" % vehicle.location.global_frame
print " Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
print " Local Location: %s" % vehicle.location.local_frame
print " Attitude: %s" % vehicle.attitude
print " Velocity: %s" % vehicle.velocity
print " GPS: %s" % vehicle.gps_0
print " Gimbal status: %s" % vehicle.gimbal
print " Battery: %s" % vehicle.battery
print " EKF OK?: %s" % vehicle.ekf_ok
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Rangefinder: %s" % vehicle.rangefinder
print " Rangefinder distance: %s" % vehicle.rangefinder.distance
print " Rangefinder voltage: %s" % vehicle.rangefinder.voltage
print " Heading: %s" % vehicle.heading
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " Groundspeed: %s" % vehicle.groundspeed    # settable
print " Airspeed: %s" % vehicle.airspeed    # settable
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
my_location_alt = vehicle.location.global_frame
my_location_alt.alt = 222.0
vehicle.home_location = my_location_alt
print " New Home Location (from attribute - altitude should be 222): %s" % vehicle.home_location

#Confirm current value on vehicle by re-downloading commands
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print " New Home Location (from vehicle - altitude should be 222): %s" % vehicle.home_location


print "\nSet Vehicle.mode = GUIDED (currently: %s)" % vehicle.mode.name 
vehicle.mode = VehicleMode("GUIDED")
while not vehicle.mode.name=='GUIDED':  #Wait until mode has changed
    print " Waiting for mode change ..."
    time.sleep(1)


# Check that vehicle is armable
while not vehicle.is_armable:
    print " Waiting for vehicle to initialise..."
    time.sleep(1)
    # If required, you can provide additional information about initialisation
    # using `vehicle.gps_0.fix_type` and `vehicle.mode.name`.
    
#print "\nSet Vehicle.armed=True (currently: %s)" % vehicle.armed 
#vehicle.armed = True
#while not vehicle.armed:
#    print " Waiting for arming..."
#    time.sleep(1)
#print " Vehicle is armed: %s" % vehicle.armed 


# Add and remove and attribute callbacks

#Define callback for `vehicle.attitude` observer
last_attitude_cache = None
def attitude_callback(self, attr_name, value):
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `self` - the associated vehicle object (used if a callback is different for multiple vehicles)
    # `value` is the updated attribute value.
    global last_attitude_cache
    # Only publish when value changes
    if value!=last_attitude_cache:
        print " CALLBACK: Attitude changed to", value
        last_attitude_cache=value

print "\nAdd `attitude` attribute callback/observer on `vehicle`"     
vehicle.add_attribute_listener('attitude', attitude_callback)

print " Wait 2s so callback invoked before observer removed"
time.sleep(2)

print " Remove Vehicle.attitude observer"    
# Remove observer added with `add_attribute_listener()` specifying the attribute and callback function
vehicle.remove_attribute_listener('attitude', attitude_callback)


        
# Add mode attribute callback using decorator (callbacks added this way cannot be removed).
print "\nAdd `mode` attribute callback/observer using decorator" 
@vehicle.on_attribute('mode')   
def decorated_mode_callback(self, attr_name, value):
    # `attr_name` is the observed attribute (used if callback is used for multiple attributes)
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `value` is the updated attribute value.
    print " CALLBACK: Mode changed to", value

print " Set mode=STABILIZE (currently: %s) and wait for callback" % vehicle.mode.name 
vehicle.mode = VehicleMode("STABILIZE")

print " Wait 2s so callback invoked before moving to next example"
time.sleep(2)

print "\n Attempt to remove observer added with `on_attribute` decorator (should fail)" 
try:
    vehicle.remove_attribute_listener('mode', decorated_mode_callback)
except:
    print " Exception: Cannot remove observer added using decorator"



 
# Demonstrate getting callback on any attribute change
def wildcard_callback(self, attr_name, value):
    print " CALLBACK: (%s): %s" % (attr_name,value)

print "\nAdd attribute callback detecting ANY attribute change"     
vehicle.add_attribute_listener('*', wildcard_callback)


print " Wait 1s so callback invoked before observer removed"
time.sleep(1)

print " Remove Vehicle attribute observer"    
# Remove observer added with `add_attribute_listener()`
vehicle.remove_attribute_listener('*', wildcard_callback)
    


# Get/Set Vehicle Parameters
print "\nRead and write parameters"
print " Read vehicle param 'THR_MIN': %s" % vehicle.parameters['THR_MIN']

print " Write vehicle param 'THR_MIN' : 10"
vehicle.parameters['THR_MIN']=10
print " Read new value of param 'THR_MIN': %s" % vehicle.parameters['THR_MIN']


print "\nPrint all parameters (iterate `vehicle.parameters`):"
for key, value in vehicle.parameters.iteritems():
    print " Key:%s Value:%s" % (key,value)
    

print "\nCreate parameter observer using decorator"
# Parameter string is case-insensitive
# Value is cached (listeners are only updated on change)
# Observer added using decorator can't be removed.
 
@vehicle.parameters.on_attribute('THR_MIN')  
def decorated_thr_min_callback(self, attr_name, value):
    print " PARAMETER CALLBACK: %s changed to: %s" % (attr_name, value)


print "Write vehicle param 'THR_MIN' : 20 (and wait for callback)"
vehicle.parameters['THR_MIN']=20
for x in range(1,5):
    #Callbacks may not be updated for a few seconds
    if vehicle.parameters['THR_MIN']==20:
        break
    time.sleep(1)


#Callback function for "any" parameter
print "\nCreate (removable) observer for any parameter using wildcard string"
def any_parameter_callback(self, attr_name, value):
    print " ANY PARAMETER CALLBACK: %s changed to: %s" % (attr_name, value)

#Add observer for the vehicle's any/all parameters parameter (defined using wildcard string ``'*'``)
vehicle.parameters.add_attribute_listener('*', any_parameter_callback)     
print " Change THR_MID and THR_MIN parameters (and wait for callback)"    
vehicle.parameters['THR_MID']=400  
vehicle.parameters['THR_MIN']=30


## Reset variables to sensible values.
print "\nReset vehicle attributes/parameters and exit"
vehicle.mode = VehicleMode("STABILIZE")
#vehicle.armed = False
vehicle.parameters['THR_MIN']=130
vehicle.parameters['THR_MID']=500


#Close vehicle object before exiting script
print "\nClose vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed")




