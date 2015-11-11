.. _migrating_dkpy2_0:

=====================
Migrating to DKPY 2.0
=====================

DroneKit-Python 2.0 has undergone a significant *architectural* evolution when compared to version 1.x (the library changed from a MAVProxy extension
to a standalone Python module). The API itself remains largely compatible, with the most important difference being that you
now need to specify the vehicle target address inside the script.

The sections below outline the main migration areas.


Installation
============

DKPY 2.0 is now installed from `pip` on all platforms - see :ref:`get-started` for more information.

Installation is generally simpler than on DK 1.x because there are far fewer dependencies (both MAVProxy and numpy 
are no longer needed).

.. note::

    * The DroneKit-Python Windows installer cannot be used for DKPY2.x (and is no longer needed).
    * One implication of the reduced dependencies is that it should now be easier to use other Python distributions 
      (like ActivePython - although this has not been verified!)


Launching scripts
=================

DroneKit-Python 2.0 apps are run from an ordinary Python command prompt. For example:

.. code:: bash

    some_python_script.py    # or `python some_python_script.py`

.. note::

    This contrasts with DKPY 1.x scripts, which were run from within MAVProxy using the command:
    
    .. code:: bash
    
        api start some_python_script.py
    

Code changes
============

This section outlines the changes you will need to make to your DroneKit-Python scripts.

Connecting to a vehicle
-----------------------

You must specify the target vehicle address in your script (in DKPY 1.x this was done when you launched MAVProxy).

The code fragment below shows how you import the :py:func:`connect() <dronekit.lib.connect>` method and use it to return a 
connected :py:class:`Vehicle <dronekit.lib.Vehicle>` object. The address string passed to ``connect()`` takes the same 
values as were passed to *MAVProxy* when setting up a connection in DKPY 1.x (in this case, a SITL instance running on the same computer). 

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle (in this case a UDP endpoint)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)


The ``wait_ready=True`` parameter ensures that ``connect()`` won't return until 
:py:attr:`Vehicle.parameters <dronekit.lib.Vehicle.parameters>` has been populated. 
This also allows *MAVLink* messages to arrive from the connected vehicle 
and populate other ``Vehicle`` attributes. 

The vehicle can then be used in exactly the same way as in DKPY 1.x. 

.. note::

    The above code replaces DKPY 1.x code to get the Vehicle (similar to the example below):
 
    .. code:: python

        # Get an instance of the API endpoint
        api = local_connect()
        # Get the connected vehicle (currently only one vehicle can be returned).
        vehicle = api.get_vehicles()[0] 
  

   
.. todo:: Above link to the connect method in API ref - make sure connect() is documented.


Connection status checks
------------------------

DroneKit no longer runs in *MAVProxy* so scripts don't need to monitor and act on external thread shutdown commands.

Remove code that checks the ``api.exit`` status (note that the ``api.exit`` call below is commented out). 

.. code:: python

    while not vehicle.armed   # and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)

.. note::

    In fact you should delete all references to ``APIConnection`` class and its methods (``get_vehicles()``, ``exit()`` and ``stop()``). 


.. todo:: Find out how to check the connection status is still valid. That would go in separate section.


Script completion checks
------------------------

Examples that might possibly have outstanding messages should call :py:func:`Vehicle.close() <dronekit.lib.Vehicle.close>` 
before exiting to ensure that all messages have flushed before the script completes:

.. code:: python

    # About to exit script
    vehicle.close()

    
Command line arguments
----------------------

Remove any code that uses the ``local_arguments`` array to get script-local command line arguments (via MAVProxy).

From DKPY 2.0 command line arguments are passed to ``sys.argv`` as with any other script. The examples use the 
`argparse <https://docs.python.org/3/library/argparse.html>`_ module for argument parsing, but you can
use whatever method you like.

.. note::

    In DKPY 1.x the script's ``sys.argv`` values were the values passed to MAVProxy when it was
    started. To access arguments passed to the script from *MAVProxy* you used the ``local_arguments`` array. 
    For example if you started a script as shown below:

    .. code:: bash

        api start my_script.py 101

    Then you would read the integer in your code using

    .. code:: python

        my_argument = int(local_arguments[0])

        
.. todo:: This addition closes https://github.com/dronekit/dronekit-python/issues/13


Current script directory
------------------------

DroneKit-Python v1.x passed a global property ``load_path`` to any executed file containing the 
directory in which the script was running. This is no longer needed in version 2 and has been removed.

Instead, use normal Python methods for getting file system information:

.. code:: python

    import os.path
    full_directory_path_of_current_script = os.path.dirname(os.path.abspath(__file__))

    
.. _migrating_dkpy2_0_heading:

Home location
-------------

DroneKit-Python 1.x code retrieved the home location from the first element in :py:attr:`Vehicle.commands <dronekit.lib.Vehicle.commands>`.
This code must be replaced with the DroneKit-Python 2.x :py:attr:`Vehicle.home_location <dronekit.lib.Vehicle.home_location>` attribute.

.. tip::

    Even though the home location is no longer returned as the first waypoint in :py:attr:`Vehicle.commands <dronekit.lib.Vehicle.commands>`,
    you will still need to download the commands in order to populate the value of 
    :py:attr:`Vehicle.home_location <dronekit.lib.Vehicle.home_location>`. 



Observing attribute changes
---------------------------

The DroneKit-Python 1.x observer function ``vehicle.add_attribute_observer`` has been replaced by 
:py:func:`Vehicle.add_attribute_listener() <dronekit.lib.Vehicle.add_attribute_listener>` or 
:py:func:`Vehicle.on_attribute() <dronekit.lib.Vehicle.on_attribute>` in DKYP2.x,  and ``Vehicle.remove_attribute_observer`` 
has been repaced by :py:func:`remove_attribute_listener() <dronekit.lib.Vehicle.remove_attribute_listener>`.

The main difference is that the callback function now takes three arguments (the vehicle object, attribute name, attribute value)
rather than just the attribute name. This allows you to more easily write callbacks that support attribute-specific and 
vehicle-specific handling and means that you can get the new value from the callback attribute rather than by re-querying
the vehicle. 

The difference between :py:func:`Vehicle.add_attribute_listener() <dronekit.lib.Vehicle.add_attribute_listener>` and 
:py:func:`Vehicle.on_attribute() <dronekit.lib.Vehicle.on_attribute>` is that attribute listeners added using
:py:func:`Vehicle.on_attribute() <dronekit.lib.Vehicle.on_attribute>` cannot be removed (while ``on_attribute()`` 
has a more elegant syntax).

A few attributes have been modified so that they only notify when the value changes: 
:py:func:`Vehicle.system_status <dronekit.lib.Vehicle.system_status>`,
:py:attr:`Vehicle.armed <dronekit.lib.Vehicle.armed>`, and
:py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>`. Users no longer need to add caching code 
for these attributes in their listeners.
Attributes that provide "streams" of information (i.e. sensor output) remain unchanged. 

.. note::

    If you're :ref:`creating your own attributes <example_create_attribute>` this caching is trivially 
    provided using the ``cache=True`` argument to 
    :py:func:`Vehicle.notify_attribute_listeners() <dronekit.lib.Vehicle.notify_attribute_listeners>`.

See :ref:`vehicle_state_observe_attributes` for more information.


Intercepting MAVLink Messages
-----------------------------

DroneKit-Python 1.x used ``Vehicle.set_mavlink_callback()`` and ``Vehicle.unset_mavlink_callback``
to set/unset a callback function that was invoked for every single mavlink message.

In DKPY2 this has been replaced by the :py:func:`Vehicle.on_message() <dronekit.lib.Vehicle.on_message>` 
decorator, which allows you to specify a callback function that will be invoked for a single message 
(or all messages, by specifying the message name as the wildcard string '``*``').

.. tip::

    :py:func:`Vehicle.on_message() <dronekit.lib.Vehicle.on_message>` is used in core DroneKit code for 
    message capture and to create ``Vehicle`` attributes.

    The API also adds :py:func:`Vehicle.add_message_listener() <dronekit.lib.Vehicle.add_message_listener>`
    and :py:func:`Vehicle.remove_message_listener() <dronekit.lib.Vehicle.remove_message_listener>`. 
    These can be used instead of :py:func:`Vehicle.on_message() <dronekit.lib.Vehicle.on_message>` when you need to be
    able to *remove* an added listener. Typically you won't need to!

See :ref:`mavlink_messages` for more information.


New attributes
--------------

In addition to the :ref:`home_location <migrating_dkpy2_0_heading>`, a few more attributes have been added, 
including:
:py:func:`Vehicle.system_status <dronekit.lib.Vehicle.system_status>`, 
:py:func:`Vehicle.heading <dronekit.lib.Vehicle.heading>`, 
:py:func:`Vehicle.mount_status <dronekit.lib.Vehicle.mount_status>`, 
:py:func:`Vehicle.ekf_ok <dronekit.lib.Vehicle.ekf_ok>`, 
:py:func:`Vehicle.is_armable <dronekit.lib.Vehicle.is_armable>`.


Channel Overrides
-----------------

.. warning:: 

    Channel overrides (a.k.a “RC overrides”) are highly discommended (they are primarily implemented for 
    simulating user input and when implementing certain types of joystick control).

DKPY v2 replaces the ``vehicle.channel_readback`` attribute with
:py:attr:`Vehicle.channels <dronekit.lib.Vehicle.channels>` (and the :py:class:`Channels <dronekit.lib.Channels>`
class) and the ``vehicle.channel_override`` attribute with 
:py:attr:`Vehicle.channels.overrides <dronekit.lib.Channels.overrides>` 
(and the :py:class:`ChannelsOverrides <dronekit.lib.ChannelsOverrides>` class). 

Documentation and example code for how to use the new API are provided in :ref:`example_channel_overrides`.




Debugging
=========

DroneKit-Python 1.x scripts were run in the context of a MAVProxy. This made them difficult to debug because you had to 
instrument your code in order to launch the debugger, and debug messages were interleaved with MAVProxy output.

Debugging on DroneKit-Python 2.x is much easier. Apps are now just standalone scripts, and can be debugged 
using standard Python methods (including the debugger/IDE of your choice). 
