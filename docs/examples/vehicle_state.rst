.. _example-vehicle-state:

======================
Example: Vehicle State
======================

This example shows how to get/set vehicle attribute, parameter and channel-override information, 
how to observe vehicle attribute changes, and how to get the home position.

The guide topic :ref:`vehicle-information` provides a more detailed explanation of how the API
should be used.


Running the example
===================

The vehicle and DroneKit should be set up as described in the :ref:`quick-start` or :ref:`get-started`.
If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

Once MAVProxy is running and the API is loaded, you can start the example by typing: ``api start vehicle_state.py``.

.. note:: 

    The command above assumes you started the *MAVProxy* prompt in a directory containing the example script. If not, 
    you will have to specify the full path to the script (something like):
    ``api start /home/user/git/dronekit-python/examples/vehicle_state/vehicle_state.py``.


On the *MAVProxy* console you should see (something like):

.. code:: bash

    MAV> api start vehicle_state.py
    STABILIZE>

    Get all vehicle attribute values:
     Location:  Attitude: Attitude:pitch=-0.00405988190323,yaw=-0.0973932668567,roll=-0.00393210304901
     Velocity: [0.06, -0.07, 0.0]
     GPS: GPSInfo:fix=3,num_sat=10
     groundspeed: 0.0
     airspeed: 0.0
     mount_status: [None, None, None]
     Mode: STABILIZE
     Armed: False
    Set Vehicle.mode=GUIDED (currently: STABILIZE)
     Waiting for mode change ...
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
    GUIDED> Mode GUIDED
    Set Vehicle.armed=True (currently: False)
     Waiting for arming...
    APM: ARMING MOTORS
    APM: Initialising APM...
    Got MAVLink msg: COMMAND_ACK {command : 400, result : 0}
    ARMED

    Add mode attribute observer for Vehicle.mode
     Set mode=STABILIZE (currently: GUIDED)
     Wait 2s so callback invoked before observer removed
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
    STABILIZE> Mode STABILIZE
     CALLBACK: Mode changed to:  STABILIZE

    Get home location
    Requesting 0 waypoints t=Fri May 15 11:35:58 2015 now=Fri May 15 11:35:58 2015
     Home WP: MISSION_ITEM {target_system : 255, target_component : 0, seq : 0, frame : 0, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.3632621765, y : 149.165237427, z : 583.729980469}

    Read vehicle param 'THR_MIN': 130.0
    Write vehicle param 'THR_MIN' : 10
    timeout setting THR_MIN to 10.000000
    Read new value of param 'THR_MIN': 10.0

    Overriding RC channels for roll and yaw
     Current overrides are: {'1': 900, '4': 1000}
     Channel default values: {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800}
     Cancelling override

    Reset vehicle atributes/parameters and exit
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
    APM: DISARMING MOTORS
    Got MAVLink msg: COMMAND_ACK {command : 400, result : 0}
    DISARMED
    timeout setting THR_MIN to 130.000000
    APIThread-0 exiting...



How does it work?
=================

The guide topic :ref:`vehicle-information` provides an explanation of how this code works.

.. INTERNAL COMMENT: 

    Normally we'd highlight code here but all of it is worth of highlight, and we do that in the
    linked guide


Known issues
============

This example works around the :ref:`known issues in the API <api-information-known-issues>`. 
Provided that the vehicle is connected and able to arm, it should run through to completion.

Two cases where you may observe issues are:

* You will see an error ``Timeout setting THR_MIN to 10.000000``. This can be ignored because the value is actually set. 
  See `#12 Timeout error when setting a parameter <https://github.com/diydrones/dronekit-python/issues/12>`_ for information. 
* When the observer sets the mode callback, it waits two seconds after changing the mode before removing the observer
  (to ensure that the callback function is run before the observer is removed). In this time you may see the callback being 
  called twice even though the mode is only changed once. 
  See `#60 Attribute observer callbacks are called with heartbeat until disabled - after first called  <https://github.com/diydrones/dronekit-python/issues/60>`_ 
  for more information.



Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/diydrones/dronekit-python/blob/master/examples/simple_goto/simple_goto.py>`_):
	
.. literalinclude:: ../../examples/vehicle_state/vehicle_state.py
   :language: python
	
