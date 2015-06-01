.. _example-guided-mode-setting-speed-yaw:

=======================================
Example: Setting Speed and Yaw (GUIDED)
=======================================

This example shows how to fly a vehicle in GUIDED mode, controlling movement by setting the vehicle speed
components and yaw direction.

.. note:: 

    Other approaches for guiding a vehicle are to set the target position in GUIDED mode (see 
    :doc:`simple_goto`) or to use AUTO mode and set waypoints. The approach in this example
    is useful when the precise position of the target is unknown.

.. todo:: When we have a doc on setting mission commands in guide, add link to it in note above.
	

Running the example
===================

Once MAVProxy is running and the API is loaded, you can run the example by typing: 
``api start full_path_to_file``

If you started the DroneKit MAVProxy prompt in a directory containing the example script you can start it using:
``api start guided_set_speed_yaw.py``. 
Otherwise you may have to specify the full path (something like):
``api start /home/user/git/dronekit-python/examples/guided_set_speed_yaw/guided_set_speed_yaw.py``.

The program will automatically arm the vehicle and start the demo. First it waits for a GPS lock 
(``Waiting for GPS...``), then to receive a location update (``Waiting for location...``) and finally 
it arms the vehicle (``Arming...`` and ``Waiting for arming cycle completes...``).
The vehicle will then lift off and ascend 5 meters. It flies at a constant speed in a square path (North, East, 
South, West) and then in a diamond-shaped path. While following the square path, the heading of the 
vehicle is changed according to the flying direction; while following the diamond-shaped path, the 
heading remains fixed. When it has completed both paths, the vehicle lands.

If it does not arm, type ``arm throttle`` manually in the MAVProxy console.

After starting the simulator, the console output should look something like:

::

    + mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551 --cmd= --aircraft xtest --console --map
    Connect tcp:127.0.0.1:5760 source_system=255
    xtest/logs/2015-04-25/flight26
    Logging to xtest/logs/2015-04-25/flight26/flight.tlog
    Running script xtest/mavinit.scr
    -> module load droneapi.module.api
    DroneAPI loaded
    Loaded module droneapi.module.api
    -> api start /home/user/git/dronekit-python/examples/guided_set_speed_yaw/guided_set_speed_yaw.py
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

How does it work?
=================

The GUIDED mode allows a vehicle to fly autonomously without a predefined a mission. This enables a GCS 
(ground control station) or a companion computer to control the vehicle “on the fly”, reacting to new
events or situations as they occur.

The example uses this mode, and calls the `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ 
and `MAV_CMD_CONDITION_YAW <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw>`_
commands to control the vehicle direction and speed.

The key code is captured in the following functions:

::

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

The function ``send_nav_velocity()`` generates a ``SET_POSITION_TARGET_LOCAL_NED`` MAVLink message 
which is used to directly specify the speed components to the vehicle.

When using ``mavutil.mavlink.MAV_FRAME_BODY_NED``, the speed components ``vx`` and ``vy`` are parallel 
to the North and East directions, not to the the front and side of the vehicle. The ``v``\ z component is
perpendicular to the plane of ``vx`` and ``vy``, with a positive value towards the ground, following 
the right-hand convention. For more information about this frame of reference, see this wikipedia article 
on `NED <http://en.wikipedia.org/wiki/North_east_down>`_.

The ``type_mask`` parameter is a bitmask to indicate which dimensions are used/ignored by the vehicle 
(0 means that the dimension is enabled, 1 means ignored). In the example the value 0b0000111111000111 
is used to enable the speed components.

The function ``condition_yaw()`` generates a `MISSION_ITEM <https://pixhawk.ethz.ch/mavlink/#MISSION_ITEM>`_ message carrying a ``MAV_CMD_CONDITION_YAW`` 
payload. It allows to specify a yaw direction for the vehicle. In the example, absolute angles are used.
Therefore a heading of 0 means North.

Other useful links:

-  `GUIDED Mode for Copter <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/ac2_guidedmode/>`_.
-  `GUIDED mode for Plane <http://plane.ardupilot.com/wiki/flying/flight-modes/#guided>`_.
-  `MAVLink mission command messages <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd>`_ 
   (e.g. `MAV_CMD_CONDITION_YAW <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw>`_).

Testbed settings
================

This demo has been developed and tested on a virtual machine running Xubuntu 14.04.02 LTS 64bit with 
2GB RAM and 2 cores.

Python environment:

::

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

ArduPilot version: `3.3.0beta2 <https://github.com/diydrones/ardupilot/commit/c73945686c821cab1034c0d434fc7d3f66a0fd50>`_.

Other information
=================

At the time of writing, the acceleration and yaw parameters of
``set_position_target_local_ned()`` are ignored in `GCS\_Mavlink.pde`_.

.. _NED: http://en.wikipedia.org/wiki/North_east_down
.. _MISSION\_ITEM: https://pixhawk.ethz.ch/mavlink/#MISSION_ITEM
.. _Copter: http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/ac2_guidedmode/
.. _Plane: http://plane.ardupilot.com/wiki/flying/flight-modes/#guided
.. _MAVLink mission command messages: http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd
.. _MAV\_CMD\_CONDITION\_YAW: http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
.. _c7394568: https://github.com/diydrones/ardupilot/commit/c73945686c821cab1034c0d434fc7d3f66a0fd50
.. _GCS\_Mavlink.pde: https://github.com/diydrones/ardupilot/blob/master/ArduCopter/GCS_Mavlink.pde#L1343


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/diydrones/dronekit-python/blob/master/examples/guided_set_speed_yaw/guided_set_speed_yaw.py>`_):

.. include:: ../../examples/guided_set_speed_yaw/guided_set_speed_yaw.py
    :literal:
