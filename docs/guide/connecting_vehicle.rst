.. _connecting_vehicle:
.. _get_started_connecting:

=======================
Connecting to a Vehicle
=======================

The connection to the vehicle (or multiple vehicles) is set up within the 
DroneKit script. Scripts import and call the :py:func:`connect() <dronekit.connect>` 
method. After connecting this returns a :py:class:`Vehicle <dronekit.Vehicle>` 
object from which you can get/set parameters and attributes, and control vehicle movement. 

The most common way to call :py:func:`connect() <dronekit.connect>` is shown below:

.. code-block:: python

    from dronekit import connect

    # Connect to the Vehicle (in this case a UDP endpoint)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

The first parameter specifies the target address (in this case the loopback 
address for UDP port 14550). See :ref:`get_started_connect_string` for the strings to use for
other common vehicles.

The second parameter (``wait_ready``) is used to determine whether ``connect()`` returns immediately
on connection or if it waits until *some* vehicle parameters and attributes are populated. In most cases you
should use ``wait_ready=True`` to wait on the default set of parameters.

Connecting over a serial device will look something like this:

.. code-block:: python

    from dronekit import connect

    # Connect to the Vehicle (in this case a serial endpoint)
    vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)

.. tip::

  If the baud rate is not set correctly, ``connect`` may fail with a
  timeout error.  It is best to set the baud rate explicitly.

:py:func:`connect() <dronekit.connect>` also has arguments for setting the baud rate, 
the length of the connection timeout, and/or to use 
a :ref:`custom vehicle class <example_create_attribute>`. 

There is more documentation on all of the parameters in the :py:func:`API Reference <dronekit.connect>`.


.. _connection_string_options:
.. _get_started_connect_string:

Connection string options
=========================

The table below shows *connection strings* you can use for some of the more common connection types:

.. list-table::
   :widths: 10 10
   :header-rows: 1

   * - Connection type
     - Connection string
   * - Linux computer connected to the vehicle via USB
     - ``/dev/ttyUSB0``
   * - Linux computer connected to the vehicle via Serial port (RaspberryPi example)
     - ``/dev/ttyAMA0`` (also set ``baud=57600``)
   * - SITL connected to the vehicle via UDP
     - ``127.0.0.1:14550``
   * - SITL connected to the vehicle via TCP
     - ``tcp:127.0.0.1:5760``
   * - OSX computer connected to the vehicle via USB
     - ``dev/cu.usbmodem1``
   * - Windows computer connected to the vehicle via USB (in this case on COM14)
     - ``com14``
   * - Windows computer connected to the vehicle using a 3DR Telemetry Radio on COM14
     - ``com14`` (also set ``baud=57600``)

.. tip::

    The strings above are the same as are used when connecting the MAVProxy GCS. For other options see the 
    `MAVProxy documentation <http://ardupilot.github.io/MAVProxy/html/getting_started/starting.html>`_.
    
.. note::

    The default baud rate may not be appropriate for all connection types (this may be the cause
    if you can connect via a GCS but not DroneKit).

    
Connecting to multiple vehicles
===============================
  
You can control multiple vehicles from within a single script by calling
:py:func:`connect() <dronekit.connect>` for each vehicle 
with the appropriate :ref:`connection strings <connection_string_options>`.

The returned :py:class:`Vehicle <dronekit.Vehicle>` objects are independent of
each other and can be separately used to control their respective
vehicle.

