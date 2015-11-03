.. _example_channel_overrides:
.. _vehicle_state_channel_override:

==========================
Example: Channel Overrides
==========================

This example shows how to get channel information and to get/set channel-override information.

.. warning::

    Channel overrides (a.k.a "RC overrides") are highly discommended (they are primarily implemented 
    for simulating user input and when implementing certain types of joystick control).

    Instead use the appropriate MAVLink commands like DO_SET_SERVO/DO_SET_RELAY, or more generally set 
    the desired position or direction/speed.

    If you have no choice but to use a channel-override please explain why in a 
    `github issue <https://github.com/dronekit/dronekit-python/issues>`_ and we will attempt to find a 
    better alternative.
    

Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`). 

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/channel_overrides/


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python channel_overrides.py --connect 127.0.0.1:14550

   .. note::
   
       The ``--connect`` parameter above connects to SITL on udp port 127.0.0.1:14550.
       This is the default value for the parameter, and may be omitted. 
          


On the command prompt you should see (something like):

.. code:: bash

    Overriding RC channels for roll and yaw
     Current overrides are: {'1': 900, '4': 1000}
     Channel default values: {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800}
     Cancelling override



How does it work?
=================

Get the default values of the channels using the :py:attr:`channel_readback <dronekit.lib.Vehicle.channel_readback>` attribute. 

You can over-ride these values using the :py:attr:`channel_override <dronekit.lib.Vehicle.channel_override>` attribute. This takes a dictionary argument defining the RC *output* channels to be overridden (specified by channel number), and their new values.  Channels that are not specified in the dictionary are not overridden. All multi-channel updates are atomic. To cancel an override call ``channel_override`` again, setting zero for the overridden channels.

The values of the first four channels map to the main flight controls: 1=Roll, 2=Pitch, 3=Throttle, 4=Yaw (the mapping is defined in ``RCMAP_`` parameters in 
`Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/#rcmap__parameters>`_, 
`Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/#rcmap__parameters>`_ , 
`Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/#rcmap__parameters>`_).

The remaining channel values are configurable, and their purpose can be determined using the 
`RCn_FUNCTION parameters <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/>`_. 
In general a value of 0 set for a specific ``RCn_FUNCTION`` indicates that the channel can be 
`mission controlled <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/#disabled>`_ (i.e. it will not directly be 
controlled by normal autopilot code).




Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/channel_overrides/channel_overrides.py>`_):

.. literalinclude:: ../../examples/channel_overrides/channel_overrides.py
   :language: python

