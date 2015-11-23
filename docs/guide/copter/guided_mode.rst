.. _guided_mode_copter:

==============================
Guiding and Controlling Copter
==============================

GUIDED mode is the recommended mode for flying Copter autonomously without a predefined a mission. It allows a Ground Control Station (GCS) or :ref:`Companion Computer <supported-companion-computers>` to control the vehicle “on the fly” and react to new events or situations as they occur.

This topic explains how you can :ref:`control vehicle movement <guided_mode_copter_control_movement>`, and also how to send :ref:`MAVLink commands <guided_mode_copter_commands>` to control vehicle orientation, region of interest, servos and other hardware. We also :ref:`list a few functions <guided_mode_copter_useful_conversion_functions>` that are useful for converting location and bearings from a global into a local frame of reference. 

Most of the code can be observed running in :ref:`example-guided-mode-setting-speed-yaw`.

.. note::

    This topic is Copter specific. Plane apps typically use AUTO mode and dynamically modify missions as needed (Plane supports GUIDED mode but it is less full featured than on Copter).

.. todo:: 

    Revisit above tip when we have a Plane AUTO mode example. Also perhaps a Plane GUIDED mode topic, though that would be low priority. Also add something about Rover when we know more about how it works.

.. _guided_mode_copter_control_movement:

Controlling vehicle movement
============================

Copter movement can be controlled either by explicitly setting a :ref:`target position <guided_mode_copter_position_control>`, or by specifying the vehicle's :ref:`velocity components <guided_mode_copter_velocity_control>` to guide it in a preferred direction. 

.. note:: 

    Changing to a new movement method is treated as a "mode change". If you've set a yaw or region-of-interest value then this will be set to the default (vehicle faces the direction of travel).


.. _guided_mode_copter_position_control:

Position control
----------------

Controlling the vehicle by explicitly setting the target position is useful when the final position is known/fixed.

The recommended method for position control is :py:func:`Vehicle.simple_goto() <dronekit.Vehicle.simple_goto>`. 
This takes a :py:class:`LocationGlobal <dronekit.LocationGlobal>` or 
:py:class:`LocationGlobalRelative <dronekit.LocationGlobalRelative>` argument.

The method is used as shown below:

.. code-block:: python

    # Set mode to guided - this is optional as the goto method will change the mode if needed.
    vehicle.mode = VehicleMode("GUIDED")

    # Set the target location in global-relative frame
    a_location = LocationGlobalRelative(-34.364114, 149.166022, 30)
    vehicle.simple_goto(a_location)


``Vehicle.simple_goto()`` can be interrupted by a later command, and does not provide any functionality 
to indicate when the vehicle has reached its destination. Developers can use either a time delay or 
:ref:`measure proximity to the target <example_guided_mode_goto_convenience>` to give the vehicle an 
opportunity to reach its destination. The :ref:`example-guided-mode-setting-speed-yaw` shows both approaches.

You can optionally set the target movement speed using the function's ``airspeed`` or ``groundspeed`` parameters 
(this is equivalent to setting :py:attr:`Vehicle.airspeed <dronekit.Vehicle.airspeed>`
or :py:attr:`Vehicle.groundspeed <dronekit.Vehicle.groundspeed>`). The speed setting will then be used
for all positional movement commands until it is set to another value. 

.. code-block:: python

    # Set airspeed using attribute
    vehicle.airspeed = 5 #m/s

    # Set groundspeed using attribute
    vehicle.groundspeed = 7.5 #m/s
    
    # Set groundspeed using `simple_goto()` parameter
    vehicle.simple_goto(a_location, groundspeed=10)

.. note::

    ``Vehicle.simple_goto()`` will use the last speed value set. If both speed values are set at the
    same time the resulting behaviour will be vehicle dependent.


.. tip::

    You can also set the position by sending the MAVLink commands 
    `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ or 
    `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_, specifying 
    a ``type_mask`` bitmask that enables the position parameters. The main difference between these commands is 
    that the former allows you to specify the location relative to the "global" frames (like 
    ``Vehicle.simple_goto()``), while the later lets you specify the location in NED co-ordinates relative 
    to the home location or the vehicle itself. For more information on these options see the example code: 
    :ref:`example_guided_mode_goto_position_target_global_int` and :ref:`example_guided_mode_goto_position_target_local_ned`.



.. _guided_mode_copter_velocity_control:

Velocity control
----------------

Controlling vehicle movement using velocity is much smoother than using position when there are likely 
to be many updates (for example when tracking moving objects).

The function ``send_ned_velocity()`` below generates a ``SET_POSITION_TARGET_LOCAL_NED`` MAVLink message 
which is used to directly specify the speed components of the vehicle in the ``MAV_FRAME_LOCAL_NED`` 
frame (relative to home location). The message is re-sent every second for the specified duration. 

.. note::

    From Copter 3.3 the vehicle will stop moving if a new message is not received in approximately 3 seconds. 
    Prior to Copter 3.3 the message only needs to be sent once, and the velocity remains active until the next 
    movement command is received. The example code works for both cases!


.. code-block:: python

    def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
        """
        Move vehicle in direction based on specified velocity vectors. 
        """
        msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
            
            
        # send command to vehicle on 1 Hz cycle
        for x in range(0,duration):
            vehicle.send_mavlink(msg)
            time.sleep(1)
            
    
The ``type_mask`` parameter is a bitmask that indicates which of the other parameters in the message are used/ignored by the vehicle 
(0 means that the dimension is enabled, 1 means ignored). In the example the value 0b0000111111000111 
is used to enable the velocity components.

In the ``MAV_FRAME_LOCAL_NED`` the speed components ``velocity_x`` and ``velocity_y`` are parallel to the North and East 
directions (not to the front and side of the vehicle). 
The ``velocity_z`` component is perpendicular to the plane of ``velocity_x`` and ``velocity_y``, with a positive value **towards the ground**, following 
the right-hand convention. For more information about the ``MAV_FRAME_LOCAL_NED`` frame of reference, see this wikipedia article 
on `NED <http://en.wikipedia.org/wiki/North_east_down>`_.

.. tip::

    From Copter 3.3 you can `specify other frames <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned>`_,
    for example ``MAV_FRAME_BODY_OFFSET_NED`` makes the velocity components relative to the current vehicle heading.
    In Copter 3.2.1 (and earlier) the frame setting is ignored (``MAV_FRAME_LOCAL_NED`` is always used).



The code fragment below shows how to call this method: 

.. code-block:: python

    # Set up velocity mappings
    # velocity_x > 0 => fly North
    # velocity_x < 0 => fly South
    # velocity_y > 0 => fly East
    # velocity_y < 0 => fly West
    # velocity_z < 0 => ascend
    # velocity_z > 0 => descend
    SOUTH=-2
    UP=-0.5   #NOTE: up is negative!

    #Fly south and up.
    send_ned_velocity(SOUTH,0,UP,DURATION)

When moving the vehicle you can send separate commands to control the yaw (and other behaviour).

.. tip::

    You can also control the velocity using the 
    `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ 
    MAVLink command, as described in :ref:`example_guided_mode_send_global_velocity`. 



.. _guided_mode_copter_accel_force_control:

Acceleration and force control
------------------------------

ArduPilot does not currently support controlling the vehicle by specifying acceleration/force components.

.. note:: 

    The `SET_POSITION_TARGET_GLOBAL_INT <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT>`_ and 
    `SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ 
    MAVLink commands allow you to specify the acceleration, force and yaw. However, commands setting 
    these parameters are ignored by the vehicle.



.. _guided_mode_copter_commands:

Guided mode commands
=====================

This section explains how to send MAVLink commands, what commands can be sent, and lists a number of real examples you can use in your own code.


.. _guided_mode_how_to_send_commands:

Sending messages/commands
-------------------------

MAVLink commands are sent by first using :py:func:`message_factory() <dronekit.Vehicle.message_factory>` 
to encode the message and then calling :py:func:`send_mavlink() <dronekit.Vehicle.send_mavlink>` to send them.

.. note::
    
    Vehicles support a subset of the messages defined in the MAVLink standard. For more information
    about the supported sets see wiki topics:
    `Copter Commands in Guided Mode <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/>`_ 
    and `Plane Commands in Guided Mode <http://dev.ardupilot.com/wiki/plane-commands-in-guided-mode/>`_.

``message_factory()`` uses a factory method for the encoding. The name of this method will always be the 
lower case version of the message/command name with ``_encode`` appended. For example, to encode a 
`SET_POSITION_TARGET_LOCAL_NED <https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED>`_ 
message we call ``message_factory.set_position_target_local_ned_encode()`` with values for all the 
message fields as arguments:

.. code-block:: python

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target_system, target_component
        mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)

If a message includes ``target_system`` id you can set it to zero (DroneKit will automatically 
update the value with the correct ID for the connected vehicle). Similarly CRC fields and sequence numbers 
(if defined in the message type) can be set to zero as they are automatically updated by DroneKit.
The ``target_component`` is not updated by DroneKit, but should be set to 0 (broadcast) unless the message is 
really intended for a specific component. 


.. _guided_mode_how_to_send_commands_command_long:

In Copter, the `COMMAND_LONG message <https://pixhawk.ethz.ch/mavlink/#COMMAND_LONG>`_ can be used send/package 
*a number* of different `supported MAV_CMD commands <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/>`_. 
The factory function is again the lower case message name with suffix ``_encode`` (``message_factory.command_long_encode``). 
The message parameters include the actual command to be sent (in the code fragment below ``MAV_CMD_CONDITION_YAW``) and its fields.

.. code-block:: python

    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target_system, target_component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)


.. _guided_mode_supported_commands:

Supported commands
------------------

`Copter Commands in Guided Mode <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/>`_ lists all the commands that *can* be sent to Copter in GUIDED mode (in fact most of the commands can be sent in any mode!)

DroneKit-Python provides a friendly Python API that abstracts many of the commands. 
Where possible you should use the API rather than send messages directly> For example, use:

* :py:func:`Vehicle.simple_takeoff() <dronekit.Vehicle.simple_takeoff>` instead of the ``MAV_CMD_NAV_TAKEOFF`` command. 
* :py:func:`Vehicle.simple_goto() <dronekit.Vehicle.simple_goto>`, :py:attr:`Vehicle.airspeed <dronekit.Vehicle.airspeed>`, 
   or :py:attr:`Vehicle.groundspeed <dronekit.Vehicle.groundspeed>` rather than ``MAV_CMD_DO_CHANGE_SPEED``.

Some of the MAV_CMD commands that you might want to send include: 
:ref:`MAV_CMD_CONDITION_YAW <guided_mode_copter_set_yaw>`, 
:ref:`MAV_CMD_DO_SET_ROI <guided_mode_copter_set_roi>`, 
``MAV_CMD_DO_SET_SERVO``, 
``MAV_CMD_DO_REPEAT_SERVO``, 
``MAV_CMD_DO_SET_RELAY``, 
``MAV_CMD_DO_REPEAT_RELAY``, 
``MAV_CMD_DO_FENCE_ENABLE``, 
``MAV_CMD_DO_PARACHUTE``, 
``MAV_CMD_DO_GRIPPER``, 
``MAV_CMD_MISSION_START``. 
These would be sent in a ``COMMAND_LONG`` message :ref:`as discussed above <guided_mode_how_to_send_commands_command_long>`.



.. _guided_mode_copter_set_yaw:

Setting the Yaw
----------------

The vehicle "yaw" is the direction that the vehicle is facing in the horizontal plane. On Copter this yaw need not be the direction of travel (though it is by default).

You can set the yaw direction using the `MAV_CMD_CONDITION_YAW <http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw>`_ command, encoded in a ``COMMAND_LONG`` message as shown below.

.. code-block:: python

    def condition_yaw(heading, relative=False):
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

The command allows you to specify that whether the heading is an absolute angle in degrees (0 degrees is North) or a value that is relative to the previously set heading.

.. note:: 

    * The yaw will return to the default (facing direction of travel) after you set the mode or change the command used for controlling movement. 
    * `At time of writing <https://github.com/diydrones/ardupilot/issues/2427>`_ there is no *safe way* to return to the default yaw "face direction of travel" behaviour.
    * After taking off, yaw commands are ignored until the first "movement" command has been received.  
      If you need to yaw immediately following takeoff then send a command to "move" to your current position.
    * :ref:`guided_mode_copter_set_roi` may work to get yaw to track a particular point (depending on the gimbal setup).




.. _guided_mode_copter_set_roi:

Setting the ROI
---------------

Send the `MAV_CMD_DO_SET_ROI <http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_set_roi>`_ command to point camera gimbal at a specified region of interest (:py:class:`LocationGlobal <dronekit.LocationGlobal>`). The vehicle may also turn to face the ROI.

.. code-block:: python

    def set_roi(location):
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


.. versionadded:: Copter 3.2.1. You can explicitly reset the ROI by sending the 
    `MAV_CMD_DO_SET_ROI <http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_do_set_roi>`_ 
    command with zero in all parameters. The front of the vehicle will then follow the direction of travel.

The ROI (and yaw) is also reset when the mode, or the command used to control movement, is changed.



.. _guided_mode_copter_responses:

Command acknowledgements and response values
--------------------------------------------

ArduPilot typically sends a command acknowledgement indicating whether a command was received, and whether 
it was accepted or rejected. At time of writing there is no way to intercept this acknowledgement 
in the API (`#168 <https://github.com/dronekit/dronekit-python/pull/168>`_).

Some MAVLink messages request information from the autopilot, and expect the result to be returned 
in another message. Provided the message is handled by the AutoPilot in GUIDED mode you can send the request
and process the response by creating a :ref:`message listener <mavlink_messages_message_listener>`.


.. _guided_mode_copter_useful_conversion_functions:

Frame conversion functions
==========================

The functions in this section help convert between different frames-of-reference. In particular they
make it easier to navigate in terms of "metres from the current position" when using commands that take 
absolute positions in decimal degrees.

The methods are approximations only, and may be less accurate over longer distances, and when close 
to the Earth's poles.

.. code-block:: python

    def get_location_metres(original_location, dNorth, dEast):
        """
        Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
        specified `original_location`. The returned LocationGlobal has the same `alt` value
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
        if type(original_location) is LocationGlobal:
            targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
        elif type(original_location) is LocationGlobalRelative:
            targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
        else:
            raise Exception("Invalid Location object passed")
            
        return targetlocation;


.. code-block:: python

    def get_distance_metres(aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two `LocationGlobal` or `LocationGlobalRelative` objects.

        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


.. code-block:: python

    def get_bearing(aLocation1, aLocation2):
        """
        Returns the bearing between the two LocationGlobal objects passed as parameters.

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

.. tip:: 

    The `common.py <https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py>`_ file 
    in the ArduPilot test code may have other functions that you will find useful.
        


Other information
=================

* `NED Frame <http://en.wikipedia.org/wiki/North_east_down>`_
* `MISSION_ITEM <https://pixhawk.ethz.ch/mavlink/#MISSION_ITEM>`_
* `GUIDED Mode for Copter <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/ac2_guidedmode/>`_ (wiki).
* `GUIDED mode for Plane <http://plane.ardupilot.com/wiki/flying/flight-modes/#guided>`_ (wiki).
* `Copter Commands in Guided Mode <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/>`_ (wiki).
* `MAVLink mission command messages <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd>`_ (wiki).
* `GCS_Mavlink.cpp <https://github.com/diydrones/ardupilot/blob/master/ArduCopter/GCS_Mavlink.cpp>`_ (Copter)



