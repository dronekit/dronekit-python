.. _example_create_attribute:

================================
Example: Create Attribute in App
================================

This example shows how you can subclass :py:class:`Vehicle <dronekit.Vehicle>` in order to support 
new attributes for MAVLink messages within your DroneKit-Python script. The new class is defined in a 
separate file (making re-use easy) and is very similar to the code used to implement the in-built attributes. 
The new attributes are used *in the same way* as the built-in 
:py:class:`Vehicle <dronekit.Vehicle>` attributes.

The new class uses the :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` decorator
to set a function that is called to process a specific message, copy its values into an attribute, and notify
observers. An observer is then set on the new attribute using 
:py:func:`Vehicle.add_attribute_listener() <dronekit.Vehicle.add_attribute_listener>`.

Additional information is provided in the guide topic :ref:`mavlink_messages`.

.. tip::
    
    This approach is useful when you urgently need to access messages that are not yet supported as 
    :py:class:`Vehicle <dronekit.Vehicle>` attributes.

    Please :ref:`contribute your code to the API <contributing_api>` so that it is available to 
    (and can be tested by) the whole DroneKit-Python community. 



Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python\examples\create_attribute\

#. You can run the example against a simulator (DroneKit-SITL) by specifying the Python script without any arguments.
   The example will download SITL binaries (if needed), start the simulator, and then connect to it:

   .. code-block:: bash

       python create_attribute.py

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
       Display RAW_IMU messages for 5 seconds and then exit.
       RAW_IMU: time_boot_us=15340000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=15580000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=15820000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=1,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=16060000,xacc=0,yacc=1,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=16300000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=16540000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=16780000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=17020000,xacc=1,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=17260000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=17500000,xacc=0,yacc=0,zacc=-1000,xgyro=1,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=17740000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=17980000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=18220000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=1,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=18460000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=18700000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=18940000,xacc=1,yacc=0,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=19180000,xacc=1,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=19420000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=161,ymag=19,zmag=-365
       RAW_IMU: time_boot_us=19660000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=154,ymag=52,zmag=-365
       RAW_IMU: time_boot_us=19900000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=154,ymag=52,zmag=-365
       RAW_IMU: time_boot_us=20140000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=154,ymag=52,zmag=-365
       Close vehicle object
       
       
#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python create_attribute.py --connect 127.0.0.1:14550




How does it work?
=================

Subclassing Vehicle
-------------------

The example file **my_vehicle.py** defines a class for the new attribute (``RawIMU``) and a new vehicle subclass (``MyVehicle``).

.. note::

    The example uses the same documentation markup used by the native code, which can be generated into a document set using
    Sphinx/autodoc.


``RawIMU`` has members for each of the values in the message
(in this case `RAW_IMU <http://mavlink.org/messages/common#RAW_IMU>`_). It provides an initialiser that sets all the values to
``None`` and a string representation for printing the object.

.. code:: python

    class RawIMU(object):
        """
        The RAW IMU readings for the usual 9DOF sensor setup. 
        This contains the true raw values without any scaling to allow data capture and system debugging.
    
        The message definition is here: http://mavlink.org/messages/common#RAW_IMU
    
        :param time_boot_us: Timestamp (microseconds since system boot). #Note, not milliseconds as per spec
        :param xacc: X acceleration (mg)
        :param yacc: Y acceleration (mg)
        :param zacc: Z acceleration (mg)
        :param xgyro: Angular speed around X axis (millirad /sec)
        :param ygyro: Angular speed around Y axis (millirad /sec)
        :param zgyro: Angular speed around Z axis (millirad /sec)
        :param xmag: X Magnetic field (milli tesla)
        :param ymag: Y Magnetic field (milli tesla)
        :param zmag: Z Magnetic field (milli tesla)    
        """

        def __init__(self, time_boot_us=None, xacc=None, yacc=None, zacc=None, xygro=None, ygyro=None, zgyro=None, xmag=None, ymag=None, zmag=None):
            """
            RawIMU object constructor.
            """
            self.time_boot_us = time_boot_us
            self.xacc = xacc
            self.yacc = yacc
            self.zacc = zacc
            self.xgyro = zgyro
            self.ygyro = ygyro
            self.zgyro = zgyro
            self.xmag = xmag        
            self.ymag = ymag
            self.zmag = zmag      
        
        def __str__(self):
            """
            String representation of the RawIMU object
            """
            return "RAW_IMU: time_boot_us={},xacc={},yacc={},zacc={},xgyro={},ygyro={},zgyro={},xmag={},ymag={},zmag={}".format(self.time_boot_us, self.xacc, self.yacc,self.zacc,self.xgyro,self.ygyro,self.zgyro,self.xmag,self.ymag,self.zmag)


``MyVehicle`` is a superclass of ``Vehicle`` (and hence inherits all its attributes). 
This first creates a private instance of ``RawIMU``.

We create a listener using the :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` 
decorator. The listener is called for messages that contain the string "RAW_IMU", 
with arguments for the vehicle, message name, and the message. It copies the message information into 
the attribute and then notifies all observers.

.. code-block:: python
    :emphasize-lines: 6, 9-10, 32
                
    class MyVehicle(Vehicle):
        def __init__(self, *args):
            super(MyVehicle, self).__init__(*args)

            # Create an Vehicle.raw_imu object with initial values set to None.
            self._raw_imu = RawIMU()

            # Create a message listener using the decorator.   
            @self.on_message('RAW_IMU')
            def listener(self, name, message):
                """
                The listener is called for messages that contain the string specified in the decorator,
                passing the vehicle, message name, and the message.
                
                The listener writes the message to the (newly attached) ``vehicle.raw_imu`` object 
                and notifies observers.
                """
                self._raw_imu.time_boot_us=message.time_usec
                self._raw_imu.xacc=message.xacc
                self._raw_imu.yacc=message.yacc
                self._raw_imu.zacc=message.zacc
                self._raw_imu.xgyro=message.xgyro
                self._raw_imu.ygyro=message.ygyro
                self._raw_imu.zgyro=message.zgyro
                self._raw_imu.xmag=message.xmag
                self._raw_imu.ymag=message.ymag
                self._raw_imu.zmag=message.zmag
                
                # Notify all observers of new message (with new value)
                #   Note that argument `cache=False` by default so listeners
                #   are updaed with every new message
                self.notify_attribute_listeners('raw_imu', self._raw_imu) 

        @property
        def raw_imu(self):
            return self._raw_imu            


.. note::

    The notifier function (:py:func:`Vehicle.notify_attribute_listeners() <dronekit.Vehicle.notify_attribute_listeners>`)
    should be called every time there is an update from the vehicle. 
    
    You can set a third parameter (``cache=True``) so that it only invokes the listeners when the value *changes*. 
    This is normally used for attributes like the vehicle mode, where the information is updated 
    regularly from the vehicle, but client code is only interested when the attribute changes.
    
    You should not set ``cache=True`` for attributes that represent sensor information or other "live" information, including
    the RAW_IMU attribute demonstrated here. Clients can then implement their own caching strategy if needed.


At the end of the class we create the public properly ``raw_imu`` which client code may read and observe.

.. note:: 

    The decorator pattern means that you can have multiple listeners for a particular message or for different
    messages and they can all have the same function name/prototype (in this case ``listener(self, name, message``).


Using the Vehicle subclass
--------------------------

The **create_attribute.py** file first imports the ``MyVehicle`` class. 


.. code-block:: python
    :emphasize-lines: 2

    from dronekit import connect, Vehicle
    from my_vehicle import MyVehicle #Our custom vehicle class
    import time


We then call ``connect()``, specifying this new class in the ``vehicle_class`` argument.    
    
.. code-block:: python

    # Connect to our custom vehicle_class `MyVehicle` at address `args.connect`
    vehicle = connect(args.connect, wait_ready=True, vehicle_class=MyVehicle)  
    
``connect()`` returns a ``MyVehicle`` class which can be used in *exactly the same way* as ``Vehicle`` but with an 
additional attribute ``raw_imu``. You can query the attribute to get any of its members, and even add an observer as shown:

.. code:: python

    # Add observer for the custom attribute

    def raw_imu_callback(self, attr_name, value):
        # attr_name == 'raw_imu'
        # value == vehicle.raw_imu
        print value

    vehicle.add_attribute_listener('raw_imu', raw_imu_callback)



Known issues
============

This code has no known issues.


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/create_attribute/create_attribute.py>`_):

.. literalinclude:: ../../examples/create_attribute/create_attribute.py
   :language: python

.. literalinclude:: ../../examples/create_attribute/my_vehicle.py
   :language: python