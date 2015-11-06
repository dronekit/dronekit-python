.. _example_create_attribute:

================================
Example: Create Attribute in App
================================

This example shows how you can create attributes for MAVLink messages within your DroneKit-Python script and 
use them in *in the same way* as the built-in :py:class:`Vehicle <dronekit.lib.Vehicle>` attributes.

It uses the :py:func:`Vehicle.message_listener() <dronekit.lib.Vehicle.message_listener>` decorator
to set a function that is called to process a specific message, copy its values into an attribute, and notify
observers. An observer is then set on the new attribute using 
:py:func:`Vehicle.on_attribute() <dronekit.lib.Vehicle.on_attribute>`.

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

The example first defines a class for the attribute. This has members for each of the values in the message
(in this case `RAW_IMU <http://mavlink.org/messages/common#RAW_IMU>`_). It provides an initialiser and a string 
representation for printing the object.

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

        def __init__(self, time_boot_us, xacc, yacc, zacc, xygro, ygyro, zgyro, xmag, ymag, zmag):
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

The script should then create an instance of the class and add it as an attribute to the vehicle object retrieved from the connection.
All values in the new attribute should be set to ``None`` so that it is obvious to users when no messages have been received. 

.. code:: python

    # Connect to the Vehicle passed in as args.connect
    vehicle = connect(args.connect, wait_ready=True)

    #Create an Vehicle.raw_imu object and set all values to None.
    vehicle.raw_imu=RawIMU(None,None,None,None,None,None,None,None,None,None)
    
We create a listener using the :py:func:`Vehicle.message_listener() <dronekit.lib.Vehicle.message_listener>` 
decorator as shown below. The listener is called for messages that contain the string "RAW_IMU", 
with arguments for the vehicle, message name, and the message. It copies the message information into 
the attribute and then notifies all observers.

.. code:: python

    #Create a message listener using the decorator.   
    @vehicle.message_listener('RAW_IMU')
    def listener(self, name, message):
        #Copy the message contents into the raw_imu attribute
        self.raw_imu.time_boot_us=message.time_usec
        self.raw_imu.xacc=message.xacc
        self.raw_imu.yacc=message.yacc
        self.raw_imu.zacc=message.zacc
        self.raw_imu.xgyro=message.xgyro
        self.raw_imu.ygyro=message.ygyro
        self.raw_imu.zgyro=message.zgyro
        self.raw_imu.xmag=message.xmag
        self.raw_imu.ymag=message.ymag
        self.raw_imu.zmag=message.zmag
        
        # Notify all observers of new message.
        self._notify_attribute_listeners('raw_imu') 


.. note:: 

    The decorator pattern means that you can have multiple listeners for a particular message or for different
    messages and they can all have the same function name/prototype (in this case ``listener(self, name, message``).

        
From this point the ``Vehicle.raw_imu`` attribute can be treated the same as any other (inbuilt) attribute.
You can query the attribute to get any of its members, and even add an observer as shown:


.. code:: python

    #Callback to print the raw_imu
    def raw_imu_callback(self, attr_name):
        print self.raw_imu


    #Add observer for the vehicle's current location
    vehicle.on_attribute('raw_imu', raw_imu_callback)


Known issues
============

This code has no known issues.


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/create_attribute/create_attribute.py>`_):

.. literalinclude:: ../../examples/create_attribute/create_attribute.py
   :language: python

