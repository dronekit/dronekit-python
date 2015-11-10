"""
simple_goto.py: GUIDED mode "simple goto" example (Copter Only)

Demonstrates how to arm and takeoff in Copter and how to navigate to points using Vehicle.commands.goto.

Full documentation is provided at http://python.dronekit.io/examples/simple_goto.html
"""

import time
from dronekit import connect
from dronekit.lib import VehicleMode, LocationGlobal
from pymavlink import mavutil
import time


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
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
        if vehicle.location.global_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print "Reached target altitude"
            break
        time.sleep(1)

arm_and_takeoff(20)


print "Going to first point..."
point1 = LocationGlobal(-35.361354, 149.165218, 20, is_relative=True)
vehicle.commands.goto(point1)

# sleep so we can see the change in map
time.sleep(30)

print "Going to second point..."
point2 = LocationGlobal(-35.363244, 149.168801, 20, is_relative=True)
vehicle.commands.goto(point2)

# sleep so we can see the change in map
time.sleep(30)

print "Returning to Launch"
vehicle.mode    = VehicleMode("RTL")

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()
