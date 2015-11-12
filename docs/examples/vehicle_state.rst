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
(otherwise the :py:attr:`Vehicle.rangefinder <dronekit.lib.Vehicle.rangefinder>` attribute may return 
values of ``None`` for the distance and voltage). 

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

    Connecting to vehicle on: 170.0.0.1:14550
    >>> APM:Copter V3.3 (d6053245)
    >>> Frame: QUAD
    >>> Calibrating barometer
    >>> Initialising APM...
    >>> barometer calibration complete
    >>> GROUND START

    Get all vehicle attribute values:
     Global Location: LocationGlobal:lat=-35.363261,lon=149.1652299,alt=0.0,is_relative=False
     Local Location: LocationLocal:north=None,east=None,down=None
     Attitude: Attitude:pitch=0.00294387154281,yaw=-0.11805768311,roll=0.00139428151306
     Velocity: [-0.03, 0.02, 0.0]
     GPS: GPSInfo:fix=3,num_sat=10
     Groundspeed: 0.0
     Airspeed: 0.0
     Mount status: [None, None, None]
     Battery: Battery:voltage=12.587,current=0.0,level=100
     EKF OK?: False
     Rangefinder: Rangefinder: distance=None, voltage=None
     Rangefinder distance: None
     Rangefinder voltage: None
     Heading: 353
     Is Armable?: False
     System status: STANDBY
     Mode: STABILIZE
     Armed: False
     Waiting for home location ...
     ...
     Waiting for home location ...
     Waiting for home location ...

     Home location: LocationGlobal:lat=-35.3632621765,lon=149.165237427,alt=583.989990234,is_relative=False

    Set new home location
     New Home Location (from attribute - altitude should be 222): LocationGlobal:lat=-35.363261,lon=149.1652299,alt=222,is_relative=False
     New Home Location (from vehicle - altitude should be 222): LocationGlobal:lat=-35.3632621765,lon=149.165237427,alt=222.0,is_relative=False

    Set Vehicle.mode=GUIDED (currently: STABILIZE)
     Waiting for mode change ...

    Set Vehicle.armed=True (currently: False)
     Waiting for arming...
     Waiting for arming...
     Waiting for arming...
    >>> ARMING MOTORS
    >>> GROUND START
     Waiting for arming...
     Waiting for arming...
    >>> Initialising APM...
     Vehicle is armed: True

    Add `attitude` attribute callback/observer on `vehicle`
     Wait 2s so callback invoked before observer removed
     CALLBACK: Attitude changed to Attitude:pitch=-0.000483880605316,yaw=-0.0960851684213,roll=-0.00799709651619
     CALLBACK: Attitude changed to Attitude:pitch=0.000153727291035,yaw=-0.0962921902537,roll=-0.00707155792043
     ...
     CALLBACK: Attitude changed to Attitude:pitch=0.00485319690779,yaw=-0.100129388273,roll=0.00181497994345
      Remove Vehicle.attitude observer

    Add `mode` attribute callback/observer using decorator
     Set mode=STABILIZE (currently: GUIDED) and wait for callback
     Wait 2s so callback invoked before moving to next example
     CALLBACK: Mode changed to VehicleMode:STABILIZE

     Attempt to remove observer added with `on_attribute` decorator (should fail)
     Exception: Cannot remove observer added using decorator

    Add attribute callback detecting ANY attribute change
     Wait 1s so callback invoked before observer removed
     CALLBACK: (attitude): Attitude:pitch=0.00716688157991,yaw=-0.0950401723385,roll=0.00759896961972
     CALLBACK: (heading): 354
     CALLBACK: (location): LocationGlobal:lat=-35.3632621,lon=149.1652291,alt=362.0,is_relative=False
     CALLBACK: (airspeed): 0.0
     CALLBACK: (groundspeed): 0.0
     CALLBACK: (ekf_ok): True
     CALLBACK: (battery): Battery:voltage=12.538,current=3.48,level=99
     CALLBACK: (gps_0): GPSInfo:fix=3,num_sat=10
     CALLBACK: (location): LocationGlobal:lat=-35.3632622,lon=149.1652295,alt=362.0,is_relative=False
     CALLBACK: (velocity): [-0.14, 0.1, 0.0]
     CALLBACK: (local_position): LocationLocal:north=-0.136136248708,east=-0.0430941730738,down=-0.00938374921679
     CALLBACK: (channels): {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800}
     ...
     CALLBACK: (ekf_ok): True
     Remove Vehicle attribute observer

    Read and write parameters
     Read vehicle param 'THR_MIN': 130.0
     Write vehicle param 'THR_MIN' : 10
     Read new value of param 'THR_MIN': 10.0

    Print all parameters (iterate `vehicle.parameters`):
     Key:RC7_REV Value:1.0
     Key:GPS_INJECT_TO Value:127.0
     Key:FLTMODE1 Value:7.0
     ...
     Key:SR2_POSITION Value:0.0
     Key:SIM_FLOW_DELAY Value:0.0
     Key:BATT_CURR_PIN Value:12.0

    Create parameter observer using decorator
    Write vehicle param 'THR_MIN' : 20 (and wait for callback)
     PARAMETER CALLBACK: THR_MIN changed to: 20.0

    Create (removable) observer for any parameter using wildcard string
     Change THR_MID and THR_MIN parameters (and wait for callback)
     ANY PARAMETER CALLBACK: THR_MID changed to: 400.0
     PARAMETER CALLBACK: THR_MIN changed to: 30.0
     ANY PARAMETER CALLBACK: THR_MIN changed to: 30.0

    Reset vehicle attributes/parameters and exit
    >>> DISARMING MOTORS
     PARAMETER CALLBACK: THR_MIN changed to: 130.0
     ANY PARAMETER CALLBACK: THR_MIN changed to: 130.0
     ANY PARAMETER CALLBACK: THR_MID changed to: 500.0

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

This example has no known issues.



Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/vehicle_state/vehicle_state.py>`_):

.. literalinclude:: ../../examples/vehicle_state/vehicle_state.py
   :language: python

