.. _example_create_attribute:

================================
Example: Create Attribute in App
================================

This example shows how you can subclass :py:class:`Vehicle <dronekit.lib.Vehicle>` in order to support 
new attributes for MAVLink messages within your DroneKit-Python script. The new class is defined in a 
separate file (making re-use easy) and is very similar to the code used to implement the in-built attributes. 
The new attributes are used *in the same way* as the built-in 
:py:class:`Vehicle <dronekit.lib.Vehicle>` attributes.

The new class uses the :py:func:`Vehicle.on_message() <dronekit.lib.Vehicle.on_message>` decorator
to set a function that is called to process a specific message, copy its values into an attribute, and notify
observers. An observer is then set on the new attribute using 
:py:func:`Vehicle.add_attribute_listener() <dronekit.lib.Vehicle.add_attribute_listener>`.

Additional information is provided in the guide topic :ref:`mavlink_messages`.

.. tip::
    
    This approach is useful when you urgently need to access messages that are not yet supported as 
    :py:class:`Vehicle <dronekit.lib.Vehicle>` attributes.

    Please :ref:`contribute your code to the API <contributing_api>` so that it is available to 
    (and can be tested by) the whole DroneKit-Python community. 



Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python\examples\create_attribute\


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python create_attribute.py --connect 127.0.0.1:14550

   .. note::
   
       The ``--connect`` parameter above connects to SITL on udp port 127.0.0.1:14550.
       This is the default value for the parameter, and may be omitted. 
          


On the command prompt you should see (something like):

.. code:: bash

    Connecting to vehicle on: tcp:127.0.0.1:14550
    >>> APM:Copter V3.3 (d6053245)
    >>> Frame: QUAD
    Display RAW_IMU messages for 5 seconds and then exit.
    RAW_IMU: time_boot_us=1593318928,xacc=-3,yacc=5,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1593558928,xacc=-4,yacc=5,zacc=-1000,xgyro=0,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1593798928,xacc=-2,yacc=6,zacc=-1000,xgyro=1,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1594038928,xacc=-2,yacc=6,zacc=-1000,xgyro=1,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1594278928,xacc=-2,yacc=5,zacc=-999,xgyro=0,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1594518928,xacc=-2,yacc=4,zacc=-998,xgyro=1,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1594758928,xacc=-3,yacc=5,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1594998928,xacc=-2,yacc=4,zacc=-999,xgyro=1,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1595238928,xacc=-3,yacc=5,zacc=-1000,xgyro=0,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1595478928,xacc=-2,yacc=4,zacc=-1000,xgyro=1,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1595718928,xacc=-2,yacc=4,zacc=-999,xgyro=0,ygyro=1,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1595958928,xacc=-3,yacc=6,zacc=-1000,xgyro=0,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1596198928,xacc=-4,yacc=6,zacc=-1000,xgyro=1,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1596438928,xacc=-2,yacc=6,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1596678928,xacc=-3,yacc=4,zacc=-999,xgyro=1,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1596918928,xacc=-2,yacc=4,zacc=-999,xgyro=0,ygyro=1,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1597158928,xacc=-2,yacc=6,zacc=-1000,xgyro=0,ygyro=1,zgyro=1,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1597398928,xacc=-2,yacc=5,zacc=-1000,xgyro=0,ygyro=1,zgyro=0,xmag=156,ymag=41,zmag=-365
    RAW_IMU: time_boot_us=1597638928,xacc=-3,yacc=5,zacc=-1000,xgyro=1,ygyro=0,zgyro=0,xmag=156,ymag=41,zmag=-365
    Close vehicle object



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

We create a listener using the :py:func:`Vehicle.on_message() <dronekit.lib.Vehicle.on_message>` 
decorator. The listener is called for messages that contain the string "RAW_IMU", 
with arguments for the vehicle, message name, and the message. It copies the message information into 
the attribute and then notifies all observers.


.. code-block:: python
    :emphasize-lines: 6, 9-10, 30
                
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
                self.notify_attribute_listeners('raw_imu', self._raw_imu) 

        @property
        def raw_imu(self):
            return self._raw_imu            
            
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