.. _example_create_attribute:

================================
Example: Create Attribute in App
================================

This example shows how you can create attributes for MAVLink messages within your DroneKit-Python script and 
use them in *in the same way* as the built-in :py:class:`Vehicle <dronekit.lib.Vehicle>` attributes.

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

    RAW_IMU: time_boot_us=41270000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=1,zgyro=1,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=41510000,xacc=0,yacc=0,zacc=-1000,xgyro=1,ygyro=0,zgyro=1,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=41750000,xacc=1,yacc=0,zacc=-1000,xgyro=1,ygyro=1,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=41990000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=42230000,xacc=0,yacc=0,zacc=-1000,xgyro=0,ygyro=0,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=42470000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=0,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=42710000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=42950000,xacc=0,yacc=0,zacc=-1000,xgyro=1,ygyro=1,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=43190000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=1,zgyro=1,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=43430000,xacc=0,yacc=0,zacc=-999,xgyro=0,ygyro=0,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=43670000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=0,zgyro=1,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=43910000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=0,zgyro=1,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=44150000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=1,zgyro=0,xmag=153,ymag=52,zmag=-364
    RAW_IMU: time_boot_us=44390000,xacc=0,yacc=0,zacc=-999,xgyro=1,ygyro=1,zgyro=0,xmag=153,ymag=52,zmag=-364
    APIThread-0 exiting...



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
            return "RAW_IMU: time_boot_us={},xacc={},yacc={},zacc={},xgyro={},ygyro={},zgyro={},xmag={},ymag={},zmag={}".format(self.time_boot_us, self.xacc,     self.yacc,self.zacc,self.xgyro,self.ygyro,self.zgyro,self.xmag,self.ymag,self.zmag)

The script should then create an instance of the class and add it as an attribute to the vehicle object retrieved from the connection.
All values in the new attribute should be set to ``None`` so that it is obvious to users when no messages have been received. 

.. code:: python

    # Connect to the Vehicle passed in as args.connect
    vehicle = connect(args.connect, wait_ready=True)

    #Create an Vehicle.raw_imu object and set all values to None.
    vehicle.raw_imu=RawIMU(None,None,None,None,None,None,None,None,None,None)
    
We set a callback to intercept all MAVLink messages using :py:func:`Vehicle.set_mavlink_callback() <dronekit.lib.Vehicle.set_mavlink_callback>` 
as shown below. 

.. code:: python

    def mavrx_debug_handler(message):
        """
        Handler for MAVLink messages.
        """
        #Handle raw_imu messages
        mav_raw_imu_handler(message)

    # Set MAVLink callback handler (after getting Vehicle instance)
    vehicle.set_mavlink_callback(mavrx_debug_handler)

For clarity we have separated the handling code for the RAW_IMU message into ``mav_raw_imu_handler()``.  The handler simply checks the message type and 
(for the correct messages) writes the values into the attribute. It then calls ``vehicle.notify_observers('raw_imu')`` to notify all observers of this attribute type.
    
.. code:: python

    def mav_raw_imu_handler(message):
        """
        Writes received message to the (newly attached) vehicle.raw_imu object and notifies observers.
        """
        messagetype=str(message).split('{')[0].strip()
        if messagetype=='RAW_IMU':
            vehicle.raw_imu.time_boot_us=message.time_usec
            vehicle.raw_imu.xacc=message.xacc
            vehicle.raw_imu.yacc=message.yacc
            vehicle.raw_imu.zacc=message.zacc
            vehicle.raw_imu.xgyro=message.xgyro
            vehicle.raw_imu.ygyro=message.ygyro
            vehicle.raw_imu.zgyro=message.zgyro
            vehicle.raw_imu.xmag=message.xmag
            vehicle.raw_imu.ymag=message.ymag
            vehicle.raw_imu.zmag=message.zmag

           #Add Notify all observers of new message.
            vehicle.notify_observers('raw_imu') 

        
At this point the ``Vehicle.raw_imu`` attribute can be treated the same as any other attribute for the duration of the session.
You can query the attribute to get any of the values, and even add an observer as shown:


.. code:: python

    #Callback to print the raw_imu
    def raw_imu_callback(rawimu):
        print vehicle.raw_imu


    #Add observer for the vehicle's current location
    vehicle.add_attribute_observer('raw_imu', raw_imu_callback)


.. note::

    It is not possible to reliably use this approach to create independent modules because only one 
    MAVLink callback can be set at a time in the running program (``set_mavlink_callback()``) 


Known issues
============

This code has no known issues.


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/create_attribute/create_attribute.py>`_):

.. literalinclude:: ../../examples/create_attribute/create_attribute.py
   :language: python

