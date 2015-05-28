.. _vehicle-information:

===========================
Vehicle State and Settings
===========================

The :py:class:`Vehicle <droneapi.lib.Vehicle>` class exposes *most* state information (position, speed, etc.) through python 
:ref:`attributes <vehicle_state_attributes>`, while vehicle :ref:`parameters <vehicle_state_parameters>` (settings) 
are accessed though named elements of :py:attr:`Vehicle.parameters <droneapi.lib.Vehicle.parameters>`. 

This topic explains how to get, set and observe vehicle state and parameter information (including getting the 
:ref:`Home location <vehicle_state_home_location>`). It also describes a few APIs that  
:ref:`should be used with caution <vehicle_state_disrecommended>`.

.. tip:: You can test most of the code in this topic by running the :ref:`Vehicle State <example-vehicle-state>` example.


.. _vehicle_state_attributes:

Attributes
==========

Vehicle state information is exposed through vehicle *attributes*. DroneKit-Python currently supports the following 
"standard" attributes: 
:py:attr:`Vehicle.location <droneapi.lib.Vehicle.location>`, 
:py:attr:`Vehicle.attitude <droneapi.lib.Vehicle.attitude>`,
:py:attr:`Vehicle.velocity <droneapi.lib.Vehicle.velocity>`,
:py:attr:`Vehicle.mode <droneapi.lib.Vehicle.mode>`,
:py:attr:`Vehicle.airspeed <droneapi.lib.Vehicle.airspeed>`,
:py:attr:`Vehicle.groundspeed <droneapi.lib.Vehicle.groundspeed>`,
:py:attr:`Vehicle.gps_0 <droneapi.lib.Vehicle.gps_0>`,
:py:attr:`Vehicle.armed <droneapi.lib.Vehicle.location>`,
:py:attr:`Vehicle.location <droneapi.lib.Vehicle.armed>`,
:py:attr:`Vehicle.mount_status <droneapi.lib.Vehicle.mount_status>`.

All of the attributes can be :ref:`read <vehicle_state_read_attributes>` and :ref:`observed <vehicle_state_observe_attributes>`, 
but only the :py:attr:`Vehicle.mode <droneapi.lib.Vehicle.mode>` and :py:attr:`Vehicle.armed <droneapi.lib.Vehicle.armed>` 
status can be :ref:`written <vehicle_state_set_attributes>`.


.. _vehicle_state_read_attributes:

Getting attributes
------------------

The code fragment below shows how to read and print all the attributes. The values are retrieved from the remote device 
(not cached).

.. code:: python
    
    # v is an instance of the Vehicle class
    print "Location: %s" % v.location
    print "Attitude: %s" % v.attitude
    print "Velocity: %s" % v.velocity
    print "GPS: %s" % v.gps_0
    print "groundspeed: %s" % v.groundspeed
    print "airspeed: %s" % v.airspeed
    print "mount_status: %s" % v.mount_status
    print "Mode: %s" % v.mode.name    # settable
    print "Armed: %s" % v.armed    # settable

If one of these attributes cannot be retrieved or is invalid then the returned object will contain
``None`` values for its members (for example, if there was no GPS lock then 
:py:attr:`Vehicle.gps_0 <droneapi.lib.Vehicle.gps_0>` would return a :py:class:`GPSInfo <droneapi.lib.GPSInfo>` 
with ``None`` values for ``eph``, ``satellites_visible`` etc.)
	
.. todo:: we need to be able to verify mount_status works/setup.



.. _vehicle_state_set_attributes:
	
Setting attributes
------------------

Only the :py:attr:`Vehicle.mode <droneapi.lib.Vehicle.mode>` and :py:attr:`Vehicle.armed <droneapi.lib.Vehicle.armed>` 
attributes can be written.

The attributes are set by assigning a value. Calling :py:func:`Vehicle.flush() <droneapi.lib.Vehicle.flush>`
then forces DroneKit to send outstanding messages.

.. code:: python

    #disarm the vehicle
    v.armed = False
    v.flush()  # Flush to ensure changes are sent to autopilot


.. warning::

    After ``flush()`` returns the message is guaranteed to have been sent to the autopilot, but it is **not guaranteed to succeed**. 
    For example, vehicle arming can fail if the vehicle doesn't pass pre-arming checks.
	
    While the autopilot does send information about the success (or failure) of the request, this is `not currently handled by DroneKit <https://github.com/diydrones/dronekit-python/issues/114>`_.


Code should not assume that an attempt to set an attribute will succeed. The example code snippet below polls the attribute values
to confirm they have changed before proceeding.

.. code:: python
    
    v.mode = VehicleMode("GUIDED")
    v.armed = True
    v.flush()  # Flush to ensure changes are sent to autopilot
    while not v.mode.name=='GUIDED' and not v.armed and not api.exit:
        print " Getting ready to take off ..."
        time.sleep(1)
    


.. _vehicle_state_observe_attributes:

Observing attribute changes
---------------------------

You can observe any of the attributes and will receive notification if their values change.  This allows you to 
monitor changes to velocity and other vehicle state without the need for polling.

.. warning::

    There is currently `a defect (#60) <https://github.com/diydrones/dronekit-python/issues/60>`_ that means that after an 
    observer is triggered, the callback function is run on every heartbeat (whether or not the observed attribute changes).

Observers are added using :py:func:`Vehicle.add_attribute_observer() <droneapi.lib.Vehicle.add_attribute_observer>`, 
specifying the name of the attribute to observe and a callback function. The same string is passed to the callback
when it is notified. Observers are removed using :py:func:`remove_attribute_observer() <droneapi.lib.Vehicle.remove_attribute_observer>`.

The code snippet below shows how to add (and remove) a callback function to observe :py:attr:`location <droneapi.lib.Vehicle.location>` attribute changes. The two second ``sleep()`` is required because otherwise the observer might be removed before the the callback is first run.

.. code:: python
     
    # Callback function. The parameter is the name of the observed attribute (a string)
    def location_callback(attribute):
        print " CALLBACK: Location changed to: ", v.location

    # Add a callback. The first parameter the name of the observed attribute (a string).
    v.add_attribute_observer('location', location_callback)	

    # Wait 2s so callback can be notified before the observer is removed
    time.sleep(2)

    # Remove observer - specifying the attribute and previously registered callback function
    v.remove_attribute_observer('location', location_callback)	





.. _vehicle_state_parameters:	

Parameters
==========

Vehicle parameters provide the information used to configure the autopilot for the vehicle-specific hardware/capabilities. 
These can be read and set using the :py:attr:`Vehicle.parameters <droneapi.lib.Vehicle.parameters>` 
attribute (a :py:class:`Parameters <droneapi.lib.Parameters>` object).

.. tip:: 

    `Copter Parameters <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/>`_, 
    `Plane Parameters <http://plane.ardupilot.com/wiki/arduplane-parameters/>`_, 
    and `Rover Parameters <http://rover.ardupilot.com/wiki/apmrover2-parameters/>`_ list all the supported parameters for each platform. 
    The lists are automatically generated from the latest ArduPilot source code, and may contain parameters 
    that are not yet in the stable released versions of the code.



Getting parameters
------------------

The parameters are read using the parameter name as a key. Reads will generally succeed unless you attempt to read an unsupported parameter
(which results in a Key error exception).

The code example below shows how to set Minimum Throttle (THR_MIN) setting. On Copter and Rover (not Plane), this is the minimum PWM setting for the 
throttle at which the motors will keep spinning.

.. code:: python

    # Print the value of the THR_MIN parameter.
    print "Param: %s" % vehicle.parameters['THR_MIN']

    

	
Setting parameters
------------------

Vehicle parameters are set as shown in the code fragment below, using the parameter name as a "key". As with attributes, the values are not guaranteed to have been sent to the vehicle until after 
:py:func:`flush() <Vehicle.flush>` returns.

.. code:: python

    # Change the parameter value (Copter, Rover)
    vehicle.parameters['THR_MIN']=100
    vehicle.flush()



Observing parameter changes
---------------------------

At time of writing :py:class:`Parameters <droneapi.lib.Parameters>` does `not support <https://github.com/diydrones/dronekit-python/issues/107>`_ observing parameter changes.
		
.. todo:: 

    Check to see if observers have been implemented and if so, update the information here, in about, and in Vehicle class:
    https://github.com/diydrones/dronekit-python/issues/107




.. _vehicle_state_home_location:

Home location
=============

The *Home location* is set when a vehicle is armed and first gets a good location fix from the GPS. The location is used 
as the target when the vehicle does a "return to launch". In Copter missions (and most Plane) missions, the altitude of 
waypoints is set relative to this position.

Unlike other vehicle state information, the home location is accessed as the 0 index value of 
:py:attr:`Vehicle.commands <droneapi.lib.Vehicle.commands>`:

.. code:: python
    
    cmds = v.commands
    cmds.download()
    cmds.wait_valid()
    print " Home WP: %s" % cmds[0]

The returned value is a :py:class:`Command <droneapi.lib.Command>` object.



.. _vehicle_state_disrecommended:

Discommended APIs
=================

This section describes methods that we recommend you do not use! In general they are provided to handle the (hopefully rare)
cases where the "proper" API is missing some needed functionality.

If you have to use these methods please `provide feedback explaining why <https://github.com/diydrones/dronekit-python/issues>`_.


.. _vehicle_state_set_mavlink_callback:

MAVLink Message Observer
------------------------

The :py:func:`Vehicle.set_mavlink_callback() <droneapi.lib.Vehicle.set_mavlink_callback>` method provides asynchronous 
notification when any *MAVLink* packet is received from this vehicle.

.. tip::

    Use :ref:`attribute observers <vehicle_state_observe_attributes>` instead of this method where possible. 


The code snippet below shows how to set a “demo” callback function as the callback handler:

.. code:: python

    # Demo callback handler for raw MAVLink messages
    def mavrx_debug_handler(message):
        print "Received", message

    # Set MAVLink callback handler (after getting Vehicle instance)                     
    v.set_mavlink_callback(mavrx_debug_handler)


.. warning:: 

    At time of writing there is no way to `disable this callback <https://github.com/diydrones/dronekit-python/issues/115>`_.


.. _vehicle_state_channel_override:

Channel Overrides
-----------------

.. warning::

    Channel Overrides may be useful for simulating user input and when implementing certain types of joystick control. 
    They should not be used for direct control of the vehicle unless there is no other choice!

    Instead use the appropriate MAVLink commands like DO_SET_SERVO/DO_SET_RELAY, or more generally set the desired position or direction/speed.

The :py:attr:`channel_override <droneapi.lib.Vehicle.channel_override>` attribute takes a dictionary argument defining the RC *output* channels to be overridden (specified by channel number), and their new values.  Channels that are not specified in the dictionary are not overridden. All multi-channel updates are atomic. To cancel an override call ``channel_override`` again, setting zero for the overridden channels.

The values of the first four channels map to the main flight controls: 1=Roll, 2=Pitch, 3=Throttle, 4=Yaw (the mapping is defined in ``RCMAP_`` parameters in 
`Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/#rcmap__parameters>`_, 
`Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/#rcmap__parameters>`_ , 
`Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/#rcmap__parameters>`_).
	
The remaining channel values are configurable, and their purpose can be determined using the 
`RCn_FUNCTION parameters <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/>`_. 
In general a value of 0 set for a specific ``RCn_FUNCTION`` indicates that the channel can be 
`mission controlled <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/#disabled>`_ (i.e. it will not directly be 
controlled by normal autopilot code).

An example of setting and clearing overrides is given below:

.. code:: python
    
    # Override the channel for roll and yaw
    v.channel_override = { "1" : 900, "4" : 1000 }
    v.flush()
	
    #print current override values
    print "Current overrides are:", v.channel_override

    # Print channel values (values if overrides removed)
    print "Channel default values:", v.channel_readback  
    
    # Cancel override by setting channels to 0
    v.channel_override = { "1" : 0, "4" : 0 }
    v.flush()	



	
.. _api-information-known-issues:

Known issues
============

Below are a number of bugs and known issues related to vehicle state and settings:

* `#12 Timeout error when setting a parameter <https://github.com/diydrones/dronekit-python/issues/12>`_
* `#60 Attribute observer callbacks are called with heartbeat until disabled - after first called  <https://github.com/diydrones/dronekit-python/issues/60>`_
* `#107 Add implementation for observer methods in Parameter class <https://github.com/diydrones/dronekit-python/issues/107>`_ 
* `#114 DroneKit has no method for detecting command failure <https://github.com/diydrones/dronekit-python/issues/114>`_
* `#115 No way to disable the callback set_mavlink_callback <https://github.com/diydrones/dronekit-python/issues/115>`_


Other API issues and improvement suggestions can viewed on `github here <https://github.com/diydrones/dronekit-python/issues>`_. 