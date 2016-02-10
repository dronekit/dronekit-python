.. _example_channel_overrides:
.. _vehicle_state_channel_override:

=======================================
Example: Channels and Channel Overrides
=======================================

This example shows how to get channel information and to get/set channel-override information.

.. warning::

    Channel overrides (a.k.a. "RC overrides") are highly dis-commended (they are primarily intended 
    for simulating user input and when implementing certain types of joystick control).

    Instead use the appropriate MAVLink commands like DO_SET_SERVO/DO_SET_RELAY, or more generally set 
    the desired position or direction/speed.

    If you have no choice but to use a channel-override please explain why in a 
    `Github issue <https://github.com/dronekit/dronekit-python/issues>`_ and we will attempt to find a 
    better alternative.
    

Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`installing_dronekit`). 

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/channel_overrides/


#. You can run the example against a simulator (DroneKit-SITL) by specifying the Python script without any arguments.
   The example will download SITL binaries (if needed), start the simulator, and then connect to it:

   .. code-block:: bash

       python channel_overrides.py

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
       Channel values from RC Tx: {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800}
       Read channels individually:
        Ch1: 1500
        Ch2: 1500
        Ch3: 1000
        Ch4: 1500
        Ch5: 1800
        Ch6: 1000
        Ch7: 1000
        Ch8: 1800
       Number of channels: 8
        Channel overrides: {}
       Set Ch2 override to 200 (indexing syntax)
        Channel overrides: {'2': 200}
        Ch2 override: 200
       Set Ch3 override to 300 (dictionary syntax)
        Channel overrides: {'3': 300}
       Set Ch1-Ch8 overrides to 110-810 respectively
        Channel overrides: {'1': 110, '3': 310, '2': 210, '5': 510, '4': 4100, '7': 710, '6': 610, '8': 810}
        Cancel Ch2 override (indexing syntax)
        Channel overrides: {'1': 110, '3': 310, '5': 510, '4': 4100, '7': 710, '6': 610, '8': 810}
       Clear Ch3 override (del syntax)
        Channel overrides: {'1': 110, '5': 510, '4': 4100, '7': 710, '6': 610, '8': 810}
       Clear Ch5, Ch6 override and set channel 3 to 500 (dictionary syntax)
        Channel overrides: {'3': 500}
       Clear all overrides
        Channel overrides: {}
        Close vehicle object
       Completed

#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python channel_overrides.py --connect 127.0.0.1:14550

       
How does it work?
=================

The RC transmitter channels are connected to the autopilot and control the vehicle. 

The values of the first four channels map to the main flight controls: 1=Roll, 2=Pitch, 3=Throttle, 4=Yaw (the mapping is defined in ``RCMAP_`` parameters in 
`Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/#rcmap__parameters>`_, 
`Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/#rcmap__parameters>`_ , 
`Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/#rcmap__parameters>`_).

The remaining channel values are configurable, and their purpose can be determined using the 
`RCn_FUNCTION parameters <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/>`_. 
In general a value of 0 set for a specific ``RCn_FUNCTION`` indicates that the channel can be 
`mission controlled <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/#disabled>`_ (i.e. it will not directly be 
controlled by normal autopilot code).

You can read the values of the channels using the :py:attr:`Vehicle.channels <dronekit.Vehicle.channels>` attribute. The values are regularly updated,
from the UAV, based on the RC inputs from the transmitter. These can be read either as a set or individually:

.. code:: python

    # Get all channel values from RC transmitter
    print "Channel values from RC Tx:", vehicle.channels

    # Access channels individually
    print "Read channels individually:"
    print " Ch1: %s" % vehicle.channels['1']
    print " Ch2: %s" % vehicle.channels['2']

You can override the values sent to the vehicle by the autopilot using :py:attr:`Vehicle.channels.overrides <dronekit.Channels.overrides>`.  
The overrides can be written individually using an indexing syntax or as a set using a dictionary syntax.

.. code:: python

    # Set Ch2 override to 200 using indexing syntax
    vehicle.channels.overrides['2'] = 200
    # Set Ch3, Ch4 override to 300,400 using dictionary syntax"
    vehicle.channels.overrides = {'3':300, '4':400}
    
To clear all overrides, set the attribute to an empty dictionary.
To clear an individual override you can set its value to ``None`` (or call ``del`` on it):

.. code:: python

    # Clear override by setting channels to None
    # Clear using index syntax
    vehicle.channels.overrides['2'] = None
    
    # Clear using 'del' syntax
    del vehicle.channels.overrides['3']

    # Clear using dictionary syntax (and set override at same time!)
    vehicle.channels.overrides = {'5':None, '6':None,'3':500}
    
    # Clear all overrides by setting an empty dictionary
    vehicle.channels.overrides = {}   

Read the channel overrides either as a dictionary or by index. 

.. code:: python

    # Get all channel overrides
    print " Channel overrides: %s" % vehicle.channels.overrides
    # Print just one channel override
    print " Ch2 override: %s" % vehicle.channels.overrides['2']

.. note::

    You'll get a ``KeyError`` exception if you read a channel override that has 
    not been set. 


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/channel_overrides/channel_overrides.py>`_):

.. literalinclude:: ../../examples/channel_overrides/channel_overrides.py
   :language: python

