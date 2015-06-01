.. _example_simple_goto:

==============================
Example: Simple Go To (Copter)
==============================

This example demonstrates how to arm and launch a Copter in GUIDED mode, travel to a number of waypoints, and then return 
to the home location. It uses :py:func:`Vehicle.commands.takeoff() <droneapi.lib.CommandSequence.takeoff>`, 
:py:func:`Vehicle.commands.goto() <droneapi.lib.CommandSequence.goto>` and :py:attr:`Vehicle.mode <droneapi.lib.Vehicle.mode>`.

The locations used are centred around the home location when the :ref:`Simulated Vehicle <vagrant-sitl-from-full-image>` is booted; you can edit the latitude and longitude 
to use more appropriate positions for your own vehicle. 

.. note:: 

    This example will only run on *Copter*:

    * *Plane* does not support ``takeoff`` in GUIDED mode. 
    * *Rover* will ignore the ``takeoff`` command and will then stick at the altitude check.
   


Running the example
===================

The vehicle and DroneKit should be set up as described in the :ref:`quick-start` or :ref:`get-started`.

If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

Once MAVProxy is running and the API is loaded, you can start the example by typing: ``api start simple_goto.py``.

.. note:: 

    The command above assumes you started the *MAVProxy* prompt in a directory containing the example script. If not, 
    you will have to specify the full path to the script (something like):
    ``api start /home/user/git/dronekit-python/examples/simple_goto/simple_goto.py``.

.. tip::	

    It is more interesting to watch the example above on a map than the console. The topic :ref:`viewing_uav_on_map` 
    explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).

On the *MAVProxy* console you should see (something like):

.. code-block:: python

    MAV> api start simple_goto.py
    STABILIZE> Basic pre-arm checks
    Arming motors
     Waiting for arming...
     Waiting for arming...
    APM: ARMING MOTORS
    APM: GROUND START
     Waiting for arming...
     Waiting for arming...
    GUIDED> Mode GUIDED
    APM: Initialising APM...
    Got MAVLink msg: COMMAND_ACK {command : 400, result : 0}
    Waiting for arming...
    ARMED
    Taking off!
     Altitude:  0.0
    Got MAVLink msg: COMMAND_ACK {command : 22, result : 0}
     Altitude:  0.10000000149
     Altitude:  0.620000004768
     ...
     Altitude:  19.25
    Reached target altitude
    Going to first point...
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    Going to second point...
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    Returning to Launch
    APIThread-0 exiting...	
	
.. tip::	

    If you get stuck in ``Waiting for arming...`` it is very likely that the vehicle did not pass all pre-arm checks. 
    On a real device you can view the controller LEDs to determine likely issues. On the Simulator console you 
    can disable the checks if needed:

    .. code-block:: bash

        STABILIZE>param load ../Tools/autotest/copter_params.parm
        STABILIZE>param set ARMING_CHECK 0


How does it work?
=================

The code has three distinct sections: arming and takeoff, flight to a specified location, and return-to-home.

Takeoff
-------

To launch *Copter* you need to set the mode to ``GUIDED``, arm the vehicle, and then call 
:py:func:`Vehicle.commands.takeoff() <droneapi.lib.CommandSequence.takeoff>`. The takeoff code in this example
is explained in the guide topic :ref:`taking-off`.

	
Flying to a point - Goto
------------------------

The vehicle is already in ``GUIDED`` mode, so to send it to a certain point we just need to 
call :py:func:`Vehicle.commands.goto() <droneapi.lib.CommandSequence.goto>` with the target location, 
and then :py:func:`flush() <droneapi.lib.Vehicle.flush>` the command:

.. code-block:: python	

    point1 = Location(-35.361354, 149.165218, 20, is_relative=True)
    vehicle.commands.goto(point1)
    vehicle.flush()

    # sleep so we can see the change in map
    time.sleep(30)

Without some sort of "wait" the next command would be executed immediately. In this example we just 
sleep for 30 seconds - a good opportunity to observe the vehicle's movement on a map. 


RTL - Return to launch
------------------------

To return to the home position and land, we set the mode to ``RTL``:

.. code-block:: python	

    vehicle.mode    = VehicleMode("RTL")
    vehicle.flush()


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/diydrones/dronekit-python/blob/master/examples/simple_goto/simple_goto.py>`_):

.. literalinclude:: ../../examples/simple_goto/simple_goto.py
    :language: python