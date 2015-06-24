.. _example-guided-mode-setting-speed-yaw:

===================================================
Example: Guided Mode Movement and Commands (Copter)
===================================================

This example shows how to control Copter movement and send immediate commands in :ref:`GUIDED mode <guided_mode_copter>`. It demonstrates three methods for explicitly specifying a target position and two commands for controlling movement by setting the vehicle's velocity vectors. It also shows how to send commands to control the yaw (direction that the front of the vehicle is pointing), region of interest, speed and home position, along with some useful functions for converting between frames of reference.

The example is :ref:`documented in the source code <guided_example_source_code>`. More detailed information about using GUIDED mode can be found in the guide: :ref:`guided_mode_copter`.


.. figure:: GuidedModeExample_FlyByPosition.png
   :width: 50 %
   :alt: Setting destination using position and changing speed and ROI

   Setting destination using position and changing speed and ROI

   
.. figure:: GuidedModeExample_FlyByVelocity.png
   :width: 50 %
   :alt: Setting destination using velocity and changing yaw and home location

   Setting destination using velocity and changing yaw and home location



Running the example
===================

The vehicle and DroneKit should be set up as described in :ref:`get-started`.
If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

Once *MAVProxy* is running and the API is loaded, you can start the example by typing: ``api start guided_set_speed_yaw.py``.

.. note:: 

    The command above assumes you started the *MAVProxy* prompt in a directory containing the example script. If not, 
    you will have to specify the full path to the script (e.g. on Linux):
    ``api start /home/user/git/dronekit-python/examples/guided_set_speed_yaw/guided_set_speed_yaw.py``.

On the *MAVProxy* console you should see (something like):

::

    MAV> api start /home/user/git/dronekit-python/examples/guided_set_speed_yaw/guided_set_speed_yaw.py
    STABILIZE> Basic pre-arm checks
    Arming motors
     Waiting for arming...
     Waiting for arming...
    GUIDED>  Waiting for arming...
    Taking off!
     Altitude:  0.00999999977648
     Altitude:  0.159999996424
     Altitude:  0.920000016689
     Altitude:  2.38000011444
     Altitude:  3.93000006676
     Altitude:  4.65000009537
     Altitude:  4.82999992371
    Reached target altitude

    TRIANGLE path using standard Vehicle.commands.goto()
    Position North 80 West 50
    Distance to target:  100.792762965
    Distance to target:  100.25918006
    ...
    Distance to target:  2.34237912414
    Distance to target:  0.308823685384
    Reached target
    Position North 0 East 100
    Distance to target:  122.62321461
    ...
    Distance to target:  5.39403923852
    Distance to target:  1.00445126117
    Reached target
    Position North -80 West 50
    goto_target_globalint_position
    Distance to target:  100.792430952
    Distance to target:  100.221083739
    ...
    Distance to target:  1.69678155659
    Distance to target:  0.0798488767383
    Reached target

    TRIANGLE path using standard SET_POSITION_TARGET_GLOBAL_INT message and with varying speed.
    Position South 100 West 130
    Set speed to 5m/s.
    Distance to target:  181.439594672
    Distance to target:  132.170351744
    ...
    Distance to target:  2.67615248028
    Distance to target:  0.382959594982
    Reached target
    Set speed to 15m/s (max).
    Position South 0 East 200
    Distance to target:  318.826739407
    Distance to target:  317.613357051
    ...
    Distance to target:  3.5935761745
    Distance to target:  0.114090613451
    Reached target
    Set speed to 10m/s (max).
    Position North 100 West 130
    goto_target_globalint_position
    Distance to target:  188.182423388
    Distance to target:  187.540272979
    ...
    Distance to target:  4.82317050152
    Distance to target:  0.377390539948
    Reached target

    SQUARE path using SET_POSITION_TARGET_LOCAL_NED and position parameters
    North 50m, East 0m, 10m altitude for 20 seconds
    Point ROI at current location (home position)
    North 50m, East 50m, 10m altitude
    Point ROI at current location
    North 0m, East 50m, 10m altitude
    North 0m, East 0m, 10m altitude

    SQUARE path using SET_POSITION_TARGET_LOCAL_NED and velocity parameters
    Velocity South & up
    Yaw 180 absolute (South)
    Velocity West & down
    Yaw 270 absolute (West)
    Velocity North
    Yaw 0 absolute (North)
    Velocity East

    DIAMOND path using SET_POSITION_TARGET_GLOBAL_INT and velocity parameters
    Velocity North, East and up
    Yaw 225 absolute   
    Velocity South, East and down
    Yaw 90 relative (to previous yaw heading)
    Set new Home location to current location
    Get new home location
     Home WP: MISSION_ITEM {target_system : 255, target_component : 0, seq : 0, frame : 0, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x :
    -35.3632583618, y : 149.164352417, z : 593.91998291}
    Velocity South and West
    Yaw 90 relative (to previous yaw heading)
    Velocity North and West
    Yaw 90 relative (to previous yaw heading)

    Setting LAND mode...
    Completed
    APIThread-0 exiting...
    LAND>



How does it work?
=================

The example is :ref:`documented in source code <guided_example_source_code>`. Additional information on the methods is provided either below or :ref:`in the guide <guided_mode_copter>`.

The functions for controlling vehicle movement are:

* :ref:`Vehicle.commands.goto() <guided_mode_copter_position_control>` is the standard DroneKit position controller method. It is called from :ref:`goto <example_guided_mode_goto_convenience>` to fly a triangular path.
* :ref:`goto_position_target_global_int() <example_guided_mode_goto_position_target_global_int>` is a position controller that uses the `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ command.
* :ref:`goto_position_target_local_ned() <example_guided_mode_goto_position_target_local_ned>` is a position controller that uses `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ command (taking values in NED frame, relative to the home position). This is used to fly a square path. The script is put to sleep for a certain time in order to allow the vehicle to reach the specified position.
* :ref:`send_ned_velocity() <guided_mode_copter_velocity_control>` is a velocity controller. It uses `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ to fly a square path using velocity vectors to define the speed in each direction. 
* :ref:`send_global_velocity() <example_guided_mode_send_global_velocity>` is a velocity controller. It uses `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ to fly a diamond-shaped path. The behaviour is essentially the same as for ``send_ned_velocity()`` because the velocity components in both commands are in the NED frame.
* :ref:`goto <example_guided_mode_goto_convenience>` is a convenience function for specifying a target location in metres from the current location and reporting the result. 


The functions sending immediate commands are:

* :ref:`condition_yaw() <guided_mode_copter_set_yaw>` 
* :ref:`set_roi(location) <guided_mode_copter_set_roi>`
* :ref:`set_speed(speed) <guided_mode_copter_set_speed>`
* :ref:`set_home() <guided_mode_copter_set_home>`

The example uses a number functions to convert global locations co-ordinates (decimal degrees) into local coordinates relative to the vehicle (in metres). These are :ref:`described in the guide <guided_mode_copter_useful_conversion_functions>`.

.. _example_guided_mode_goto_convenience:

goto() - convenience function
-----------------------------

This is a convenience function for setting position targets in metres North and East of the current location. It reports the distance to the target every two seconds and completes when the target is reached.

This takes a function argument of either :ref:`Vehicle.commands.goto() <guided_mode_copter_position_control>` or :ref:`goto_position_target_global_int() <example_guided_mode_goto_position_target_global_int>`

.. code-block:: python

    def goto(dNorth, dEast, gotoFunction=vehicle.commands.goto):
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



.. _example_guided_mode_send_ned_velocity:

send_ned_velocity()
-------------------

The function ``send_ned_velocity()`` generates a ``SET_POSITION_TARGET_LOCAL_NED`` MAVLink message 
which is used to directly specify the speed components of the vehicle. The distance travelled is controlled 
by a delay before the next command is sent.

This is documented in :ref:`the guide here <guided_mode_copter_velocity_control>`.


.. _example_guided_mode_send_global_velocity:

send_global_velocity()
----------------------

The function ``send_global_velocity()`` generates a `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ MAVLink message 
which is used to directly specify the speed components of the vehicle. The function behaviour is otherwise exactly the same as when using :ref:`SET_POSITION_TARGET_LOCAL_NED <guided_mode_copter_velocity_control>` 

.. code-block:: python

    def send_global_velocity(velocity_x, velocity_y, velocity_z):
        """
        Move vehicle in direction based on specified velocity vectors.
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


		
.. _example_guided_mode_goto_position_target_global_int:

goto_position_target_global_int()
---------------------------------

The function ``goto_position_target_global_int()`` generates a `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ MAVLink message 
which is used to directly specify the target location of the vehicle. When used with ``MAV_FRAME_GLOBAL_RELATIVE_ALT_INT`` as shown below, this method is effectively the same as  :ref:`Vehicle.commands.goto <guided_mode_copter_position_control>`.
		
.. code-block:: python

    def goto_position_target_global_int(aLocation):
        """
        Send SET_POSITION_TARGET_GLOBAL_INT command to request the vehicle fly to a specified location.
	    """
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

In the example code this function is called from the :ref:`goto() <example_guided_mode_goto_convenience>` convenience function.	



.. _example_guided_mode_goto_position_target_local_ned:

goto_position_target_local_ned()
--------------------------------

The function ``goto_position_target_local_ned()`` generates a `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ MAVLink message 
which is used to directly specify the target location in the North, East, Down frame. The ``type_mask`` enables the position parameters (the last three bits of of the mask are zero).

.. warning:: 

    In the NED frame positive altitudes are entered as negative "Down" values. 
    So if down is "10", this will be 10 metres below the home altitude.

.. note:: 

    The `documentation <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ lists a number of possible frames of reference. At time of writing experimentation indicates that the actual frame use is always relative to the home location (not the vehicle, as indicated by MAV_FRAME_BODY_NED).


.. code-block:: python	

    def goto_position_target_local_ned(north, east, down):
        """	
        Send SET_POSITION_TARGET_LOCAL_NED command to request the vehicle fly to a specified 
        location in the North, East, Down frame.
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
		
At time of writing, acceleration and yaw bits are ignored.		


Testbed settings
================

This demo has been tested on Windows against SITL running both natively and in a virtual machine (as described in :ref:`get-started`).

DroneKit environment (from PIP):

* droneapi: 1.2.0
* pymavlink: 1.1.57
* MAVProxy: 1.4.23
* protobuf: 2.6.1

ArduPilot version: 

* `3.3.0beta2 <https://github.com/diydrones/ardupilot/commit/c73945686c821cab1034c0d434fc7d3f66a0fd50>`_.



.. _guided_example_source_code:

Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/diydrones/dronekit-python/blob/master/examples/guided_set_speed_yaw/guided_set_speed_yaw.py>`_):

.. literalinclude:: ../../examples/guided_set_speed_yaw/guided_set_speed_yaw.py
    :language: python

