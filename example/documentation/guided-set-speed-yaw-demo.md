# Demo: GUIDED Mode Setting Speed and Yaw

This little demonstration shows how to fly the vehicle using the GUIDED mode directly specifying the speed components and the yaw direction. It is a different approach than to fly the vehicle in GUIDED mode specifying the position (i.e. [simple goto](http://python.dronekit.io/example_1.html), [code here](https://github.com/diydrones/dronekit-python/blob/master/example/simple_goto/simple_goto.py)) or in AUTO mode.

This one is a useful modality in cases when the vehicle is guided by a companion computer and it has to autonomously reach a target with position unknown.

In this demo, the vehicle will fly following a square path and a diamond-shaped one. While following the square path, the heading of the vehicle is changed according to the flying direction; while following the diamond-shaped path, the heading remains fixed.

## Running the example

Once Mavproxy is running and the API is loaded, you can run this small example by typing ```api start guided_set_speed_yaw.py```, if you start the simulator in the same folder of the file otherwise, if you start the the simulator in a different folder, you have to specify the full path to the file, something like ```api start /home/user/git/dronekit-python/example/guided_set_speed_yaw/guided_set_speed_yaw.py```. 

The program will automatically arm the vehicle and start the demo: at first, it waits for a GPS lock (```Waiting for GPS...```), then to receive a location update (```Waiting for location...```) and finally it arms the vehicle (```Arming...``` and ```Waiting for arming cycle completes...```). After that, it will lift off and ascend 5 meters then it will start the demo.

If it does not arm, type ```arm throttle``` manually in the Mavproxy console.

After starting the simulator, you should see something like:

```
+ mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551 --cmd= --aircraft xtest --console --map
Connect tcp:127.0.0.1:5760 source_system=255
xtest/logs/2015-04-25/flight26
Logging to xtest/logs/2015-04-25/flight26/flight.tlog
Running script xtest/mavinit.scr
-> module load droneapi.module.api
DroneAPI loaded
Loaded module droneapi.module.api
-> api start /home/user/git/dronekit-python/example/guided_set_speed_yaw/guided_set_speed_yaw.py
Waiting for GPS...
Loaded module console
Loaded module map
MAV> STABILIZE> Received 473 parameters
Saved 473 parameters to xtest/logs/2015-04-25/flight26/mav.parm
Waiting for location...
Arming...
timeout setting ARMING_CHECK to 0.000000
Waiting for arming cycle completes...
Setting GUIDED mode...
GUIDED> Taking off!
Going North & up
Going East & down
Going South
Going West
Going North, East and up
Going South, East and down
Going South and West
Going North and West
Setting LAND mode...
Completed
APIThread-0 exiting...

```

## How does it work?

The GUIDED mode is a flying modality that allows a vehicle to fly autonomously without a predefined a mission. It allows a user, a GCS (ground control station) or a companion computer to control the vehicle and give new instructions to react to new events or situations.

When flying in this modality, the SET_POSITION_TARGET_LOCAL_NED and MAV_CMD_CONDITION_YAW commands are useful to instruct the vehicle to move along to a specific direction towards a target or a point without knowing its coordinates.

The key code in this demo are the following functions:

```
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
```

The function **send_nav_velocity** generates a **set_position_target_local_ned** MAVLink message which is used to directly specify the speed components to the vehicle.

When using **mavutil.mavlink.MAV_FRAME_BODY_NED**, the speed components vx and vy are parallel to the North and East directions, not to the the front and side of the vehicle. The vz component is perpendicular to the plane of vx and vy, with a positive value towards the ground, following the right-hand convention. For more info, check [NED](http://en.wikipedia.org/wiki/North_east_down).

The **type_mask** parameter is a bitmask to indicate which dimensions should be ignored by the vehicle. A 0 means that the dimension is enabled, a 1 means ignored. In the example the value 0b0000111111000111 is used to enable the speed components.

Check [SET_POSITION_TARGET_LOCAL_NED](https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED) for more info on the command.

The function **condition_yaw** generates a **MISSION_ITEM** message carrying a **MAV_CMD_CONDITION_YAW** payload. It allows to specify a yaw direction for the vehicle. In the example, absolute angles are used. Therefore a heading of 0 means North.

Check [MISSION_ITEM](https://pixhawk.ethz.ch/mavlink/#MISSION_ITEM) and [MAV_CMD](https://pixhawk.ethz.ch/mavlink/) for more info on the command.

Other useful links:
- GUIDED mode for [copters](http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/ac2_guidedmode/)
- GUIDED mode for [plane](http://plane.ardupilot.com/wiki/flying/flight-modes/#guided)
- MAVLink mission command messages, i.e. [mav_condition_yaw](http://planner.ardupilot.com/wiki/mavlink-mission-command-messages/#mav_cmd_condition_yaw)

## Testbed settings

This demo has been developed and tested on a virtual machine running Xubuntu 14.04.02 LTS 64bit with 2GB ram and 2 cores.

Python environment:
```
pip show droneapi pymavlink mavproxy
---
Name: droneapi
Version: 1.1.1
Location: /usr/local/lib/python2.7/dist-packages
Requires: pymavlink, MAVProxy, protobuf
---
Name: pymavlink
Version: 1.1.52
Location: /usr/local/lib/python2.7/dist-packages
Requires: 
---
Name: MAVProxy
Version: 1.4.14
Location: /usr/local/lib/python2.7/dist-packages
Requires: pymavlink, pyserial
```
Ardupilot version: [c7394568](https://github.com/diydrones/ardupilot/commit/c73945686c821cab1034c0d434fc7d3f66a0fd50)

## Other info

At the time of writing, the acceleration and yaw parameters of **set_position_target_local_ned** are ignored in [GCS_Mavlink.pde](https://github.com/diydrones/ardupilot/blob/master/ArduCopter/GCS_Mavlink.pde#L1343).