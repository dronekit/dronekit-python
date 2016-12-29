#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
flight_replay.py: 

This example requests a past flight from Droneshare, and then 'replays' 
the flight by sending waypoints to a vehicle.

Full documentation is provided at http://python.dronekit.io/examples/flight_replay.html
"""

from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import json, urllib, math
import time

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Load a telemetry log and use position data to create mission waypoints for a vehicle. Connects to SITL on local PC by default.')
parser.add_argument('--connect', help="vehicle connection target.")
parser.add_argument('--tlog', default='flight.tlog',
                   help="Telemetry log containing path to replay")
args = parser.parse_args()


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5



def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

def position_messages_from_tlog(filename):
    """
    Given telemetry log, get a series of wpts approximating the previous flight
    """
    # Pull out just the global position msgs
    messages = []
    mlog = mavutil.mavlink_connection(filename)
    while True:
        try:
            m = mlog.recv_match(type=['GLOBAL_POSITION_INT'])
            if m is None:
                break
        except Exception:
            break
        # ignore we get where there is no fix:
        if m.lat == 0:
            continue
        messages.append(m)

    # Shrink the number of points for readability and to stay within autopilot memory limits. 
    # For coding simplicity we:
    #   - only keep points that are with 3 metres of the previous kept point.
    #   - only keep the first 100 points that meet the above criteria.
    num_points = len(messages)
    keep_point_distance=3 #metres
    kept_messages = []
    kept_messages.append(messages[0]) #Keep the first message
    pt1num=0
    pt2num=1
    while True:
        #Keep the last point. Only record 99 points.
        if pt2num==num_points-1 or len(kept_messages)==99:
            kept_messages.append(messages[pt2num])
            break
        pt1 = LocationGlobalRelative(messages[pt1num].lat/1.0e7,messages[pt1num].lon/1.0e7,0)
        pt2 = LocationGlobalRelative(messages[pt2num].lat/1.0e7,messages[pt2num].lon/1.0e7,0)
        distance_between_points = get_distance_metres(pt1,pt2)
        if distance_between_points > keep_point_distance:
            kept_messages.append(messages[pt2num])
            pt1num=pt2num
        pt2num=pt2num+1

    return kept_messages
    
    
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)
        
    # Set mode to GUIDED for arming and takeoff:
    while (vehicle.mode.name != "GUIDED"):
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(0.1)

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        vehicle.armed = True
        print " Waiting for arming..."
        time.sleep(1)

    print " Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height 
    # before allowing next command to process.
    while True:
        requiredAlt = aTargetAltitude*0.95
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=requiredAlt: 
            print " Reached target altitude of ~%f" % (aTargetAltitude)
            break
        print " Altitude: %f < %f" % (vehicle.location.global_relative_frame.alt,
                                      requiredAlt)
        time.sleep(1)


print("Generating waypoints from tlog...")
messages = position_messages_from_tlog(args.tlog)
print " Generated %d waypoints from tlog" % len(messages)
if len(messages) == 0:
    print("No position messages found in log")
    exit(0)

#Start SITL if no connection string specified
if args.connect:
    connection_string = args.connect
    sitl = None
else:
    start_lat = messages[0].lat/1.0e7
    start_lon = messages[0].lon/1.0e7

    import dronekit_sitl
    sitl = dronekit_sitl.start_default(lat=start_lat,lon=start_lon)
    connection_string = sitl.connection_string()

# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True)


# Now download the vehicle waypoints
cmds = vehicle.commands
cmds.wait_ready()


cmds = vehicle.commands
cmds.clear()
for i in xrange(0, len(messages)):
    pt = messages[i]
    #print "Point: %d %d" % (pt.lat, pt.lon,)
    lat = pt.lat
    lon = pt.lon
    # To prevent accidents we don't trust the altitude in the original flight, instead
    # we just put in a conservative cruising altitude.
    altitude = 30.0
    cmd = Command( 0,
                   0,
                   0,
                   mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                   mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                   0, 0, 0, 0, 0, 0,
                   lat/1.0e7, lon/1.0e7, altitude)
    cmds.add(cmd)

#Upload clear message and command messages to vehicle.
print("Uploading %d waypoints to vehicle..." % len(messages))
cmds.upload()

print "Arm and Takeoff"
arm_and_takeoff(30)


print "Starting mission"

# Reset mission set to first (0) waypoint
vehicle.commands.next=0

# Set mode to AUTO to start mission:
while (vehicle.mode.name != "AUTO"):
    vehicle.mode = VehicleMode("AUTO")
    time.sleep(0.1)

# Monitor mission for 60 seconds then RTL and quit:
time_start = time.time()
while time.time() - time_start < 60:
    nextwaypoint=vehicle.commands.next
    print 'Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint())

    if nextwaypoint==len(messages):
        print "Exit 'standard' mission when start heading to final waypoint"
        break;
    time.sleep(1)

print 'Return to launch'
while (vehicle.mode.name != "RTL"):
    vehicle.mode = VehicleMode("RTL")
    time.sleep(0.1)

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed...")
