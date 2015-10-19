.. _example_mission_basic:

======================
Example: Basic Mission
======================

This example demonstrates the basic mission operations provided by DroneKit-Python, including:
downloading missions from the vehicle, clearing missions, creating mission commands
and uploading them to the vehicle, monitoring the current active command, and changing the active 
command. 

The guide topic :ref:`auto_mode_vehicle_control` provides more detailed explanation of how the API
should be used.


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`).

If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python\examples\mission_basic\


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python mission_basic.py --connect 127.0.0.1:14550

   .. note::
   
       The examples uses the ``--connect`` parameter to pass the :ref:`connection string <get_started_connect_string>` into the script. 
       The command above would be used to connect to :ref:`SITL <sitl_setup>` running on the local machine via UDP port 14550.

       
.. tip::

    It is more interesting to watch the example above on a map than the console. The topic :ref:`viewing_uav_on_map` 
    explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).

On the command prompt you should see (something like):


.. code:: bash

    \dronekit-python\examples\mission_basic>mission_basic.py
    Connecting to vehicle on: 127.0.0.1:14550
    >>> ☺APM:Copter V3.4-dev (e0810c2e)
    >>> ☺Frame: QUAD
    Clear the current mission

    Requesting 0 waypoints t=Wed Jul 29 21:27:58 2015 now=Wed Jul 29 21:27:58 2015
    Create a new mission
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    Sent waypoint 0 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 0, frame : 0, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.3632621765, y : 149.165237427, z : 584.0}
    Sent waypoint 1 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 1, frame : 3, command : 22, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 0, y : 0, z : 10}
    Sent waypoint 2 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 2, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : -35.3628118424, y : 149.164679124, z : 11}
    Sent waypoint 3 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 3, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : -35.3628118424, y : 149.165780676, z : 12}
    Sent waypoint 4 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 4, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : -35.3637101576, y : 149.165780676, z : 13}
    Sent waypoint 5 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 5, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : -35.3637101576, y : 149.164679124, z : 14}
    Sent all 6 waypoints
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    APM: flight plan received
    Basic pre-arm checks
    Arming motors
     Waiting for arming...
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
     Waiting for arming...
    APM: ARMING MOTORS
    APM: GROUND START
     Waiting for arming...
    GUIDED> Mode GUIDED
    APM: Initialising APM...
    Got MAVLink msg: COMMAND_ACK {command : 400, result : 0}
     Waiting for arming...
    ARMED
    Taking off!
     Altitude:  0.0
    Got MAVLink msg: COMMAND_ACK {command : 22, result : 0}
    GPS lock at 0 meters
     Altitude:  0.10000000149
     ...
     Altitude:  8.84000015259
     Altitude:  9.60999965668
    Reached target altitude
    Starting mission
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
    waypoint 1
    waypoint 2
    AUTO> Mode AUTO
    Distance to waypoint (2): 79.3138466142
    Distance to waypoint (2): 79.1869592549
    Distance to waypoint (2): 77.8436803794
    ...
    Distance to waypoint (2): 20.7677087176
    Distance to waypoint (2): 15.4592692026
    APM: Reached Command #2
    waypoint 3
    Distance to waypoint (3): 115.328425048
    Skipping to Waypoint 4 when reach waypoint 3
    waypoint 4
    Distance to waypoint (4): 152.376018911
    Distance to waypoint (4): 154.882233097
    ...
    Distance to waypoint (4): 20.4052797291
    Distance to waypoint (4): 15.0592597507
    APM: Reached Command #4
    waypoint 5
    Distance to waypoint (5): 114.450267446
    Exit 'standard' mission when start heading to final waypoint (5)
    Return to launch
    APIThread-0 exiting...



How does it work?
=================

The :ref:`source code <example_mission_basic_source_code>` is relatively self-documenting, and most of its main
operations are explained in the guide topic :ref:`auto_mode_vehicle_control` .

In overview, the example first calls ``clear_mission()`` to clear the current mission and then creates and 
uploads a new mission using ``adds_square_mission(vehicle.location,50)``. This function defines a mission with a takeoff 
command and four waypoints arranged in a square around the central position.

After taking off (in guided mode using the ``takeoff()`` function) the example starts the mission by setting the mode to AUTO:

.. code:: python

    print "Starting mission"
    # Set mode to AUTO to start mission
    vehicle.mode = VehicleMode("AUTO")
    vehicle.flush()

The progress of the mission is monitored in a loop. The convenience function 
:ref:`distance_to_current_waypoint() <auto_mode_mission_distance_to_waypoint>` 
gets the distance to the next waypoint and 
:py:func:`Vehicle.commands.next <dronekit.lib.CommandSequence.next>` gets the value of
the next command.

We also show how to move to a specified command using
:py:func:`Vehicle.commands.next <dronekit.lib.CommandSequence.next>` (note how we skip the third command below):

.. code:: python

    while True:
        nextwaypoint =vehicle.commands.next
        if nextwaypoint  > 1:
            print 'Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint())
        if nextwaypoint ==3: #Skip to next waypoint
            print 'Skipping to Waypoint 4 when reach waypoint 3'
            vehicle.commands.next=4
        if nextwaypoint ==5: #Skip to next waypoint
            print "Exit 'standard' mission when start heading to final waypoint (5)"
            break;
        time.sleep(1)

When the vehicle starts the 5th command the loop breaks and the mode is set to RTL (return to launch).


.. _example_mission_basic_known_issues:

Known issues
============

This example fails in DroneKit 2.0.0b6 (see `#355 DKPY2 Can't clear waypoints  <https://github.com/dronekit/dronekit-python/issues/355>`_).


.. todo:: 

    This is blocked by https://github.com/dronekit/dronekit-python/issues/355 (vehicle.commands.clear not working).
    The code output in "running the example needs to be updated once this runs cleanly.
    The above text for the error needs to be replaced with original text 
       > "This example works around the :ref:`known issues in the API <auto_mode_mission_known_issues>`. 
       > Provided that the vehicle is connected and able to arm, it should run through to completion."
    Need to check all that clearing is still strictly necessary in DKPY2 which handles race conditions more gracefully.
    Add image of waypoints /flight for top of page.



.. _example_mission_basic_source_code:

Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/mission_basic/mission_basic.py>`_):

.. literalinclude:: ../../examples/mission_basic/mission_basic.py
   :language: python

