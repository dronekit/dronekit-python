"""
followme - Tracks GPS position of your computer (Linux only).

This example uses the python gps package to read positions from a GPS attached to your 
laptop and sends a new vehicle.commands.goto command every two seconds to move the
vehicle to the current point.

When you want to stop follow-me, either change vehicle modes or type Ctrl+C to exit the script.

Example documentation: http://python.dronekit.io/examples/follow_me.html
"""

from dronekit import connect
import gps
import socket
import time
import sys
from dronekit.lib import VehicleMode, LocationGlobal

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Tracks GPS position of your computer (Linux only). Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True)



def arm_and_takeoff(aTargetAltitude):
    """
    Arm vehicle and fly to aTargetAltitude.
    """
    print "Basic pre-arm checks"
    # Don't let the user try to fly while autopilot is booting
    if vehicle.mode.name == "INITIALISING":
        print "Waiting for vehicle to initialise"
        time.sleep(1)
    while vehicle.gps_0.fix_type < 2:
        print "Waiting for GPS...:", vehicle.gps_0.fix_type
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.commands.takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_frame.alt
        if vehicle.location.global_frame.alt>=aTargetAltitude*0.95: #Just below target, in case of undershoot.
            print "Reached target altitude"
            break;
        time.sleep(1)



try:
    # Use the python gps package to access the laptop GPS
    gpsd = gps.gps(mode=gps.WATCH_ENABLE)

    #Arm and take off to altitude of 5 meters
    arm_and_takeoff(5)

    while True:
    
        if vehicle.mode.name != "GUIDED":
            print "User has changed flight modes - aborting follow-me"
            break    
            
        # Read the GPS state from the laptop
        gpsd.next()

        # Once we have a valid location (see gpsd documentation) we can start moving our vehicle around
        if (gpsd.valid & gps.LATLON_SET) != 0:
            altitude = 30  # in meters
            dest = LocationGlobalRelative(gpsd.fix.latitude, gpsd.fix.longitude, altitude)
            print "Going to: %s" % dest

            # A better implementation would only send new waypoints if the position had changed significantly
            vehicle.commands.goto(dest)

            # Send a new target every two seconds
            # For a complete implementation of follow me you'd want adjust this delay
            time.sleep(2)
            
except socket.error:
    print "Error: gpsd service does not seem to be running, plug in USB GPS or run run-fake-gps.sh"
    sys.exit(1)

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

print("Completed")
