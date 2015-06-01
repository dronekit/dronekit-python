import time
from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil

api             = local_connect()
vehicle         = api.get_vehicles()[0]

def arm_and_takeoff():
    """Dangerous: Arm and takeoff vehicle - use only in simulation"""
    # NEVER DO THIS WITH A REAL VEHICLE - it is turning off all flight safety checks
    # but fine for experimenting in the simulator.

    print "Waiting for GPS..."
    while vehicle.gps_0.fix_type < 2:
        # gps_0.fix_type:
        # 0-1: no fix
        # 2: 2D fix, 3: 3D fix, 4: DGPS, 5: RTK
        # check https://pixhawk.ethz.ch/mavlink/#GPS_RAW_INT
        time.sleep(1)

    print "Waiting for location..."
    while vehicle.location.alt == 0.0:
        time.sleep(1)

    print "Arming..."
    vehicle.mode    = VehicleMode("STABILIZE")
    vehicle.parameters["ARMING_CHECK"] = 0
    vehicle.armed   = True
    vehicle.flush()

    print "Waiting for arming cycle completes..."
    while not vehicle.armed and not api.exit:
        time.sleep(1)        

    print("Setting GUIDED mode...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.flush()

    time.sleep(1)

    print "Taking off!"
    vehicle.commands.takeoff(5) # Take off to 5m height
    vehicle.flush()
    time.sleep(10)

# send_nav_velocity - send nav_velocity command to vehicle to request it fly in specified direction
def send_nav_velocity(velocity_x, velocity_y, velocity_z):
    # create the SET_POSITION_TARGET_LOCAL_NED command
    # Check https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED
    # for info on the type_mask (0=enable, 1=ignore).
    # Accelerations and yaw are ignored in GCS_Mavlink.pde at the
    # time of writing.
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink.pde)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink.pde) 
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()

# condition_yaw - send condition_yaw mavlink command to vehicle so it points at specified heading (in degrees)
def condition_yaw(heading):
    # create the CONDITION_YAW command
    msg = vehicle.message_factory.mission_item_encode(0, 0,  # target system, target component
            0,     # sequence
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,         # command
            2, # current - set to 2 to make it a guided command
            0, # auto continue
            heading,    # param 1, yaw in degrees
            0,          # param 2, yaw speed deg/s
            1,          # param 3, direction -1 ccw, 1 cw
            0,          # param 4, relative offset 1, absolute angle 0
            0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()

arm_and_takeoff()

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

DURATION=20

# Square path
print("Going North & up")
condition_yaw(0)
send_nav_velocity(NORTH,0,UP)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going East & down")
condition_yaw(90)
send_nav_velocity(0,EAST,DOWN)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going South")
condition_yaw(180)
send_nav_velocity(SOUTH,0,0)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going West")
condition_yaw(270)
send_nav_velocity(0,WEST,0)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

# Diamond shape
# vx, vy are parallel to North and East, that is they are independent from the direction of the front of the vehicle
print("Going North, East and up")
condition_yaw(90)
send_nav_velocity(NORTH,EAST,UP)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going South, East and down")
condition_yaw(90)
send_nav_velocity(SOUTH,EAST,DOWN)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going South and West")
condition_yaw(90)
send_nav_velocity(SOUTH,WEST,0)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Going North and West")
condition_yaw(90)
send_nav_velocity(NORTH,WEST,0)
time.sleep(DURATION)
send_nav_velocity(0,0,0)

print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")
vehicle.flush()

print("Completed")
