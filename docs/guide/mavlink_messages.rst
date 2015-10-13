.. _mavlink_messages:

================
MAVLink Messages
================

Some useful MAVLink messages sent by the autopilot are not (yet) directly available to DroneKit-Python scripts
through the :ref:`observable attributes <vehicle_state_observe_attributes>` in :py:class:`Vehicle <dronekit.lib.Vehicle>`.

This topic shows how you can intercept MAVLink messages using 
:py:func:`Vehicle.set_mavlink_callback() <dronekit.lib.Vehicle.set_mavlink_callback>`.

.. tip::

    :ref:`example_create_attribute` shows how you can extend this approach to create a new :py:class:`Vehicle <dronekit.lib.Vehicle>`
    attribute in your client code.

    

.. _mavlink_messages_set_mavlink_callback:

Creating the message observer
=============================

The :py:func:`Vehicle.set_mavlink_callback() <dronekit.lib.Vehicle.set_mavlink_callback>` method provides asynchronous 
notification when any *MAVLink* packet is received from the connected vehicle.

The code snippet below shows how to set a “demo” callback function as the callback handler:

.. code:: python

    # Demo callback handler for raw MAVLink messages
    def mavrx_debug_handler(message):
        print type(message)
        print message
        

    # Set MAVLink callback handler (after getting Vehicle instance)                     
    vehicle.set_mavlink_callback(mavrx_debug_handler)

.. note::

    DroneKit-Python only supports a single MAVLink message observer at a time. This can be removed or replaced 
    with a different observer.    
    
The messages are `classes <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_ from the `pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_ library. 
The output of the code above looks something like:

.. code:: bash

    <class 'pymavlink.dialects.v10.ardupilotmega.MAVLink_rangefinder_message'>
    RANGEFINDER {distance : 0.0899999961257, voltage : 0.00900000054389}
    <class 'pymavlink.dialects.v10.ardupilotmega.MAVLink_terrain_report_message'>
    TERRAIN_REPORT {lat : -353632610, lon : 1491652299, spacing : 100, terrain_height : 583.88470459, current_height : 0.0, pending : 0, loaded : 504}
    <class 'pymavlink.dialects.v10.ardupilotmega.MAVLink_ekf_status_report_message'>
    EKF_STATUS_REPORT {flags : 933, velocity_variance : 0.0, pos_horiz_variance : 0.0, pos_vert_variance : 0.000532002304681, compass_variance : 0.00632426189259, terrain_alt_variance : 0.0}
    <class 'pymavlink.dialects.v10.ardupilotmega.MAVLink_vibration_message'>
    VIBRATION {time_usec : 88430000, vibration_x : 0.0, vibration_y : 0.0, vibration_z : 0.0, clipping_0 : 0, clipping_1 : 0, clipping_2 : 0}
    ...
    
You can access the message fields directly. For example, to access the ``RANGEFINDER`` message your handler might look like this:

.. code:: python

    # Handler for message: RANGEFINDER {distance : 0.0899999961257, voltage : 0.00900000054389}
    def mavrx_debug_handler(message):
        messagetype=str(message).split('{')[0].strip()
        if messagetype=='RANGEFINDER':
            print 'distance: %s' % message.distance
            print 'voltage: %s' % message.voltage



    


Clearing the observer
=====================

The observer is unset by calling :py:func:`Vehicle.unset_mavlink_callback <dronekit.lib.Vehicle.unset_mavlink_callback>`.

The observer will also be removed when the thread exits.


    
    