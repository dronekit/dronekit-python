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

.. figure:: mission_basic_example_copter_path.png
   :width: 50 %
   :alt: Basic Mission Path

   Basic Mission Example: Flight path


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/mission_basic/

#. You can run the example against a simulator (DroneKit-SITL) by specifying the Python script without any arguments.
   The example will download SITL binaries (if needed), start the simulator, and then connect to it:

   .. code-block:: bash

       python mission_basic.py

   On the command prompt you should see (something like):
   
   .. code:: bash

       Starting copter simulator (SITL)
       SITL already Downloaded.
       Connecting to vehicle on: tcp:127.0.0.1:5760
       >>> APM:Copter V3.3 (d6053245)
       >>> Frame: QUAD
       >>> Calibrating barometer
       >>> Initialising APM...
       >>> barometer calibration complete
       >>> GROUND START
       >>> Mission Planner 1.3.35
       Create a new mission (for current location)
        Clear any existing commands
        Define/add new commands.
        Upload new commands to vehicle
       Basic pre-arm checks
        Waiting for vehicle to initialise...
       >>> flight plan received
        Waiting for vehicle to initialise...
        ...
        Waiting for vehicle to initialise...
       Arming motors
        Waiting for arming...
        ...
        Waiting for arming...
       >>> ARMING MOTORS
       >>> GROUND START
        Waiting for arming...
       >>> Initialising APM...
       Taking off!
        Altitude:  0.0
        Altitude:  0.11
        ...
        Altitude:  8.9
        Altitude:  9.52
       Reached target altitude
       Starting mission
       Distance to waypoint (0): None
       Distance to waypoint (1): 78.8000191616
       Distance to waypoint (1): 78.3723704927
       ...
       Distance to waypoint (1): 20.7131390269
       Distance to waypoint (1): 15.4196151863
       >>> Reached Command #1
       Distance to waypoint (2): 115.043560356
       Distance to waypoint (2): 117.463458185
       ...
       Distance to waypoint (2): 25.7122243168
       Distance to waypoint (2): 16.8624794106
       >>> Reached Command #2
       Distance to waypoint (3): 100.45231832
       Skipping to Waypoint 5 when reach waypoint 3
       Distance to waypoint (5): 154.645144788
       Exit 'standard' mission when start heading to final waypoint (5)
       Return to launch
       Close vehicle object


   .. tip::

       It is more interesting to watch the example run on a map than the console. The topic :ref:`viewing_uav_on_map` 
       explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).
       
#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python mission_basic.py --connect 127.0.0.1:14550  



How does it work?
=================

The :ref:`source code <example_mission_basic_source_code>` is relatively self-documenting, and most of its main
operations are explained in the guide topic :ref:`auto_mode_vehicle_control` .

In overview, the example calls ``adds_square_mission(vehicle.location.global_frame,50)`` to first  
clear the current mission and then define a new mission with a takeoff command and four waypoints arranged
in a square around the central position (two waypoints are added in the last position - 
we use :py:func:`next <dronekit.CommandSequence.next>` to determine when we've reached the final point).  
The clear command and new mission items are then uploaded to the vehicle.

After taking off (in guided mode using the ``takeoff()`` function) the example starts the mission by setting the mode to AUTO:

.. code:: python

    print "Starting mission"
    # Set mode to AUTO to start mission
    vehicle.mode = VehicleMode("AUTO")

The progress of the mission is monitored in a loop. The convenience function 
:ref:`distance_to_current_waypoint() <auto_mode_mission_distance_to_waypoint>` 
gets the distance to the next waypoint and 
:py:func:`Vehicle.commands.next <dronekit.CommandSequence.next>` gets the value of
the next command.

We also show how to jump to a specified command using
:py:func:`Vehicle.commands.next <dronekit.CommandSequence.next>` (note how we skip the third command below):

.. code:: python

    while True:
        nextwaypoint=vehicle.commands.next
        print 'Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint())
      
        if nextwaypoint==3: #Skip to next waypoint
            print 'Skipping to Waypoint 5 when reach waypoint 3'
            vehicle.commands.next=5
            vehicle.commands.upload()
        if nextwaypoint==5: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print "Exit 'standard' mission when start heading to final waypoint (5)"
            break;
        time.sleep(1)

When the vehicle starts the 5th command (a dummy waypoint) the loop breaks and the mode is set to RTL (return to launch).


.. _example_mission_basic_known_issues:

Known issues
============

This example has no known issues.


.. _example_mission_basic_source_code:

Source code
===========

The full source code at documentation build-time is listed below 
(`current version on Github <https://github.com/dronekit/dronekit-python/blob/master/examples/mission_basic/mission_basic.py>`_):

.. literalinclude:: ../../examples/mission_basic/mission_basic.py
   :language: python

