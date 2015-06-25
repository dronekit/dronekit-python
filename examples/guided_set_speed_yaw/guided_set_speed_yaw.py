"""
This example shows how to move/direct Copter and send commands in GUIDED mode using DroneKit Python.

Example documentation: http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html
"""

from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil
import time
import math

api             = local_connect()
vehicle         = api.get_vehicles()[0]


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
    vehicle.flush()

    while not vehicle.armed and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude
    vehicle.flush()

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.commands.takeoff will execute immediately).
    while not api.exit:
        print " Altitude: ", vehicle.location.alt
        if vehicle.location.alt>=aTargetAltitude*0.95: #Just below target, in case of undershoot.
            print "Reached target altitude"
            break;
        time.sleep(1)


#Arm and take of to altitude of 5 meters
arm_and_takeoff(5)



"""
Convenience functions for sending immediate/guided mode commands to control the Copter.

The set of commands demonstrated here include:
* MAV_CMD_CONDITION_YAW - set direction of the front of the Copter (latitude, longitude)
* MAV_CMD_DO_SET_ROI - set direction where the camera gimbal is aimed (latitude, longitude, altitude)
* MAV_CMD_DO_CHANGE_SPEED - set target speed in metres/second.
* MAV_CMD_DO_SET_HOME - set the home location.


The full set of available commands are listed here:
http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/
"""

def condition_yaw(heading, relative=False):
    """
    Send MAV_CMD_CONDITION_YAW message to point vehicle at a specified heading (in degrees).

    This method sets an absolute heading by default, but you can set the `relative` parameter
    to `True` to set yaw relative to the current yaw heading.
	
    By default the yaw of the vehicle will follow the direction of travel. After setting 
    the yaw using this function there is no way to return to the default yaw "follow direction 
    of travel" behaviour (https://github.com/diydrones/ardupilot/issues/2427)
	
    For more information see: 
    http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
    """
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()


def set_roi(location):
    """
    Send MAV_CMD_DO_SET_ROI message to point camera gimbal at a specified region of interest (Location).
    The vehicle may also turn to face the ROI.

    For more information see: 
    http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_set_roi
    """
    # create the MAV_CMD_DO_SET_ROI command
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
        0, #confirmation
        0, 0, 0, 0, #params 1-4
        location.lat,
        location.lon,
        location.alt
        )
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()


def set_speed(speed):
    """
    Send MAV_CMD_DO_CHANGE_SPEED to change the current speed when travelling to a point.
	
    In AC3.2.1 Copter will accelerate to this speed near the centre of its journey and then 
    decelerate as it reaches the target. In AC3.3 the speed changes immediately.
	
    This method is only useful when controlling the vehicle using position/goto commands. 
    It is not needed when controlling vehicle movement using velocity components.
	
    For more information see: 
    http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_change_speed
    """
    # create the MAV_CMD_DO_CHANGE_SPEED command
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, #command
        0, #confirmation
        0, #param 1
        speed, # speed
        0, 0, 0, 0, 0 #param 3 - 7
        )

    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()

	
def set_home(aLocation, aCurrent=1):
    """
    Send MAV_CMD_DO_SET_HOME command to set the Home location to either the current location 
    or a specified location.
	
    For more information see: 
    http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_set_home
    """
    # create the MAV_CMD_DO_SET_HOME command: 
    # http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_set_home
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_HOME, #command
        0, #confirmation
        aCurrent, #param 1: 1 to use current position, 2 to use the entered values.
		0, 0, 0, #params 2-4
        aLocation.lat,
        aLocation.lon,
        aLocation.alt
        )
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()
	


"""
Functions to make it easy to convert between the different frames-of-reference. In particular these
make it easy to navigate in terms of "metres from the current position" when using commands that take 
absolute positions in decimal degrees.

The methods are approximations only, and may be less accurate over longer distances, and when close 
to the Earth's poles.

Specifically, it provides:
* get_location_metres - Get Location (decimal degrees) at distance (m) North & East of a given Location.
* get_distance_metres - Get the distance between two Location objects in metres
* get_bearing - Get the bearing in degrees to a Location
"""

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a Location object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned Location has the same `alt and `is_relative` values 
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.

    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return Location(newlat, newlon,original_location.alt,original_location.is_relative)


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two Location objects.
	
    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat 		= aLocation2.lat - aLocation1.lat
    dlong		= aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def get_bearing(aLocation1, aLocation2):
    """
    Returns the bearing between the two Location objects passed as parameters.
	
    This method is an approximation, and may not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """	
    off_x = aLocation2.lon - aLocation1.lon
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing;

	

"""
Functions to move the vehicle to a specified position (as opposed to controlling movement by setting velocity components).

The methods include:
* goto_position_target_global_int - Sets position using SET_POSITION_TARGET_GLOBAL_INT command in 
    MAV_FRAME_GLOBAL_RELATIVE_ALT_INT frame
* goto_position_target_local_ned - Sets position using SET_POSITION_TARGET_LOCAL_NED command in 
    MAV_FRAME_BODY_NED frame
* goto - A convenience function that can use Vehicle.commands.goto (default) or 
    goto_position_target_global_int to travel to a specific position in metres 
    North and East from the current location. 
    This method reports distance to the destination.
"""

def goto_position_target_global_int(aLocation):
    """
    Send SET_POSITION_TARGET_GLOBAL_INT command to request the vehicle fly to a specified location.
	
    For more information see: https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT

    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
	"""
    print 'goto_target_globalint_position'
    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame		
        0b0000111111111000, # type_mask (only speeds enabled)
        aLocation.lat*1e7, # lat_int - X Position in WGS84 frame in 1e7 * meters
        aLocation.lon*1e7, # lon_int - Y Position in WGS84 frame in 1e7 * meters
        aLocation.alt, # alt - Altitude in meters in AMSL altitude, not WGS84 if absolute or relative, above terrain if GLOBAL_TERRAIN_ALT_INT
        0, # X velocity in NED frame in m/s
		0, # Y velocity in NED frame in m/s
		0, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()
	


def goto_position_target_local_ned(north, east, down):
    """	
    Send SET_POSITION_TARGET_LOCAL_NED command to request the vehicle fly to a specified 
    location in the North, East, Down frame.
	
    It is important to remember that in this frame, positive altitudes are entered as negative 
    "Down" values. So if down is "10", this will be 10 metres below the home altitude.
	
    At time of writing the method ignores the frame value and the NED frame is relative to the 
    HOME Location. If you want to specify the frame in terms of the vehicle (i.e. really use 
    MAV_FRAME_BODY_NED) then you can translate values relative to the home position (or move 
    the home position if this is sensible in your context).
	
    For more information see: https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED

    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
	"""
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
        0b0000111111111000, # type_mask (only positions enabled)
        north, east, down, # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
        0, 0, 0, # x, y, z velocity in m/s  (not used)
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()
	


def goto(dNorth, dEast, gotoFunction=vehicle.commands.goto):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
	
    The method takes a function pointer argument with a single `droneapi.lib.Location` parameter for 
    the target position. This allows it to be called with different position-setting commands. 
    By default it uses the standard method: droneapi.lib.Vehicle.commands.goto().
	
    The method reports the distance to target every two seconds.
    """
    currentLocation=vehicle.location
    targetLocation=get_location_metres(currentLocation, dNorth, dEast)
    targetDistance=get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)
    vehicle.flush()

	
    while not api.exit and vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        remainingDistance=get_distance_metres(vehicle.location, targetLocation)
        print "Distance to target: ", remainingDistance
        if remainingDistance<=targetDistance*0.01: #Just below target, in case of undershoot.
            print "Reached target"
            break;
        time.sleep(2)



"""
Functions that move the vehicle by specifying the velocity components in each direction.
The two functions use different MAVLink commands, but effectively implement the same behaviour.

The methods include:
* send_ned_velocity - Sets velocity components using SET_POSITION_TARGET_LOCAL_NED command
* send_global_velocity - Sets velocity components using SET_POSITION_TARGET_GLOBAL_INT command
"""

def send_ned_velocity(velocity_x, velocity_y, velocity_z):
    """
    Move vehicle in direction based on specified velocity vectors. 
	
    This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only 
    velocity components (https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED).
    
    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()



def send_global_velocity(velocity_x, velocity_y, velocity_z):
    """
    Move vehicle in direction based on specified velocity vectors.
	
    This uses the SET_POSITION_TARGET_GLOBAL_INT command with type mask enabling only 
    velocity components (https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT).
    
    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
    """
    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame		
        0b0000111111000111, # type_mask (only speeds enabled)
        0, # lat_int - X Position in WGS84 frame in 1e7 * meters
        0, # lon_int - Y Position in WGS84 frame in 1e7 * meters
        0, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
		   # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
        velocity_x, # X velocity in NED frame in m/s
		velocity_y, # Y velocity in NED frame in m/s
		velocity_z, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()


	
"""
Fly a triangular path using the standard Vehicle.commands.goto() method.

The method is called indirectly via a custom "goto" that allows the target position to be
specified as a distance in metres (North/East) from the current position, and which reports
the distance-to-target.
"""	
print("TRIANGLE path using standard Vehicle.commands.goto()")
print("Position North 80 West 50")
goto(80, -50)

print("Position North 0 East 100")
goto(0, 100)

print("Position North -80 West 50")
goto(-80, -50)



"""
Fly a triangular path using the SET_POSITION_TARGET_GLOBAL_INT command and specifying
a target position (rather than controlling movement using velocity vectors). The command is
called from goto_position_target_global_int() (via `goto`).

The goto_position_target_global_int method is called indirectly from a custom "goto" that allows 
the target position to be specified as a distance in metres (North/East) from the current position, 
and which reports the distance-to-target.

The code also sets the speed (MAV_CMD_DO_CHANGE_SPEED). In AC3.2.1 Copter will accelerate to this speed 
near the centre of its journey and then decelerate as it reaches the target. 
In AC3.3 the speed changes immediately.
"""	
print("TRIANGLE path using standard SET_POSITION_TARGET_GLOBAL_INT message and with varying speed.")
print("Position South 100 West 130")

print("Set speed to 5m/s.")
set_speed(5)
goto(-100, -130, goto_position_target_global_int)

print("Set speed to 15m/s (max).")
set_speed(15)
print("Position South 0 East 200")
goto(0, 260, goto_position_target_global_int)

print("Set speed to 10m/s (max).")
set_speed(10, goto_position_target_global_int)

print("Position North 100 West 130")
goto(100, -130, goto_position_target_global_int)



"""
Fly the vehicle in a 50m square path, using the SET_POSITION_TARGET_LOCAL_NED command 
and specifying a target position (rather than controlling movement using velocity vectors). 
The command is called from goto_position_target_local_ned() (via `goto`).

The position is specified in terms of the NED (North East Down) relative to the Home location.

WARNING: The "D" in NED means "Down". Using a positive D value will drive the vehicle into the ground!

The code sleeps for a time (DURATION) to give the vehicle time to reach each position (rather than 
sending commands based on proximity).

The code also sets the region of interest (MAV_CMD_DO_SET_ROI) via the `set_roi()` method. This points the 
camera gimbal at the the selected location (in this case it aligns the whole vehicle to point at the ROI).
"""	

print("SQUARE path using SET_POSITION_TARGET_LOCAL_NED and position parameters")
DURATION=20 #Set duration for each segment.

print("North 50m, East 0m, 10m altitude for %s seconds" % DURATION)
goto_position_target_local_ned(50,0,-10)
print("Point ROI at current location (home position)") 
# NOTE that this has to be called after the goto command as first "move" command of a particular type
# "resets" ROI/YAW commands
set_roi(vehicle.location)
time.sleep(DURATION)

print("North 50m, East 50m, 10m altitude")
goto_position_target_local_ned(50,50,-10)
time.sleep(DURATION)

print("Point ROI at current location")
set_roi(vehicle.location)

print("North 0m, East 50m, 10m altitude")
goto_position_target_local_ned(0,50,-10)
time.sleep(DURATION)

print("North 0m, East 0m, 10m altitude")
goto_position_target_local_ned(0,0,-10)
time.sleep(DURATION)



"""
Fly the vehicle in a SQUARE path using velocity vectors (the underlying code calls the 
SET_POSITION_TARGET_LOCAL_NED command with the velocity parameters enabled).

The thread sleeps for a time (DURATION) which defines the distance that will be travelled.

The code also sets the yaw (MAV_CMD_CONDITION_YAW) using the `set_yaw()` method in each segment
so that the front of the vehicle points in the direction of travel
"""	

#Set up velocity vector to map to each direction.
# vx > 0 => fly North
# vx < 0 => fly South
NORTH=2
SOUTH=-2

# Note for vy:
# vy > 0 => fly East
# vy < 0 => fly West
EAST=2
WEST=-2

# Note for vz: 
# vz < 0 => ascend
# vz > 0 => descend
UP=-0.5
DOWN=0.5


# Square path using velocity
print("SQUARE path using SET_POSITION_TARGET_LOCAL_NED and velocity parameters")
print("Velocity South & up")
send_ned_velocity(SOUTH,0,UP)
print("Yaw 180 absolute (South)")
condition_yaw(180)
time.sleep(DURATION)
send_ned_velocity(0,0,0)

print("Velocity West & down")
send_ned_velocity(0,WEST,DOWN)
print("Yaw 270 absolute (West)")
condition_yaw(270)
time.sleep(DURATION)
send_ned_velocity(0,0,0)

print("Velocity North")
send_ned_velocity(NORTH,0,0)
print("Yaw 0 absolute (North)")
condition_yaw(0)
time.sleep(DURATION)
send_ned_velocity(0,0,0)

print("Velocity East")
condition_yaw(90)
send_ned_velocity(0,EAST,0)
time.sleep(DURATION)
send_ned_velocity(0,0,0)



"""
Fly the vehicle in a DIAMOND path using velocity vectors (the underlying code calls the 
SET_POSITION_TARGET_GLOBAL_INT command with the velocity parameters enabled).

The thread sleeps for a time (DURATION) which defines the distance that will be travelled.

The code sets the yaw (MAV_CMD_CONDITION_YAW) using the `set_yaw()` method using relative headings
so that the front of the vehicle points in the direction of travel.

At the end of the second segment the code sets a new home location to the current point.
"""	

print("DIAMOND path using SET_POSITION_TARGET_GLOBAL_INT and velocity parameters")
# vx, vy are parallel to North and East (independent of the vehicle orientation)
print("Velocity North, East and up")
send_global_velocity(SOUTH,WEST,UP)
print("Yaw 225 absolute")
condition_yaw(225)
time.sleep(DURATION)
send_global_velocity(0,0,0)

print("Velocity South, East and down")
send_global_velocity(NORTH,WEST,DOWN)
print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90,relative=True)
time.sleep(DURATION)
send_global_velocity(0,0,0)

print("Set new Home location to current location")
set_home(vehicle.location)
print "Get new home location" #This reloads the home location in GCSs
cmds = vehicle.commands
cmds.download()
cmds.wait_valid()
print " Home WP: %s" % cmds[0]

print("Velocity South and West")
send_global_velocity(NORTH,EAST,0)
print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90,relative=True)
time.sleep(DURATION)
send_global_velocity(0,0,0)

print("Velocity North and West")
send_global_velocity(SOUTH,EAST,0)
print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90,relative=True)
time.sleep(DURATION)
send_global_velocity(0,0,0)


"""
The example is completing. LAND at current location.
"""	

print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")
vehicle.flush()

print("Completed")