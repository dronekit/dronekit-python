.. _vehicle-information:

===========================
Vehicle State and Settings
===========================

The :py:class:`Vehicle <dronekit.lib.Vehicle>` class exposes *most* state information (position, speed, etc.) through python 
:ref:`attributes <vehicle_state_attributes>`, while vehicle :ref:`parameters <vehicle_state_parameters>` (settings) 
are accessed though named elements of :py:attr:`Vehicle.parameters <dronekit.lib.Vehicle.parameters>`. 

This topic explains how to get, set and observe vehicle state and parameter information (including getting the 
:ref:`Home location <vehicle_state_home_location>`).

.. tip:: You can test most of the code in this topic by running the :ref:`Vehicle State <example-vehicle-state>` example.


.. _vehicle_state_attributes:

Attributes
==========

Vehicle state information is exposed through vehicle *attributes*. DroneKit-Python currently supports the following 
"standard" attributes: 
:py:attr:`Vehicle.location <dronekit.lib.Vehicle.location>`, 
:py:attr:`Vehicle.attitude <dronekit.lib.Vehicle.attitude>`,
:py:attr:`Vehicle.velocity <dronekit.lib.Vehicle.velocity>`,
:py:attr:`Vehicle.airspeed <dronekit.lib.Vehicle.airspeed>`,
:py:attr:`Vehicle.groundspeed <dronekit.lib.Vehicle.groundspeed>`,
:py:attr:`Vehicle.gps_0 <dronekit.lib.Vehicle.gps_0>`,
:py:attr:`Vehicle.mount_status <dronekit.lib.Vehicle.mount_status>`,
:py:attr:`Vehicle.battery <dronekit.lib.Vehicle.battery>`,
:py:attr:`Vehicle.rangefinder <dronekit.lib.Vehicle.rangefinder>`,
:py:attr:`Vehicle.home_location <dronekit.lib.Vehicle.home_location>`
:py:attr:`Vehicle.armed <dronekit.lib.Vehicle.armed>`,
:py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>`.

All of the attributes can be :ref:`read <vehicle_state_read_attributes>` and :ref:`observed <vehicle_state_observe_attributes>`, 
but only the :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>` and :py:attr:`Vehicle.armed <dronekit.lib.Vehicle.armed>` 
status can be :ref:`written <vehicle_state_set_attributes>`.



.. _vehicle_state_read_attributes:

Getting attributes
------------------

The code fragment below shows how to read and print almost the attributes. The values are retrieved from the remote device 
(not cached).

.. code:: python
    
    # vehicle is an instance of the Vehicle class
    print "Global Location: %s" % vehicle.location.global_frame
    print "Local Location: %s" % vehicle.location.local_frame    #NED
    print "Attitude: %s" % vehicle.attitude
    print "Velocity: %s" % vehicle.velocity
    print "GPS: %s" % vehicle.gps_0
    print "Groundspeed: %s" % vehicle.groundspeed
    print "Airspeed: %s" % vehicle.airspeed
    print "Mount status: %s" % vehicle.mount_status
    print "Battery: %s" % vehicle.battery
    print "Rangefinder: %s" % vehicle.rangefinder
    print "Rangefinder distance: %s" % vehicle.rangefinder.distance
    print "Rangefinder voltage: %s" % vehicle.rangefinder.voltage
    print "Mode: %s" % vehicle.mode.name    # settable
    print "Armed: %s" % vehicle.armed    # settable


If an attribute cannot be retrieved then the returned object will contain
``None`` values for its members (for example, if there was no GPS lock then 
:py:attr:`Vehicle.gps_0 <dronekit.lib.Vehicle.gps_0>` would return a :py:class:`GPSInfo <dronekit.lib.GPSInfo>` 
with ``None`` values for ``eph``, ``satellites_visible`` etc.) 
Attributes will also return  ``None`` if the associated hardware is not present on the connected device. 

The behaviour of :py:attr:`Vehicle.home_location <dronekit.lib.Vehicle.home_location>` is different, 
:ref:`as discussed below <vehicle_state_home_location>`.

.. tip::

    If you're using a :ref:`simulated vehicle <sitl_setup>` you can add support for optional hardware including
    `rangefinders <http://dev.ardupilot.com/using-sitl-for-ardupilot-testing/#adding_a_virtual_rangefinder>`_
    and `optical flow sensors <http://dev.ardupilot.com/using-sitl-for-ardupilot-testing/#adding_a_virtual_optical_flow_sensor>`_.


    
.. todo:: we need to be able to verify mount_status works/setup.



.. _vehicle_state_set_attributes:

Setting attributes
------------------

Only the :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>` and :py:attr:`Vehicle.armed <dronekit.lib.Vehicle.armed>` 
attributes can be written.

The attributes are set by assigning a value:

.. code:: python

    #disarm the vehicle
    vehicle.armed = False


.. warning::

    Changing a value is **not guaranteed to succeed**. 
    For example, vehicle arming can fail if the vehicle doesn't pass pre-arming checks.

    While the autopilot does send information about the success (or failure) of the request, 
    this is `not currently handled by DroneKit <https://github.com/dronekit/dronekit-python/issues/114>`_.


Code should not assume that an attempt to set an attribute will succeed. The example code snippet below polls the attribute values
to confirm they have changed before proceeding.

.. code:: python
    
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.mode.name=='GUIDED' and not vehicle.armed and not api.exit:
        print " Getting ready to take off ..."
        time.sleep(1)
    


.. _vehicle_state_observe_attributes:

Observing attribute changes
---------------------------

You can observe any of the attributes (except the ``home_location``) and will receive notification every time a value is received from the connected vehicle.  
This allows you to monitor changes to velocity and other vehicle state without the need for polling.

Observers are added using :py:func:`Vehicle.add_attribute_observer() <dronekit.lib.Vehicle.add_attribute_observer>`, 
specifying the name of the attribute to observe and a callback function. The same string is passed to the callback
when it is notified. Observers are removed using :py:func:`remove_attribute_observer() <dronekit.lib.Vehicle.remove_attribute_observer>`.

The code snippet below shows how to add (and remove) a callback function to observe :py:attr:`location <dronekit.lib.Vehicle.location>` 
attribute changes. The two second ``sleep()`` is required because otherwise the observer might be removed before the the callback is first run.

.. code:: python
     
    # Callback function. The parameter is the name of the observed attribute (a string)
    def location_callback(attribute):
        print " CALLBACK: Global Location changed to: ", vehicle.location.global_frame
        print " CALLBACK: Location changed to: ", vehicle.location.local_frame
        
    # Add a callback. The first parameter the name of the observed attribute (a string).
    vehicle.add_attribute_observer('location', location_callback)

    # Wait 2s so callback can be notified before the observer is removed
    time.sleep(2)

    # Remove observer - specifying the attribute and previously registered callback function
    vehicle.remove_attribute_observer('location', location_callback)


The callback is triggered every time a message is received from the vehicle (whether or not the observed attribute changes). 
Callback code may therefore choose to cache the result and only report changes. 
For example, the following code can be used in the callback to only print output when the value of 
:py:attr:`Vehicle.rangefinder <dronekit.lib.Vehicle.rangefinder>` changes.

.. code:: python

    last_rangefinder_distance=0

    def rangefinder_callback(rangefinder):
        global last_rangefinder_distance
        if last_rangefinder_distance == round(vehicle.rangefinder.distance, 1):
            return
        last_rangefinder_distance = round(vehicle.rangefinder.distance, 1)
        print " Rangefinder (metres): %s" % last_rangefinder_distance


    vehicle.add_attribute_observer('rangefinder', rangefinder_callback)



.. _vehicle_state_home_location:

Home location
-------------

The *Home location* is set when a vehicle is armed and first gets a good location fix from the GPS. The location is used 
as the target when the vehicle does a "return to launch". In Copter missions (and often Plane) missions, the altitude of 
waypoints is set relative to this position.

The behaviour of :py:attr:`Vehicle.home_location <dronekit.lib.Vehicle.home_location>` is slightly different than other attributes:

* In order to get the current value you must first download :py:attr:`Vehicle.commands <dronekit.lib.Vehicle.commands>`, as shown:

  .. code:: python
    
      cmds = vehicle.commands
      cmds.download()
      cmds.wait_ready()
      print " Home Location: %s" % vehicle.home_location

  The returned value is a :py:class:`LocationGlobal <dronekit.lib.LocationGlobal>` object 
  (or ``None`` before you download the commands).
* The attribute is not observable.
* While you cannot directly set the attribute it can be :ref:`set using a message <guided_mode_copter_set_home>`.    
    
    

.. _vehicle_state_parameters:

Parameters
==========

Vehicle parameters provide the information used to configure the autopilot for the vehicle-specific hardware/capabilities. 
These can be read and set using the :py:attr:`Vehicle.parameters <dronekit.lib.Vehicle.parameters>` 
attribute (a :py:class:`Parameters <dronekit.lib.Parameters>` object).

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

Vehicle parameters are set as shown in the code fragment below, using the parameter name as a "key":

.. code:: python

    # Change the parameter value (Copter, Rover)
    vehicle.parameters['THR_MIN']=100


Observing parameter changes
---------------------------

At time of writing :py:class:`Parameters <dronekit.lib.Parameters>` does `not support <https://github.com/dronekit/dronekit-python/issues/107>`_ observing parameter changes.

.. todo:: 

    Check to see if observers have been implemented and if so, update the information here, in about, and in Vehicle class:
    https://github.com/dronekit/dronekit-python/issues/107




.. _api-information-known-issues:

Known issues
============

Below are a number of bugs and known issues related to vehicle state and settings:

* `#60 Attribute observer callbacks are called with heartbeat until disabled - after first called  <https://github.com/dronekit/dronekit-python/issues/60>`_
* `#107 Add implementation for observer methods in Parameter class <https://github.com/dronekit/dronekit-python/issues/107>`_ 
* `#114 DroneKit has no method for detecting command failure <https://github.com/dronekit/dronekit-python/issues/114>`_
* `#392 vehicle.home_location should be settable <https://github.com/dronekit/dronekit-python/issues/392>`_


Other API issues and improvement suggestions can viewed on `github here <https://github.com/dronekit/dronekit-python/issues>`_. 