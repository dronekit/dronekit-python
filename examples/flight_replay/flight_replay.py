#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
flight_replay.py: 

This example requests a past flight from Droneshare, and then 'replays' 
the flight by sending waypoints to a vehicle.

Full documentation is provided at http://python.dronekit.io/examples/flight_replay.html
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flight_replay.py: 
Fixed and optimized version for Python 3 / DroneKit.
"""

from __future__ import print_function
from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import math
import time
import argparse

# Set up option parsing to get connection string
parser = argparse.ArgumentParser(description='Load a telemetry log and use position data to create mission waypoints for a vehicle.')
parser.add_argument('--connect', help="vehicle connection target.")
parser.add_argument('--tlog', default='flight.tlog', help="Telemetry log containing path to replay")
args = parser.parse_args()


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    Returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    
    # Safety check: if mission is complete or hasn't started
    if nextwaypoint == 0:
        return None
    
    # FIX: Use 'nextwaypoint' directly to get the target we are flying TO.
    # The original code used 'nextwaypoint-1', which gave the distance to the point we just PASSED.
    try:
        missionitem = vehicle.commands[nextwaypoint] 
    except IndexError:
        return None

    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat, lon, alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint


def position_messages_from_tlog(filename):
    """
    Given telemetry log, get a series of wpts approximating the previous flight
    """
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
    num_points = len(messages)
    keep_point_distance = 3 # metres
    kept_messages = []
    kept_messages.append(messages[0]) # Keep the first message
    pt1num = 0
    pt2num = 1
    
    # FIX: Raised limit from 99 to 200 for modern hardware capability
    max_waypoints = 200 
    
    while True:
        # Keep the last point. Or if we hit the limit.
        if pt2num == num_points - 1 or len(kept_messages) >= max_waypoints:
            kept_messages.append(messages[pt2num])
            break
            
        pt1 = LocationGlobalRelative(messages[pt1num].lat/1.0e7, messages[pt1num].lon/1.0e7, 0)
        pt2 = LocationGlobalRelative(messages[pt2num].lat/1.0e7, messages[pt2num].lon/1.0e7, 0)
        distance_between_points = get_distance_metres(pt1, pt2)
        
        if distance_between_points > keep_point_distance:
            kept_messages.append(messages[pt2num])
            pt1num = pt2num
        pt2num = pt2num + 1

    return kept_messages
    

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    Includes timeouts to prevent infinite loops.
    """
    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    
    # Timeout counter
    timeout_counter = 0
    
    while not vehicle.armed:
        vehicle.armed = True
        print(" Waiting for arming...")
        time.sleep(1)
        timeout_counter += 1
        
        # Safety Timeout (15 seconds)
        if timeout_counter > 15:
            print("Error: Vehicle failed to arm! Check GPS/Battery/Safety Switch.")
            return

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) 

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


# --- MAIN EXECUTION ---

print("Generating waypoints from tlog...")
try:
    messages = position_messages_from_tlog(args.tlog)
except Exception as e:
    print(f"Error reading tlog: {e}. Make sure the file exists.")
    exit(1)

print(" Generated %d waypoints from tlog" % len(messages))
if len(messages) == 0:
    print("No position messages found in log")
    exit(0)

# Start SITL if no connection string specified
if args.connect:
    connection_string = args.connect
    sitl = None
else:
    start_lat = messages[0].lat/1.0e7
    start_lon = messages[0].lon/1.0e7
    import dronekit_sitl
    sitl = dronekit_sitl.start_default(lat=start_lat, lon=start_lon)
    connection_string = sitl.connection_string()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

# Download and clear waypoints
cmds = vehicle.commands
cmds.wait_ready()
cmds.clear() # FIX: Removed redundant reassignment of 'cmds'

# Create MAVLink mission commands
for pt in messages:
    lat = pt.lat
    lon = pt.lon
    # Conservative cruising altitude
    altitude = 30.0
    cmd = Command(0, 0, 0,
                  mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                  mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                  0, 0, 0, 0, 0, 0,
                  lat/1.0e7, lon/1.0e7, altitude)
    cmds.add(cmd)

print("Uploading %d waypoints to vehicle..." % len(messages))
cmds.upload()

print("Arm and Takeoff")
arm_and_takeoff(30)

print("Starting mission")
# Reset mission set to first (0) waypoint
vehicle.commands.next = 0

# Set mode to AUTO to start mission
vehicle.mode = VehicleMode("AUTO")
while vehicle.mode.name != "AUTO":
    print("Waiting for AUTO mode...")
    time.sleep(1)

# Monitor mission
time_start = time.time()
while True:
    nextwaypoint = vehicle.commands.next
    # FIX: Added try/except for robust status printing
    try:
        dist = distance_to_current_waypoint()
        dist_str = f"{dist:.2f}" if dist is not None else "N/A"
    except:
        dist_str = "Calculating..."
        
    print(f'Distance to waypoint ({nextwaypoint}): {dist_str}')

    # Exit condition: if we reach the last waypoint index
    if nextwaypoint == len(messages):
        print("Mission complete. Heading to final waypoint.")
        break
    
    # Timeout safety (e.g. 60 seconds)
    if time.time() - time_start > 60:
        print("Timeout reached.")
        break
        
    time.sleep(1)

print('Return to launch')
vehicle.mode = VehicleMode("RTL")
while vehicle.mode.name != "RTL":
    time.sleep(0.1)

# Close vehicle object
print("Close vehicle object")
vehicle.close()

# Shut down simulator
if sitl is not None:
    sitl.stop()

print("Completed...")
