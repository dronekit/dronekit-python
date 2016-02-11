.. _best_practices:

==============
Best Practices
==============

This guide provides a broad overview of how to use the API, its main programming idioms 
and best practices. More detail information is linked from each section.


General considerations
======================

DroneKit-Python communicates with vehicle autopilots using the MAVLink protocol, 
which defines how commands, telemetry and vehicle settings/parameters
are sent between vehicles, companion computers, ground stations and other systems on
a MAVLink network. 

Some general considerations from using this protocol are:

* Messages and message acknowledgments are not guaranteed to arrive (the protocol is not "lossless").
* Commands may be silently ignored by the Autopilot if it is not in a state where it can
  safely act on them. 
* Command acknowledgment and completion messages are not sent in most cases
  (and if sent, may not arrive).
* Commands may be interrupted before completion.
* Autopilots may choose to interpret the protocol in slightly different ways.
* Commands can arrive at the autopilot from multiple sources.

Developers should code defensively. Where possible:

* Check that a vehicle is in a state to obey a command (for example, 
  poll on :py:func:`Vehicle.is_armable <dronekit.Vehicle.is_armable>`
  before trying to arm the vehicle).
* Don't assume that a command has succeeded until the changed behaviour is observed.
  In particular we recommend a launch sequence where you check that the mode and arming
  have succeeded before attempting to take off.
* Monitor for state changes and react accordingly. 
  For example, if the user changes the mode from ``GUIDED`` your script should 
  stop sending commands.
* Verify that your script can run inside the normal latency limits for message passing
  from the vehicle and tune any monitoring appropriately.


Connecting
==========

In most cases you'll use the normal way to :ref:`connect to a vehicle <connecting_vehicle>`, 
setting ``wait_ready=True`` to ensure that the vehicle is already populated with attributes
when the :py:func:`connect() <dronekit.connect>` returns: 

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle (in this case a UDP endpoint)
    vehicle = connect('REPLACE_connection_string_for_your_vehicle', wait_ready=True)
    
The ``connect()`` call will sometimes fail with an exception. 
Additional information about an exception can be obtained by
running the connect within a ``try-catch`` block as shown:

.. code-block:: python
    
    import dronekit
    import socket
    import exceptions


    try:
        dronekit.connect('REPLACE_connection_string_for_your_vehicle', heartbeat_timeout=15)
        
    # Bad TCP connection
    except socket.error:
        print 'No server exists!'
 
    # Bad TTY connection
    except exceptions.OSError as e:
        print 'No serial exists!'

    # API Error
    except dronekit.APIException:
        print 'Timeout!'
        
    # Other error
    except:
        print 'Some other error!'

.. tip::

    The default ``heartbeat_timeout`` on connection is 30 sections. Usually a connection will 
    succeed quite quickly, so you may wish to reduce this in the ``connect()`` method as shown in the 
    code snippet above.
    
If a connection succeeds from a ground station, but not from DroneKit-Python it may be that your baud
rate is incorrect for your hardware. This rate can also be set in the ``connect()`` method.


Launch sequence
===============

Generally you should use the standard launch sequence described in :doc:`../guide/taking_off`:

* Poll on :py:func:`Vehicle.is_armable <dronekit.Vehicle.is_armable>` 
  until the vehicle is ready to arm.
* Set the :py:attr:`Vehicle.mode <dronekit.Vehicle.mode>` to ``GUIDED``
* Set :py:attr:`Vehicle.armed <dronekit.Vehicle.armed>` to ``True`` and 
  poll on the same attribute until the vehicle is armed.
* Call :py:func:`Vehicle.simple_takeoff <dronekit.Vehicle.simple_takeoff>` 
  with a target altitude.
* Poll on the altitude and allow the code to continue only when it is reached.

The approach ensures that commands are only sent to the vehicle when it is able 
to act on them (e.g. we know :py:func:`Vehicle.is_armable <dronekit.Vehicle.is_armable>` 
is ``True`` before trying to arm, we know
:py:attr:`Vehicle.armed <dronekit.Vehicle.armed>` is ``True`` before we take off).
It also makes debugging takeoff problems a lot easier.


Movement commands
=================

DroneKit-Python provides :py:func:`Vehicle.simple_goto <dronekit.Vehicle.simple_goto>` for moving to a specific position (at a defined speed). It is also possible to control movement by sending commands to specify the vehicle's :ref:`velocity components <guided_mode_copter_velocity_control>`. 

.. note:: 

    As with :py:func:`Vehicle.simple_takeoff <dronekit.Vehicle.simple_takeoff>`, movement 
    commands are asynchronous, and will be interrupted if another command arrives 
    before the vehicle reaches its target. Calling code should block and wait (or 
    check that the operation is complete) before preceding to the next command.

For more information see: :ref:`guided_mode_copter`.


Vehicle information
===================

Vehicle state information is exposed through vehicle *attributes* which can be read and observed (and in some cases written)
and vehicle settings which can be read, written, iterated and observed using *parameters* (a special attribute). All the attributes are documented in :doc:`../guide/vehicle_state_and_parameters`.

Attributes are populated by MAVLink messages from the vehicle. 
Information read from an attribute may not precisely reflect the actual value on the vehicle. Commands sent
to the vehicle may not arrive, or may be ignored by the autopilot.

If low-latency is critical, we recommend you verify that the update rate is achievable and 
perhaps modify script behaviour if :py:attr:`Vehicle.last_heartbeat <dronekit.Vehicle.last_heartbeat>` falls outside
a useful range.

When setting attributes, poll their values to confirm that they have changed. This applies, in particular,
to :py:attr:`Vehicle.armed <dronekit.Vehicle.armed>` and :py:attr:`Vehicle.mode <dronekit.Vehicle.mode>`.  



Missions and waypoints
======================

DroneKit-Python can also :ref:`create and modify autonomous missions <auto_mode_vehicle_control>`.

While it is possible to construct DroneKit-Python apps by dynamically constructing missions "on the fly", we recommend you use guided mode for Copter apps. This generally results in a better experience.

.. tip::

    If a mission command is not available in guided mode, 
    it can be useful to switch to a mission and call it, then change 
    back to normal guided mode operation.
    

Monitor and react to state changes
==================================

Almost all attributes can be observed - see :ref:`vehicle_state_observe_attributes` for more information.

Exactly what state information you observe, and how you react to it, depends on your particular script:

* Most standalone apps should monitor the :py:func:`Vehicle.mode <dronekit.Vehicle.mode>` and 
  stop sending commands if the mode changes unexpectedly (this usually indicates 
  that the user has taken control of the vehicle).
* Apps might monitor :py:func:`Vehicle.last_heartbeat <dronekit.Vehicle.last_heartbeat>` 
  and could attempt to reconnect if the value gets too high.
* Apps could monitor :py:func:`Vehicle.system_status <dronekit.Vehicle.system_status>` 
  for ``CRITICAL`` or ``EMERGENCY`` in order to implement specific emergency handling.


Sleep the script when not needed
================================

Sleeping your script can reduce the CPU overhead.

For example, at low speeds you might only need to check whether you've reached a target every few seconds.
Using ``time.sleep(2)`` between checks will be more efficient than checking more often.


Exiting a script
================

Scripts should call :py:func:`Vehicle.close() <dronekit.Vehicle.close>` 
before exiting to ensure that all messages have flushed before the script completes:

.. code:: python

    # About to exit script
    vehicle.close()
    

Subclass Vehicle
=====================================

If you need to use functionality that is specific to particular hardware, we
recommend you subclass :py:class:`Vehicle <dronekit.Vehicle>` and pass this new class into 
:py:func:`connect() <dronekit.connect>`.

:doc:`../examples/create_attribute` shows how you can do this.



    
Debugging
=========

DroneKit-Python apps are ordinary standalone Python scripts, and can be :doc:`debugged using standard Python methods <../guide/debugging>` (including the debugger/IDE of your choice). 

    
Launching scripts
=================

Scripts are run from an ordinary Python command prompt. For example:

.. code:: bash

    python some_python_script.py [arguments]

Command line arguments are passed into the script as ``sys.argv`` variables (the normal)
and you can use these directly or via an argument parser (e.g. 
`argparse <https://docs.python.org/3/library/argparse.html>`_).


Current script directory
========================

You can use normal Python methods for getting file system information:

.. code-block:: python

    import os.path
    full_directory_path_of_current_script = os.path.dirname(os.path.abspath(__file__))

