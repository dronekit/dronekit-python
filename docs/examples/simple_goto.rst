.. _example_simple_goto:

==============================
Example: Simple Go To (Copter)
==============================

This example demonstrates how to arm and launch a Copter in GUIDED mode, travel towards a number of target points, and then return 
to the home location. It uses :py:func:`Vehicle.commands.takeoff() <dronekit.lib.CommandSequence.takeoff>`, 
:py:func:`Vehicle.commands.goto() <dronekit.lib.CommandSequence.goto>` and :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>`.

The target locations are centred around the home location when the :ref:`Simulated Vehicle <vagrant-sitl-from-full-image>` is booted; 
you can edit the latitude and longitude to use more appropriate positions for your own vehicle. 

.. note:: 

    This example will only run on *Copter*:

    * *Plane* does not support ``takeoff`` in GUIDED mode. 
    * *Rover* will ignore the ``takeoff`` command and will then stick at the altitude check.
   

.. figure:: simple_goto_example_copter_path.png
   :width: 50 %
   :alt: Setting destination using position and changing speed and ROI

   Simple Goto Example: Flight path
   
   

Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`).

If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/simple_goto/


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python simple_goto.py --connect 127.0.0.1:14550

   .. note::
   
       The ``--connect`` parameter above connects to SITL on udp port 127.0.0.1:14550.
       This is the default value for this example, and may be omitted. 

       
.. tip::

    It is more interesting to watch the example above on a map than the console. The topic :ref:`viewing_uav_on_map` 
    explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).

On the command prompt you should see (something like):

.. code-block:: bash

    Connecting to vehicle on: 127.0.0.1:14550
    >>> APM:Copter V3.4-dev (e0810c2e)
    >>> Frame: QUAD
    Basic pre-arm checks
     Waiting for vehicle to initialise...
     Waiting for vehicle to initialise...
     Waiting for vehicle to initialise...
     Waiting for vehicle to initialise...
     Waiting for vehicle to initialise...
    Arming motors
     Waiting for arming...
     Waiting for arming...
     Waiting for arming...
    >>> ARMING MOTORS
    >>> GROUND START
     Waiting for arming...
     Waiting for arming...
    >>> Initialising APM...
    Taking off!
     Altitude:  0.0
     Altitude:  0.00999999977648
     Altitude:  0.25
     Altitude:  0.5
    ...
     Altitude:  18.7299995422
     Altitude:  19.2700004578
    Reached target altitude
    Going to first point...
    Going to second point...
    Returning to Launch
    Close vehicle object

.. tip::

    The code waits on :py:func:`Vehicle.is_armable <dronekit.lib.Vehicle.is_armable>`, so you shouldn't get stuck in ``Waiting for arming...``.
    If you do, then:
    
    * On a real device you can view the controller LEDs to determine possible causes. 
    * On the Simulator console you can disable the checks if needed:

      .. code-block:: bash

          STABILIZE>param load ../Tools/autotest/copter_params.parm
          STABILIZE>param set ARMING_CHECK 0


How does it work?
=================

The code has three distinct sections: arming and takeoff, flight to two locations, and return-to-home.

Takeoff
-------

To launch *Copter* you need to first check that the vehicle :py:func:`Vehicle.is_armable <dronekit.lib.Vehicle.is_armable>`. 
Then set the mode to ``GUIDED``, arm the vehicle, and call 
:py:func:`Vehicle.commands.takeoff() <dronekit.lib.CommandSequence.takeoff>`. The takeoff code in this example
is explained in the guide topic :ref:`taking-off`.


Flying to a point - Goto
------------------------

The vehicle is already in ``GUIDED`` mode, so to send it to a certain point we just need to 
call :py:func:`Vehicle.commands.goto() <dronekit.lib.CommandSequence.goto>` with the target ``LocationGlobal``:

.. code-block:: python

    point1 = LocationGlobal(-35.361354, 149.165218, 20, is_relative=True)
    vehicle.commands.goto(point1)

    # sleep so we can see the change in map
    time.sleep(30)

Without some sort of "wait" the next command would be executed immediately. In this example we just 
sleep for 30 seconds, set a new destination and then sleep another 30 seconds (the vehicle doesn't reach
its target destination in either 30 second wait). The script doesn't report anything during these sleep periods, 
but you can observe the vehicle's movement on a ground station map.




RTL - Return to launch
------------------------

To return to the home position and land, we set the mode to ``RTL``:

.. code-block:: python

    vehicle.mode    = VehicleMode("RTL")


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/simple_goto/simple_goto.py>`_):

.. literalinclude:: ../../examples/simple_goto/simple_goto.py
    :language: python