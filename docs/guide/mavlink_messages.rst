.. _mavlink_messages:

================
MAVLink Messages
================

Some useful MAVLink messages sent by the autopilot are not (yet) directly available to DroneKit-Python scripts
through the :ref:`observable attributes <vehicle_state_observe_attributes>` in :py:class:`Vehicle <dronekit.lib.Vehicle>`.

This topic shows how you can intercept specific MAVLink messages by defining a listener callback function 
using the :py:func:`Vehicle.message_listener() <dronekit.lib.Vehicle.message_listener>` 
decorator.

.. tip::

    :ref:`example_create_attribute` shows how you can extend this approach to create a new :py:class:`Vehicle <dronekit.lib.Vehicle>`
    attribute in your client code.


.. _mavlink_messages_message_listener:
.. _mavlink_messages_set_mavlink_callback:

Creating a message listener
===========================

The :py:func:`Vehicle.message_listener() <dronekit.lib.Vehicle.message_listener>` decorator can be used to 
set a particular function as the callback handler for a particular message type. You can create listeners 
for as many messages as you like, or even multiple listeners for the same message. 

For example, code snippet below shows how to set a listener for the ``RANGEFINDER`` message:

.. code:: python

    #Create a message listener using the decorator.   
    @vehicle.message_listener('RANGEFINDER')
    def listener(self, name, message):
        print message

.. tip::

    Every single listener can have the same name/prototpye as above ("``listener``") because
    Python does not notice these decorated functions as having the same name in the same scope.
    
The messages are `classes <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_ from the 
`pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_ library. 
The output of the code above looks something like:

.. code:: bash

    RANGEFINDER {distance : 0.0899999961257, voltage : 0.00900000054389}
    ...
    
You can access the message fields directly. For example, to access the ``RANGEFINDER`` message your listener
function might look like this:

.. code:: python

    #Create a message listener using the decorator.   
    @vehicle.message_listener('RANGEFINDER')
    def listener(self, name, message):
        print 'distance: %s' % message.distance
        print 'voltage: %s' % message.voltage


        
        
Clearing the observer
=====================

The observer is unset by calling :py:func:`Vehicle.remove_message_listener <dronekit.lib.Vehicle.remove_message_listener>`.

The observer will also be removed when the thread exits.
