.. _example-vehicle-state:

======================
Example: Vehicle State
======================

This example shows how to get/set vehicle attribute and parameter information, 
how to observe vehicle attribute changes, and how to get the home position.

The guide topic :ref:`vehicle-information` provides a more detailed explanation 
of how the API should be used.


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that 
the vehicle and DroneKit have been set up as described in :ref:`get-started`).

If you're using a simulated vehicle remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run. You can also 
`add a virtual rangefinder <http://dev.ardupilot.com/wiki/using-sitl-for-ardupilot-testing/#adding_a_virtual_rangefinder>`_
(otherwise the :py:attr:`Vehicle.rangefinder <dronekit.lib.Vehicle.rangefinder>` attribute may return values of ``None`` for the distance
and voltage). 

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/vehicle_state/


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python vehicle_state.py --connect 127.0.0.1:14550

   .. note::
   
       The ``--connect`` parameter above connects to SITL on udp port 127.0.0.1:14550.
       This is the default value for the parameter, and may be omitted. 
          


On the command prompt you should see (something like):

.. code:: bash

    Connecting to vehicle on: 127.0.0.1:14550
    >>> APM:Copter V3.3 (d6053245)
    >>> Frame: QUAD

    Accumulating vehicle attribute messages

    Get all vehicle attribute values:
     Global Location: LocationGlobal:lat=-35.3632615,lon=149.1652301,alt=0.0,is_relative=False
     Local Location: LocationLocal:north=None,east=None,down=None
     Attitude: Attitude:pitch=0.00589594058692,yaw=-0.0884591862559,roll=0.000426373298978
     Velocity: [-0.02, 0.02, 0.0]
     GPS: GPSInfo:fix=3,num_sat=10
     Groundspeed: 0.0
     Airspeed: 0.0
     Mount status: [None, None, None]
     Battery: Battery:voltage=12.587,current=0.0,level=99
     Rangefinder: Rangefinder: distance=None, voltage=None
     Rangefinder distance: None
     Rangefinder voltage: None
     Mode: STABILIZE
     Armed: False

     Home Location (before downloading waypoints): None
     Home Location (after downloading waypoints): LocationGlobal:lat=-35.3632621765,lon=149.165237427,alt=583.989990234,is_relative=False

    Set Vehicle.mode=GUIDED (currently: STABILIZE)
     Waiting for mode change ...

    Set Vehicle.armed=True (currently: False)
     Waiting for arming...
    >>> ARMING MOTORS
    >>> Initialising APM...

    Add mode attribute observer for Vehicle.mode
     Set mode=STABILIZE (currently: GUIDED)
     Wait 2s so callback invoked before observer removed
     CALLBACK: Mode changed to:  STABILIZE
     CALLBACK: Mode changed to:  STABILIZE

    Read vehicle param 'THR_MIN': 130.0
    Write vehicle param 'THR_MIN' : 10
    Read new value of param 'THR_MIN': 10.0

    Reset vehicle attributes/parameters and exit
    >>> DISARMING MOTORS

    Close vehicle object
    Completed




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

You may observe these issues:

* When the observer sets the mode callback, it waits two seconds after changing the mode before removing the observer
  (to ensure that the callback function is run before the observer is removed). In this time you may see the callback being 
  called twice even though the mode is only changed once. 
  See `#60 Attribute observer callbacks are called with heartbeat until disabled - after first called  <https://github.com/dronekit/dronekit-python/issues/60>`_ 
  for more information.



Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/vehicle_state/vehicle_state.py>`_):

.. literalinclude:: ../../examples/vehicle_state/vehicle_state.py
   :language: python

