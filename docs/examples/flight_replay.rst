=========================
Example: Flight Replay
=========================

This example creates and runs a waypoint mission using position information in a TLOG file.

The log used in this example contains around 2700 points. We reduce this to a smaller number 
(that is able to fit on the autopilot) by taking 100 points that are evenly spread across the range. 
After 60 seconds the mission is artificially ended by setting the mode to RTL (return to launch).

.. figure:: flight_replay_example.png
    :width: 50%

    Mission generated from log

.. note::

    A more detailed example might determine the best points for the mission
    by mapping the path to lines and spline curves.


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`installing_dronekit`). 

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/flight_replay/
       
#. You can run the example against a simulator (DroneKit-SITL) by specifying the Python script without any arguments. 
   The example will download SITL binaries if needed, start the simulator, and then connect to it:

   .. code-block:: bash

       python flight_replay.py

   On the command prompt you should see (something like):
   
   .. code:: bash

       Generating waypoints from tlog...
        Generated 96 waypoints from tlog
       Starting copter simulator (SITL)
       SITL already Downloaded.
       Connecting to vehicle on: tcp:127.0.0.1:5760
       >>> APM:Copter V3.3 (d6053245)
       >>> Frame: QUAD
       >>> Calibrating barometer
       >>> Initialising APM...
       >>> barometer calibration complete
       >>> GROUND START
       Uploading 96 waypoints to vehicle...
       Arm and Takeoff
        Waiting for vehicle to initialise...
       >>> flight plan received
        Waiting for arming...
        ...
        Waiting for arming...
       >>> ARMING MOTORS
       >>> GROUND START
        Waiting for arming...
       >>> Initialising APM...
        Waiting for arming...
       >>> ARMING MOTORS
        Taking off!
        Altitude: 0.010000 < 28.500000
        Altitude: 0.020000 < 28.500000
        ...
        Altitude: 26.150000 < 28.500000
        Altitude: 28.170000 < 28.500000
        Reached target altitude of ~30.000000
       Starting mission
       Distance to waypoint (1): 6.31671220061
       Distance to waypoint (1): 5.54023406731
       >>> Reached Command #1
       Distance to waypoint (2): 4.05805003875
       ...
       Distance to waypoint (2): 4.66600036548
       >>> Reached Command #2
       Distance to waypoint (3): 1.49371523482
       Distance to waypoint (3): 0.13542601646
       Distance to waypoint (3): 0.708432959397
       >>> Reached Command #3
       Distance to waypoint (4): 3.29161427437
       Distance to waypoint (4): 3.63454331996
       Distance to waypoint (4): 2.89070828637
       >>> Reached Command #4
       Distance to waypoint (5): 0.955857968149
       >>> Reached Command #5
       >>> Reached Command #6
       >>> Reached Command #7
       ...
       >>> Reached Command #42
       Distance to waypoint (42): 7.6983209285
       ...
       Distance to waypoint (43): 6.05247510021
       >>> Reached Command #43
       Distance to waypoint (43): 4.80180763387
       >>> Reached Command #44
       Distance to waypoint (44): 3.89880557617
       ...
       Distance to waypoint (45): 11.0865559753
       >>> Reached Command #45
       Distance to waypoint (46): 9.45419808223
       ...
       Distance to waypoint (46): 13.2676499949
       Return to launch
       Close vehicle object
       Completed...

   .. tip::

       It is more interesting to watch the example run on a map than the console. The topic :ref:`viewing_uav_on_map` 
       explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).
       
#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python simple_goto.py --connect 127.0.0.1:14550
       

       
How it works
============

The example parses the **flight.tlog** file for position information. It then selects about 100
points that are evenly spread across the log and uploads them as a mission. 

For safety reasons, the altitude for the waypoints is set to 30 meters (irrespective of the recorded height).

Getting the points
------------------

The following simple function parses the tlog for points and then 
returns 100 evenly points from the collected set.

.. code:: python

    def position_messages_from_tlog(filename):
        """
        Given telemetry log, get a series of waypoints approximating the previous flight
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

            # Shrink the # of pts to be lower than the max # of wpts allowed by vehicle
        num_points = len(messages)
        max_points = 99
        if num_points > max_points:
            step = int(math.ceil((float(num_points) / max_points)))
            shorter = [messages[i] for i in xrange(0, num_points, step)]
            messages = shorter
        return messages



Setting the new waypoints
-------------------------

If necessary, the example then reduces the number of messages retrieved into a set that can fit on the vehicle (in this case 100 waypoints).

The following code shows how the vehicle writes the received messages as commands (this part of the code is very similar to that
shown in :ref:`example_mission_basic`):

.. code:: python

    print "Generating %s waypoints from replay..." % len(messages)
    cmds = vehicle.commands
    cmds.clear()
    for i in xrange(0, len(messages)):
        pt = messages[i]
        lat = pt['lat']
        lon = pt['lon']
        # To prevent accidents we don't trust the altitude in the original flight, instead
        # we just put in a conservative cruising altitude.
        altitude = 30.0 # pt['alt']
        cmd = Command( 0,
                       0,
                       0,
                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                       mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                       0, 0, 0, 0, 0, 0,
                       lat, lon, altitude)
        cmds.add(cmd)
    #Upload clear message and command messages to vehicle.
    cmds.upload()


Known issues
============

There are no known issues with this example.

  

Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/flight_replay/flight_replay.py>`_):


.. literalinclude:: ../../examples/flight_replay/flight_replay.py
   :language: python
