.. _connecting_vehicle:
.. _get_started_connecting:

=======================
Connecting to a Vehicle
=======================

The connection to the vehicle (or multiple vehicles) is set up within the 
DroneKit script. Scripts import and call the :py:func:`connect() <dronekit.connect>` 
method. After connecting this returns a :py:class:`Vehicle <dronekit.Vehicle>` 
object from which you can get/set parameters and attributes, and control vehicle movement:

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle (in this case a UDP endpoint)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

The first parameter above specifies the target address (in this case the loopback 
address for UDP port 14550). See :ref:`get_started_connect_string` for the strings to use for
other common vehicles. 

:py:func:`connect() <dronekit.connect>` also has arguments for setting the baud rate, whether ``connect()`` returns immediately or waits until vehicle parameters and attributes are populated (:py:func:`wait_ready=True <dronekit.Vehicle.wait_ready>`),
the length of the connection timeout, and/or to use a :ref:`custom vehicle class <example_create_attribute>`. 


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
   * - OSX computer connected to the vehicle via USB
     - ``dev/cu.usbmodem1``
   * - Windows computer connected to the vehicle via USB (in this case on COM14)
     - ``com14``
   * - Windows computer connected to the vehicle using a 3DR Telemetry Radio on COM14
     - ``com14`` (also set ``baud=57600``)

.. tip::

    The strings above are the same as are used when connecting the MAVProxy GCS. For other options see the 
    `MAVProxy documentation <http://dronecode.github.io/MAVProxy/html/getting_started/starting.html#master>`_.
    
.. note::

    The default baud rate may not be appropriate for all connection types (this may be the cause
    if you can connect via a GCS but not DroneKit).

